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
from .manifest import manifest
from .tv_source import TVSource

protocol = 'xiaomi://'
tv_protocol = 'xiaomi://tv/'

class XiaomiRouter():

    tv_home = f'{tv_protocol}home'
    tv_playlist = f'{tv_protocol}playlist'
    tv_search = f'{tv_protocol}search'

def parse_query(url_query):
    query = parse_qsl(url_query)
    data = {}
    for item in query:
        data[item[0]] = item[1]
    return data


# 初始化直播源
async def async_Init_TVSource(hass):
    tv = hass.data.get(manifest.domain)
    if tv is None:
        tv = TVSource()
        hass.data.setdefault(manifest.domain, tv)
    # 更新数据
    await tv.update()
    return tv

async def async_browse_media(media_player, media_content_type, media_content_id):
    hass = media_player.hass
    # 初始化直播源
    tv = await async_Init_TVSource(hass)

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
        for item in tv.groups:
            library_info.children.append(
                BrowseMedia(
                    title=item,
                    media_class=CHILD_TYPE_MEDIA_CLASS[MEDIA_TYPE_CHANNEL],
                    media_content_type=MEDIA_TYPE_CHANNEL,
                    media_content_id=f'{XiaomiRouter.tv_playlist}?group={item}',
                    can_play=False,
                    can_expand=True
                )
            )
        return library_info
    
    # 协议转换
    url = urlparse(media_content_id)
    query = parse_query(url.query)

    if media_content_id.startswith(XiaomiRouter.tv_playlist):
        # 播放列表
        group = query['group']
        library_info = BrowseMedia(
            media_class=CHILD_TYPE_MEDIA_CLASS[MEDIA_TYPE_PLAYLIST],
            media_content_type=MEDIA_TYPE_PLAYLIST,
            media_content_id=media_content_id,
            title=group,
            can_play=False,
            can_expand=False,
            children=[],
        )
        channels = filter(lambda x: x.group == group, tv.playlist)
        for item in channels:
            library_info.children.append(
                BrowseMedia(
                    title=item.title,
                    media_class=MEDIA_CLASS_MUSIC,
                    media_content_type=MEDIA_TYPE_TVSHOW,
                    media_content_id=item.path,
                    can_play=True,
                    can_expand=False
                )
            )
        return library_info


async def async_play_media(media_player, media_content_type, media_content_id):
    if media_content_id is None or media_content_id.startswith(protocol) == False:
        return

    hass = media_player.hass
    # 初始化直播源
    tv = await async_Init_TVSource(hass)

    # 协议转换
    url = urlparse(media_content_id)
    query = parse_query(url.query)

    if media_content_id.startswith(XiaomiRouter.tv_search):
        kv = query.get('kv')
        # 电视搜索
        return await tv.search_channel(kv)