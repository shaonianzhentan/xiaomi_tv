"""Add support for the Xiaomi TVs."""
import logging
import requests, time, hashlib
import voluptuous as vol
from icmplib import ping

from homeassistant.components.media_player import PLATFORM_SCHEMA, MediaPlayerEntity
from homeassistant.components.media_player.const import (
    SUPPORT_TURN_OFF,
    SUPPORT_TURN_ON,
    SUPPORT_VOLUME_STEP,
    SUPPORT_VOLUME_SET,
    SUPPORT_VOLUME_MUTE,
    SUPPORT_SELECT_SOURCE,
    SUPPORT_SELECT_SOUND_MODE,
    SUPPORT_PLAY_MEDIA,
)
from homeassistant.const import CONF_HOST, CONF_NAME, STATE_OFF, STATE_ON
import homeassistant.helpers.config_validation as cv

DEFAULT_NAME = "电视"

_LOGGER = logging.getLogger(__name__)

SUPPORT_XIAOMI_TV = SUPPORT_VOLUME_STEP | SUPPORT_VOLUME_MUTE | SUPPORT_VOLUME_SET | \
    SUPPORT_TURN_ON | SUPPORT_TURN_OFF | SUPPORT_SELECT_SOURCE | SUPPORT_SELECT_SOUND_MODE | SUPPORT_PLAY_MEDIA

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
    add_entities([XiaomiTV(host, name, hass)])

class XiaomiTV(MediaPlayerEntity):
    """Represent the Xiaomi TV for Home Assistant."""

    def __init__(self, ip, name, hass):
        """Receive IP address and name to construct class."""
        self.hass = hass
        self.ip = ip
        self._name = name
        self._volume_level = 1
        self._state = STATE_OFF
        self._source_list = []
        # 已知应用列表
        self.apps = {
                '云视听极光': 'com.ktcp.video',
                '芒果TV': 'com.hunantv.license',
                '银河奇异果': 'com.gitvdemo.video',
                'CIBN酷喵': 'com.cibn.tv',
                '视频头条': 'com.duokan.videodaily',
                'QQ音乐': 'com.tencent.qqmusictv'
            }

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
        return ['up', 'down', 'left', 'right', 'menu', 'home', 'back', 'enter']

    @property
    def source_list(self):
        return self._source_list

    @property
    def supported_features(self):
        """Flag media player features that are supported."""
        return SUPPORT_XIAOMI_TV

    # 更新属性
    def update(self):
        # 检测当前IP是否在线
        host = ping(self.ip, count=1, interval=0.2)
        self._state = host.is_alive and STATE_ON or STATE_OFF
        self.get_apps()

    # 选择应用
    def select_source(self, source):
        if self.apps[source] is not None:
            self.htt('run', {'packageName': self.apps[source]})

    # 选择数据源
    def select_source_mode(self, mode):
        print(mode)

    def turn_off(self):
        if self._state != STATE_OFF:
            self.fire_event('off')
            self._state = STATE_OFF

    def turn_on(self):
        """Wake the TV back up from sleep."""
        if self._state != STATE_ON:
            self.fire_event('on')
            self._state = STATE_ON

    def volume_up(self):
        self.http('key', {'code': 24})

    def volume_down(self):
        self.http('key', {'code': 25})

    def mute_volume(self, mute):
        self.http('key', {'code': 164})

    def set_volume_level(self, volume):
        print(volume)

    def media_play(self):
        self.keyevent(23)

    def media_pause(self):
        self.keyevent(23)

    # 发送事件
    def fire_event(self, cmd):
        self.hass.bus.async_fire("xiaomi_tv", { 'ip': self.ip, 'type': cmd })

    # 获取安装APP
    def get_apps(self):
        # 获取本机APP列表
        res = self.http('apps', { 'system': 'false' })
        if res is not None:
            for app in res:
                self.apps.update({ app['lable']: app['packageName'] })
        # 绑定数据源
        _source_list = []
        for name in self.apps:
            _source_list.append(name)
        self._source_list = _source_list

    # 执行按键命令
    def keyevent(self, keycode):
        data = {'code': keycode}
        self.http('keydown', data)
        self.http('keyup', data)

    # 获取执行命令
    def http(self, url, data):
        try:
            request_timeout = 0.1
            res = requests.post(f'http://{self.ip}:9978/{url}', data, timeout=request_timeout)
            return res.json()
        except Exception as ex:
            _LOGGER.debug(ex)
        return None