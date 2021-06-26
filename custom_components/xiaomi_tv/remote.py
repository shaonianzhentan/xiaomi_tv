import asyncio
import logging, requests
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
        key = command[0]
        _LOGGER.debug(command)
        self.keyevent(key)

    # 获取执行命令
    def keyevent(self, keycode):
        try:
            request_timeout = 0.1
            res = requests.get(f'http://{self.ip}:6095/controller?action=keyevent&keycode={keycode}', timeout=request_timeout)
            res.encoding = 'utf-8'
            return res.json()
        except Exception as ex:
            _LOGGER.debug(ex)
        return None