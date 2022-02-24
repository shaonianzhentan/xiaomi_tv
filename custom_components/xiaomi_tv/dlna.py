from async_upnp_client import UpnpFactory, UpnpError
from async_upnp_client.aiohttp import AiohttpRequester
from async_upnp_client.profiles.dlna import DmrDevice, TransportState

from homeassistant.components.media_player import const as _mp_const
from homeassistant.const import (
    STATE_OFF, 
    STATE_ON, 
    STATE_PLAYING, 
    STATE_PAUSED, 
    STATE_IDLE, 
    STATE_UNAVAILABLE
)

from .utils import check_port

# Map UPnP class to media_player media_content_type
MEDIA_TYPE_MAP: Mapping[str, str] = {
    "object": _mp_const.MEDIA_TYPE_URL,
    "object.item": _mp_const.MEDIA_TYPE_URL,
    "object.item.imageItem": _mp_const.MEDIA_TYPE_IMAGE,
    "object.item.imageItem.photo": _mp_const.MEDIA_TYPE_IMAGE,
    "object.item.audioItem": _mp_const.MEDIA_TYPE_MUSIC,
    "object.item.audioItem.musicTrack": _mp_const.MEDIA_TYPE_MUSIC,
    "object.item.audioItem.audioBroadcast": _mp_const.MEDIA_TYPE_MUSIC,
    "object.item.audioItem.audioBook": _mp_const.MEDIA_TYPE_PODCAST,
    "object.item.videoItem": _mp_const.MEDIA_TYPE_VIDEO,
    "object.item.videoItem.movie": _mp_const.MEDIA_TYPE_MOVIE,
    "object.item.videoItem.videoBroadcast": _mp_const.MEDIA_TYPE_TVSHOW,
    "object.item.videoItem.musicVideoClip": _mp_const.MEDIA_TYPE_VIDEO,
    "object.item.playlistItem": _mp_const.MEDIA_TYPE_PLAYLIST,
    "object.item.textItem": _mp_const.MEDIA_TYPE_URL,
    "object.item.bookmarkItem": _mp_const.MEDIA_TYPE_URL,
    "object.item.epgItem": _mp_const.MEDIA_TYPE_EPISODE,
    "object.item.epgItem.audioProgram": _mp_const.MEDIA_TYPE_EPISODE,
    "object.item.epgItem.videoProgram": _mp_const.MEDIA_TYPE_EPISODE,
    "object.container": _mp_const.MEDIA_TYPE_PLAYLIST,
    "object.container.person": _mp_const.MEDIA_TYPE_ARTIST,
    "object.container.person.musicArtist": _mp_const.MEDIA_TYPE_ARTIST,
    "object.container.playlistContainer": _mp_const.MEDIA_TYPE_PLAYLIST,
    "object.container.album": _mp_const.MEDIA_TYPE_ALBUM,
    "object.container.album.musicAlbum": _mp_const.MEDIA_TYPE_ALBUM,
    "object.container.album.photoAlbum": _mp_const.MEDIA_TYPE_ALBUM,
    "object.container.genre": _mp_const.MEDIA_TYPE_GENRE,
    "object.container.genre.musicGenre": _mp_const.MEDIA_TYPE_GENRE,
    "object.container.genre.movieGenre": _mp_const.MEDIA_TYPE_GENRE,
    "object.container.channelGroup": _mp_const.MEDIA_TYPE_CHANNELS,
    "object.container.channelGroup.audioChannelGroup": _mp_const.MEDIA_TYPE_CHANNELS,
    "object.container.channelGroup.videoChannelGroup": _mp_const.MEDIA_TYPE_CHANNELS,
    "object.container.epgContainer": _mp_const.MEDIA_TYPE_TVSHOW,
    "object.container.storageSystem": _mp_const.MEDIA_TYPE_PLAYLIST,
    "object.container.storageVolume": _mp_const.MEDIA_TYPE_PLAYLIST,
    "object.container.storageFolder": _mp_const.MEDIA_TYPE_PLAYLIST,
    "object.container.bookmarkFolder": _mp_const.MEDIA_TYPE_PLAYLIST,
}

# Map media_player media_content_type to UPnP class. Not everything will map
# directly, in which case it's not specified and other defaults will be used.
MEDIA_UPNP_CLASS_MAP: Mapping[str, str] = {
    _mp_const.MEDIA_TYPE_ALBUM: "object.container.album.musicAlbum",
    _mp_const.MEDIA_TYPE_ARTIST: "object.container.person.musicArtist",
    _mp_const.MEDIA_TYPE_CHANNEL: "object.item.videoItem.videoBroadcast",
    _mp_const.MEDIA_TYPE_CHANNELS: "object.container.channelGroup",
    _mp_const.MEDIA_TYPE_COMPOSER: "object.container.person.musicArtist",
    _mp_const.MEDIA_TYPE_CONTRIBUTING_ARTIST: "object.container.person.musicArtist",
    _mp_const.MEDIA_TYPE_EPISODE: "object.item.epgItem.videoProgram",
    _mp_const.MEDIA_TYPE_GENRE: "object.container.genre",
    _mp_const.MEDIA_TYPE_IMAGE: "object.item.imageItem",
    _mp_const.MEDIA_TYPE_MOVIE: "object.item.videoItem.movie",
    _mp_const.MEDIA_TYPE_MUSIC: "object.item.audioItem.musicTrack",
    _mp_const.MEDIA_TYPE_PLAYLIST: "object.item.playlistItem",
    _mp_const.MEDIA_TYPE_PODCAST: "object.item.audioItem.audioBook",
    _mp_const.MEDIA_TYPE_SEASON: "object.item.epgItem.videoProgram",
    _mp_const.MEDIA_TYPE_TRACK: "object.item.audioItem.musicTrack",
    _mp_const.MEDIA_TYPE_TVSHOW: "object.item.videoItem.videoBroadcast",
    _mp_const.MEDIA_TYPE_URL: "object.item.bookmarkItem",
    _mp_const.MEDIA_TYPE_VIDEO: "object.item.videoItem",
}

# Translation of MediaMetadata keys to DIDL-Lite keys.
# See https://developers.google.com/cast/docs/reference/messages#MediaData via
# https://www.home-assistant.io/integrations/media_player/ for HA keys.
# See http://www.upnp.org/specs/av/UPnP-av-ContentDirectory-v4-Service.pdf for
# DIDL-Lite keys.
MEDIA_METADATA_DIDL: Mapping[str, str] = {
    "subtitle": "longDescription",
    "releaseDate": "date",
    "studio": "publisher",
    "season": "episodeSeason",
    "episode": "episodeNumber",
    "albumName": "album",
    "trackNumber": "originalTrackNumber",
}

class MediaDLNA():

    def __init__(self, ip):
        self.ip = ip
        self.dlna = None

    @property
    def state(self):
        if self.dlna is not None:
            if self.dlna.transport_state in (TransportState.PLAYING, TransportState.TRANSITIONING):
                return STATE_PLAYING
            elif self.dlna.transport_state in (TransportState.PAUSED_PLAYBACK, TransportState.PAUSED_RECORDING):
                return STATE_PAUSED
        return STATE_UNAVAILABLE

    @property
    def media_duration(self):
        return None if not self.dlna else self.dlna.media_duration

    @property
    def media_position(self):
        return None if not self.dlna else self.dlna.media_position

    async def async_media_play(self):
        if self.state == STATE_PAUSED:
            await self.dlna.async_play()
            return True
        return False

    async def async_media_pause(self):
        if self.state == STATE_PLAYING:
            await self.dlna.async_pause()
            return True
        return False

    async def async_set_volume_level(self, volume):
        if self.state != STATE_UNAVAILABLE:
            await self.dlna.async_set_volume_level(volume)

    async def async_turn_off(self):
        print('断开链接')
        self.dlna = None

    async def async_update(self):
        if check_port(self.ip, 49152) == False:
            return
        try:
            requester = AiohttpRequester()
            factory = UpnpFactory(requester)
            url = f"http://{self.ip}:49152/description.xml"
            # print(url)
            device = await factory.async_create_device(url)

            def event_handler(**args):
                print(args)

            self.dlna = DmrDevice(device, event_handler)
        except Exception as ex:
            print(ex)
        # 订阅事件通知
        # self.dlna_device.on_event = self._on_event
        # await self.dlna_device.async_subscribe_services(auto_resubscribe=True)
    
    ''' 有时间再研究
    def _on_event(self, service, state_variables):
        if not state_variables:
            # Indicates a failure to resubscribe, check if device is still available
            self.check_available = True
        print(service, state_variables)
    '''

    async def async_play_media(self, media_type, media_id, **kwargs):

        if self.dlna is None:
            return
        title = "小米电视 - HomeAssistant"
        didl_metadata: str | None = None
        metadata = {}
        # Translate metadata keys from HA names to DIDL-Lite names
        for hass_key, didl_key in MEDIA_METADATA_DIDL.items():
            if hass_key in metadata:
                metadata[didl_key] = metadata.pop(hass_key)

        if not didl_metadata:
            # Create metadata specific to the given media type; different fields are
            # available depending on what the upnp_class is.
            upnp_class = MEDIA_UPNP_CLASS_MAP.get(media_type)
            didl_metadata = await self.dlna.construct_play_media_metadata(
                media_url=media_id,
                media_title=title,
                override_upnp_class=upnp_class,
                meta_data=metadata,
            )

        if self.dlna.can_stop:
            await self.dlna.async_stop()

        await self.dlna.async_set_transport_uri(media_id, title, didl_metadata)