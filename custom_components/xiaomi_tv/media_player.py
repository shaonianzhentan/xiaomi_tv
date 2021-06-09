"""Add support for the Xiaomi TVs."""
import logging
import requests
import pymitv
import voluptuous as vol

from homeassistant.components.media_player import PLATFORM_SCHEMA, MediaPlayerEntity
from homeassistant.components.media_player.const import (
    SUPPORT_TURN_OFF,
    SUPPORT_TURN_ON,
    SUPPORT_VOLUME_STEP,
    SUPPORT_SELECT_SOURCE,
    SUPPORT_SELECT_SOUND_MODE,
    SUPPORT_PLAY_MEDIA,
)
from homeassistant.const import CONF_HOST, CONF_NAME, STATE_OFF, STATE_ON
import homeassistant.helpers.config_validation as cv

DEFAULT_NAME = "小米电视"

_LOGGER = logging.getLogger(__name__)

SUPPORT_XIAOMI_TV = SUPPORT_VOLUME_STEP | SUPPORT_TURN_ON | SUPPORT_TURN_OFF | SUPPORT_SELECT_SOURCE | SUPPORT_SELECT_SOUND_MODE | SUPPORT_PLAY_MEDIA

# No host is needed for configuration, however it can be set.
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_HOST): cv.string,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    }
)

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Xiaomi TV platform."""

    # If a hostname is set. Discovery is skipped.
    host = config.get(CONF_HOST)
    name = config.get(CONF_NAME)

    if host is not None:
        # Check if there's a valid TV at the IP address.
        if not pymitv.Discover().check_ip(host):
            _LOGGER.error("Could not find Xiaomi TV with specified IP: %s", host)
        else:
            # Register TV with Home Assistant.
            add_entities([XiaomiTV(host, name)])
    else:
        # Otherwise, discover TVs on network.
        add_entities(XiaomiTV(tv, DEFAULT_NAME) for tv in pymitv.Discover().scan())


class XiaomiTV(MediaPlayerEntity):
    """Represent the Xiaomi TV for Home Assistant."""

    def __init__(self, ip, name):
        """Receive IP address and name to construct class."""
        self.ip = ip
        # Initialize the Xiaomi TV.
        self._tv = pymitv.TV(ip)
        # Default name value, only to be overridden by user.
        self._name = name
        self._state = STATE_OFF
        self._volume_level = self._tv.get_volume()
        # 应用
        self.apps = {
            '奇异果': 'com.gitvdemo.video',
            '酷喵': 'com.cibn.tv',
            '腾讯视频': 'com.ktcp.video',
            '哔哩哔哩': 'com.xiaodianshi.tv.yst',
            '芒果TV': 'com.hunantv.license',
            'Kodi': 'org.xbmc.kodi',
            '视频头条': 'com.duokan.videodaily',
            'QQ音乐': 'com.tencent.qqmusictv',
            '桌面': 'com.mitv.tvhome',
            '小米通话': 'com.xiaomi.mitv.tvvideocall',
            '小爱同学': 'com.xiaomi.voicecontrol',
            '无线投屏': 'com.xiaomi.mitv.smartshare',
        }
        _source_list = []
        for app in self.apps:
            _source_list.append(app)
        self._source_list = _source_list

    @property
    def name(self):
        """Return the display name of this TV."""
        return self._name

    @property
    def volume_level(self):
        return self._volume_level

    @property
    def state(self):
        """Return _state variable, containing the appropriate constant."""
        return self._state

    @property
    def assumed_state(self):
        """Indicate that state is assumed."""
        return True

    @property
    def sound_mode_list(self):
        return ['hdmi1', 'hdmi2', 'hdmi3', 'gallery', 'aux', 'tv', 'vga', 'av', 'dtmb']

    @property
    def source_list(self):
        return self._source_list

    @property
    def supported_features(self):
        """Flag media player features that are supported."""
        return SUPPORT_XIAOMI_TV

    # 更新属性
    def update(self):
        self._volume_level = self._tv.get_volume()
        self._state = self._tv.is_on and STATE_ON or STATE_OFF

    # 选择应用
    def select_source(self, source):
        # 如果是切换源
        if self.source_path.count(source) > 0:
            return self._tv.change_source(source)
        # 打开应用
        tv_url = 'http://{}:6095/controller?action=startapp&type=packagename&packagename='.format(self.ip)
        if self.apps[source] is not None:
            requests.get(tv_url + self.apps[source])

    # 选择数据源
    def select_source_mode(self, mode):
        # 如果是切换源
        if self.sound_mode_list.count(mode) > 0:
            return self._tv.change_source(mode)

    def turn_off(self):
        if self._state != STATE_OFF:
            self._tv.turn_off()

            self._state = STATE_OFF

    def turn_on(self):
        """Wake the TV back up from sleep."""
        if self._state != STATE_ON:
            self._tv.wake()

            self._state = STATE_ON

    def volume_up(self):
        """Increase volume by one."""
        self._tv.volume_up()

    def volume_down(self):
        """Decrease volume by one."""
        self._tv.volume_down()