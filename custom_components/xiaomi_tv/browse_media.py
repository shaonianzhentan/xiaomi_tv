"""Support for media browsing."""
import logging, os
from homeassistant.helpers.network import get_url
from homeassistant.components.media_player import BrowseError, BrowseMedia
from homeassistant.components.media_player.const import (
    MEDIA_CLASS_ALBUM,
    MEDIA_CLASS_ARTIST,
    MEDIA_CLASS_CHANNEL,
    MEDIA_CLASS_DIRECTORY,
    MEDIA_CLASS_EPISODE,
    MEDIA_CLASS_MOVIE,
    MEDIA_CLASS_MUSIC,
    MEDIA_CLASS_PLAYLIST,
    MEDIA_CLASS_SEASON,
    MEDIA_CLASS_TRACK,
    MEDIA_CLASS_TV_SHOW,
    MEDIA_TYPE_ALBUM,
    MEDIA_TYPE_ARTIST,
    MEDIA_TYPE_CHANNEL,
    MEDIA_TYPE_EPISODE,
    MEDIA_TYPE_MOVIE,
    MEDIA_TYPE_PLAYLIST,
    MEDIA_TYPE_SEASON,
    MEDIA_TYPE_TRACK,
    MEDIA_TYPE_TVSHOW,
)

PLAYABLE_MEDIA_TYPES = [
    MEDIA_TYPE_ALBUM,
    MEDIA_TYPE_ARTIST,
    MEDIA_TYPE_TRACK,
]

CONTAINER_TYPES_SPECIFIC_MEDIA_CLASS = {
    MEDIA_TYPE_ALBUM: MEDIA_CLASS_ALBUM,
    MEDIA_TYPE_ARTIST: MEDIA_CLASS_ARTIST,
    MEDIA_TYPE_PLAYLIST: MEDIA_CLASS_PLAYLIST,
    MEDIA_TYPE_SEASON: MEDIA_CLASS_SEASON,
    MEDIA_TYPE_TVSHOW: MEDIA_CLASS_TV_SHOW,
}

CHILD_TYPE_MEDIA_CLASS = {
    MEDIA_TYPE_SEASON: MEDIA_CLASS_SEASON,
    MEDIA_TYPE_ALBUM: MEDIA_CLASS_ALBUM,
    MEDIA_TYPE_ARTIST: MEDIA_CLASS_ARTIST,
    MEDIA_TYPE_MOVIE: MEDIA_CLASS_MOVIE,
    MEDIA_TYPE_PLAYLIST: MEDIA_CLASS_PLAYLIST,
    MEDIA_TYPE_TRACK: MEDIA_CLASS_TRACK,
    MEDIA_TYPE_TVSHOW: MEDIA_CLASS_TV_SHOW,
    MEDIA_TYPE_CHANNEL: MEDIA_CLASS_CHANNEL,
    MEDIA_TYPE_EPISODE: MEDIA_CLASS_EPISODE,
}

_LOGGER = logging.getLogger(__name__)

from .parsem3u import get_tvsource

async def async_browse_media(media_player, media_content_type, media_content_id):
    print(media_content_type, media_content_id)
    tvsource = get_tvsource()
    # 主界面
    if media_content_type in [None, 'home']:
        library_info = BrowseMedia(
            media_class=MEDIA_CLASS_DIRECTORY,
            media_content_id="home",
            media_content_type="home",
            title="电视直播",
            can_play=False,
            can_expand=True,
            children=[],
        )
        # 分组列表        
        for item in tvsource:
            library_info.children.append(
                BrowseMedia(
                    title=item,
                    media_class=MEDIA_CLASS_DIRECTORY,
                    media_content_type="tv",
                    media_content_id=item,
                    can_play=False,
                    can_expand=True,
                    thumbnail="https://www.home-assistant.io/images/favicon-192x192.png"
                )
            )
    elif media_content_type == 'tv':
        library_info = BrowseMedia(
            media_class=MEDIA_CLASS_DIRECTORY,
            media_content_id=media_content_id,
            media_content_type=media_content_type,
            title=media_content_id,
            can_play=False,
            can_expand=False,
            children=[],
        )
        # 播放列表
        channels = tvsource[media_content_id]
        for item in channels:
            library_info.children.append(
                BrowseMedia(
                    title=item[0],
                    media_class=MEDIA_CLASS_TV_SHOW,
                    media_content_type=MEDIA_TYPE_TVSHOW,
                    media_content_id=item[1],
                    can_play=True,
                    can_expand=False,
                    thumbnail="https://www.home-assistant.io/images/favicon-192x192.png"
                )
            )
    return library_info