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


class UnknownMediaType(BrowseError):
    """Unknown media type."""


async def build_item_response(media_player, payload):
    """Create response payload for the provided media query."""
    # print(payload)
    search_id = payload["search_id"]
    search_type = payload["search_type"]
    hass = media_player.hass
    thumbnail = None
    title = None
    media = None
    media_class = MEDIA_CLASS_DIRECTORY
    can_play = False
    can_expand = True
    children = []
    base_url = get_url(hass)
    is_library = 'library_' in search_type

    properties = ["thumbnail"]
    if is_library:
        '''
        # 读取配置目录
        path = hass.config.path("media/ha_cloud_music")        
        # 获取所有文件
        music_list = media_player.api_music.get_local_media_list(search_type)
        for item in music_list:
            children.append(item_payload({
                    "label": item['name'], "type": 'music', "songid": item['url']
                }, media_player))
        '''
        title = search_type.replace('library_', '')
        media_class = MEDIA_CLASS_TV_SHOW
        can_play = True
        can_expand = False

    response = BrowseMedia(
        media_class=media_class,
        media_content_id=search_id,
        media_content_type=search_type,
        title=title,
        can_play=can_play,
        can_expand=can_expand,
        children=children,
        thumbnail=thumbnail,
    )

    if is_library:
        response.children_media_class = MEDIA_CLASS_TV_SHOW
    else:
        response.calculate_children_class()

    return response


def item_payload(item, media_player):
    # print(item)
    title = item["label"]
    media_class = None
    media_content_type = item["type"]

    if "songid" in item:
        # 音乐
        media_class = MEDIA_CLASS_TV_SHOW
        media_content_id = f"{item['songid']}"
        can_play = True
        can_expand = False
    else:
        # 目录
        media_class = MEDIA_CLASS_DIRECTORY
        media_content_id = ""
        can_play = False
        can_expand = True

    return BrowseMedia(
        title=title,
        media_class=media_class,
        media_content_type=media_content_type,
        media_content_id=media_content_id,
        can_play=can_play,
        can_expand=can_expand,
        thumbnail=thumbnail
    )


def library_payload(media_player):
    """
    创建音乐库
    """
    library_info = BrowseMedia(
        media_class=MEDIA_CLASS_DIRECTORY,
        media_content_id="library",
        media_content_type="library",
        title="电视直播",
        can_play=False,
        can_expand=True,
        children=[],
    )
    # 默认列表
    channels = [
        {
            "id": 1,
            "title": "省卫视",
            "type": "tv",
        },
        {
            "id": 2,
            "title": "中央台",
            "type": "tv",
        }
    ]
    for item in channels:
        library_info.children.append(
            BrowseMedia(
                title=item['title'],
                media_class=MEDIA_CLASS_DIRECTORY,
                media_content_type=item['type'],
                media_content_id=item['id'],
                can_play=False,
                can_expand=True,
                thumbnail="https://www.home-assistant.io/images/favicon-192x192.png"
            )
        )
    return library_info