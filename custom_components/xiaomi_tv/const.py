from homeassistant.components.media_player import const as _mp_const

DEFAULT_NAME = "小米电视"
DOMAIN = "xiaomi_tv"
VERSION = "1.2.2"
SERVICE_ADB_COMMAND = "adb_command"
PLATFORMS = ["media_player", "remote"]

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