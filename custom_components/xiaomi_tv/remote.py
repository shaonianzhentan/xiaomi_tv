import aiohttp, time
import logging
import voluptuous as vol

from homeassistant.components.media_player import PLATFORM_SCHEMA

from homeassistant.components.remote import (
    ATTR_DELAY_SECS,
    ATTR_NUM_REPEATS,
    DEFAULT_DELAY_SECS,
    RemoteEntity,
)

from homeassistant.const import CONF_HOST, CONF_NAME
import homeassistant.helpers.config_validation as cv
from .const import DOMAIN, DEFAULT_NAME

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_HOST): cv.string,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    }
)

def setup_platform(hass, config, add_entities, discovery_info=None):

    host = config.get(CONF_HOST)
    name = config.get(CONF_NAME)
    add_entities([XiaomiRemote(host, name, hass)])

class XiaomiRemote(RemoteEntity):

    def __init__(self, ip, name, hass):
        self.ip = ip
        self._name = name

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        return self.ip.replace('.', '')

    @property
    def is_on(self):
        return True

    @property
    def should_poll(self):
        return False

    async def async_turn_on(self, activity: str = None, **kwargs):
         """Turn the remote on."""

    async def async_turn_off(self, activity: str = None, **kwargs):
         """Turn the remote off."""
         
    async def async_send_command(self, command, **kwargs):
        """Send commands to a device."""
        # device = kwargs.get('device', '')
        key = command[0]
        _LOGGER.debug(command)
        actionKeys = {
            'sleep': ['power', 'wait', 'right', 'wait', 'right', 'wait', 'enter'],
            'power': ['power'],
            'up': ['up'],
            'down': ['down'],
            'right': ['right'],
            'left': ['left'],
            'home': ['home'],
            'enter': ['enter'],
            'back': ['back'],
            'menu': ['menu'],
            'volumedown': ['volumedown'],
            'volumeup': ['volumeup'],
            # 搜索功能
        }
        if key in actionKeys:
            await self.send_keystrokes(actionKeys[key])

    # 获取执行命令
    async def send_keystrokes(self, keystrokes):
        try:
            tv_url = 'http://{}:6095/controller?action=keyevent&keycode='.format(self.ip)
            request_timeout = aiohttp.ClientTimeout(total=1)
            for keystroke in keystrokes:
                if keystroke == 'wait':
                    time.sleep(0.7)
                else:
                    async with aiohttp.ClientSession(timeout=request_timeout) as session:
                        async with session.get(tv_url + keystroke) as response:
                            if response.status != 200:
                                return False
        except Exception as ex:
            _LOGGER.debug(ex)