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
    MEDIA_TYPE_MUSIC,
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

from urllib.parse import urlparse, parse_qs, parse_qsl, quote
from .parsem3u import get_tvsource

protocol = 'xiaomi://'
tv_protocol = 'xiaomi://tv/'

class XiaomiRouter():

    tv_home = f'{tv_protocol}home'
    tv_playlist = f'{tv_protocol}playlist'

def parse_query(url_query):
    query = parse_qsl(url_query)
    data = {}
    for item in query:
        data[item[0]] = item[1]
    return data

async def async_browse_media(media_player, media_content_type, media_content_id):
    tvsource = await get_tvsource(media_player.tv_url)
    # 主界面
    if media_content_id in [None, XiaomiRouter.tv_home]:
        library_info = BrowseMedia(
            media_class=MEDIA_CLASS_DIRECTORY,
            media_content_id=XiaomiRouter.tv_home,
            media_content_type=MEDIA_TYPE_CHANNEL,
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
                    media_class=CHILD_TYPE_MEDIA_CLASS[MEDIA_TYPE_CHANNEL],
                    media_content_type=MEDIA_TYPE_CHANNEL,
                    media_content_id=f'{XiaomiRouter.tv_playlist}?title={item}&id={item}',
                    can_play=False,
                    can_expand=True,
                    # thumbnail="https://brands.home-assistant.io/_/group/logo@2x.png"
                )
            )
        return library_info
    
    # 协议转换
    url = urlparse(media_content_id)
    query = parse_query(url.query)

    title = query['title']
    id = query.get('id')

    if media_content_id.startswith(XiaomiRouter.tv_playlist):
        # 播放列表
        library_info = BrowseMedia(
            media_class=CHILD_TYPE_MEDIA_CLASS[MEDIA_TYPE_PLAYLIST],
            media_content_type=MEDIA_TYPE_PLAYLIST,
            media_content_id=media_content_id,
            title=title,
            can_play=False,
            can_expand=False,
            children=[],
        )
        channels = tvsource[id]
        for item in channels:
            library_info.children.append(
                BrowseMedia(
                    title=item[0],
                    media_class=MEDIA_CLASS_MUSIC,
                    media_content_type=MEDIA_TYPE_TVSHOW,
                    media_content_id=item[1],
                    can_play=True,
                    can_expand=False
                )
            )
        return library_info