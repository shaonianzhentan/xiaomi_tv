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
    add_entities([XiaomiTV(host, name, hass)])

class XiaomiTV(MediaPlayerEntity):
    """Represent the Xiaomi TV for Home Assistant."""

    def __init__(self, ip, name, hass):
        """Receive IP address and name to construct class."""
        self.hass = hass
        self.ip = ip
        self._tv = None
        self._name = name
        self._volume_level = 0
        self._state = STATE_OFF
        self._source_list = []
        self.update()

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
        try:
            if self._tv is None:
                self._tv = pymitv.TV(ip)
            self._volume_level = self._tv.get_volume()
            self._state = self._tv.is_on and STATE_ON or STATE_OFF
            # 获取本机APP列表
            res = self.execute('getinstalledapp&count=999&changeIcon=1')
            AppInfo = res['data']['AppInfo']
            apps = {}
            _source_list = []
            for app in AppInfo:
                AppName = app['AppName']
                _source_list.append(AppName)
                apps.update({ AppName: app['PackageName'] })        
            self.apps = apps
            self._source_list = _source_list
        except Exception as ex:
            _LOGGER.debug(ex)

    # 选择应用
    def select_source(self, source):
        if self.apps[source] is not None:
            self.execute('startapp&type=packagename&packagename=' + self.apps[source])

    # 选择数据源
    def select_source_mode(self, mode):
        # 如果是切换源
        if self.sound_mode_list.count(mode) > 0:
            return self._tv.change_source(mode)

    def turn_off(self):
        if self._state != STATE_OFF:
            self._tv.turn_off()
            self.fire_event('off')
            self._state = STATE_OFF

    def turn_on(self):
        """Wake the TV back up from sleep."""
        if self._state != STATE_ON:
            self.fire_event('on')
            self._state = STATE_ON

    def volume_up(self):
        """Increase volume by one."""
        self._tv.volume_up()

    def volume_down(self):
        """Decrease volume by one."""
        self._tv.volume_down()

    # 发送事件
    def fire_event(self, cmd):
        self.hass.bus.async_fire("xiaomi_tv", { 'ip': self.ip, 'type': cmd })

    # 获取执行命令
    def execute(self, cmd):
        request_timeout = 0.1
        tv_url = 'http://{}:6095/controller?action='.format(self.ip) + cmd
        res = requests.get(tv_url, timeout=request_timeout)
        res.encoding = 'utf-8'
        return res.json()