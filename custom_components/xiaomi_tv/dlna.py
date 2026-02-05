from collections.abc import Mapping

from async_upnp_client.client_factory import UpnpFactory, UpnpError
from async_upnp_client.aiohttp import AiohttpRequester
from async_upnp_client.profiles.dlna import DmrDevice, TransportState

from homeassistant.components.media_player import MediaType
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
    "object": MediaType.URL,
    "object.item": MediaType.URL,
    "object.item.imageItem": MediaType.IMAGE,
    "object.item.imageItem.photo": MediaType.IMAGE,
    "object.item.audioItem": MediaType.MUSIC,
    "object.item.audioItem.musicTrack": MediaType.MUSIC,
    "object.item.audioItem.audioBroadcast": MediaType.MUSIC,
    "object.item.audioItem.audioBook": MediaType.PODCAST,
    "object.item.videoItem": MediaType.VIDEO,
    "object.item.videoItem.movie": MediaType.MOVIE,
    "object.item.videoItem.videoBroadcast": MediaType.TVSHOW,
    "object.item.videoItem.musicVideoClip": MediaType.VIDEO,
    "object.item.playlistItem": MediaType.PLAYLIST,
    "object.item.textItem": MediaType.URL,
    "object.item.bookmarkItem": MediaType.URL,
    "object.item.epgItem": MediaType.EPISODE,
    "object.item.epgItem.audioProgram": MediaType.EPISODE,
    "object.item.epgItem.videoProgram": MediaType.EPISODE,
    "object.container": MediaType.PLAYLIST,
    "object.container.person": MediaType.ARTIST,
    "object.container.person.musicArtist": MediaType.ARTIST,
    "object.container.playlistContainer": MediaType.PLAYLIST,
    "object.container.album": MediaType.ALBUM,
    "object.container.album.musicAlbum": MediaType.ALBUM,
    "object.container.album.photoAlbum": MediaType.ALBUM,
    "object.container.genre": MediaType.GENRE,
    "object.container.genre.musicGenre": MediaType.GENRE,
    "object.container.genre.movieGenre": MediaType.GENRE,
    "object.container.channelGroup": MediaType.CHANNELS,
    "object.container.channelGroup.audioChannelGroup": MediaType.CHANNELS,
    "object.container.channelGroup.videoChannelGroup": MediaType.CHANNELS,
    "object.container.epgContainer": MediaType.TVSHOW,
    "object.container.storageSystem": MediaType.PLAYLIST,
    "object.container.storageVolume": MediaType.PLAYLIST,
    "object.container.storageFolder": MediaType.PLAYLIST,
    "object.container.bookmarkFolder": MediaType.PLAYLIST,
}

# Map media_player media_content_type to UPnP class. Not everything will map
# directly, in which case it's not specified and other defaults will be used.
MEDIA_UPNP_CLASS_MAP: Mapping[str, str] = {
    MediaType.ALBUM: "object.container.album.musicAlbum",
    MediaType.ARTIST: "object.container.person.musicArtist",
    MediaType.CHANNEL: "object.item.videoItem.videoBroadcast",
    MediaType.CHANNELS: "object.container.channelGroup",
    MediaType.COMPOSER: "object.container.person.musicArtist",
    MediaType.CONTRIBUTING_ARTIST: "object.container.person.musicArtist",
    MediaType.EPISODE: "object.item.epgItem.videoProgram",
    MediaType.GENRE: "object.container.genre",
    MediaType.IMAGE: "object.item.imageItem",
    MediaType.MOVIE: "object.item.videoItem.movie",
    MediaType.MUSIC: "object.item.audioItem.musicTrack",
    MediaType.PLAYLIST: "object.item.playlistItem",
    MediaType.PODCAST: "object.item.audioItem.audioBook",
    MediaType.SEASON: "object.item.epgItem.videoProgram",
    MediaType.TRACK: "object.item.audioItem.musicTrack",
    MediaType.TVSHOW: "object.item.videoItem.videoBroadcast",
    MediaType.URL: "object.item.bookmarkItem",
    MediaType.VIDEO: "object.item.videoItem",
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