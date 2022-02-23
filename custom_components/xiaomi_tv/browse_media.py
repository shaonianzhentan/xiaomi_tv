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

async def async_browse_media(media_player, media_content_type, media_content_id):
    print(media_content_type, media_content_id)
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
        channels = ["省卫视", "中央台"]
        for item in channels:
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
        channels = [
            {
                "title": "湖北卫视",
                "url": "https://freetyst.nf.migu.cn/public%2Fproduct9th%2Fproduct42%2F2021%2F02%2F0716%2F2019%E5%B9%B406%E6%9C%8826%E6%97%A517%E7%82%B908%E5%88%86%E5%86%85%E5%AE%B9%E5%87%86%E5%85%A5%E5%8D%8E%E7%BA%B373%E9%A6%96810969%2F%E5%85%A8%E6%9B%B2%E8%AF%95%E5%90%AC%2FMp3_64_22_16%2F6005751VAUU163746.mp3?Key=f24d176d32a189b2&Tim=1644937233045&channelid=01&msisdn=0d3a501458ea43e5abc748067be93cbc",
            },
            {
                "title": "CCTV1",
                "url": "http://111.63.117.13:6060/030000001000/CCTV-3/CCTV-3.m3u8",
            }
        ]
        for item in channels:
            library_info.children.append(
                BrowseMedia(
                    title=item['title'],
                    media_class=MEDIA_CLASS_TV_SHOW,
                    media_content_type=MEDIA_TYPE_TVSHOW,
                    media_content_id=item['url'],
                    can_play=True,
                    can_expand=False,
                    thumbnail="https://www.home-assistant.io/images/favicon-192x192.png"
                )
            )
    return library_info