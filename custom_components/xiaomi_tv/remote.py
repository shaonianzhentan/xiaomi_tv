import aiohttp, time
import logging
import voluptuous as vol

from homeassistant.components.remote import (
    ATTR_DELAY_SECS,
    ATTR_NUM_REPEATS,
    DEFAULT_DELAY_SECS,
    RemoteEntity,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_NAME
import homeassistant.helpers.config_validation as cv
from .const import DOMAIN, DEFAULT_NAME, VERSION
from .utils import KeySearch, keyevent, startapp

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    host = entry.data.get(CONF_HOST)
    name = entry.data.get(CONF_NAME)
    async_add_entities([XiaomiRemote(host, name, hass)], True)

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
    
    @property
    def device_info(self):
        return {
            "identifiers": {
                (DOMAIN, self.unique_id)
            },
            "name": self.name,
            "manufacturer": "Xiaomi",
            "model": self.ip,
            "sw_version": VERSION,
            "via_device": (DOMAIN, self.ip),
        }

    async def async_turn_on(self, activity: str = None, **kwargs):
         """Turn the remote on."""

    async def async_turn_off(self, activity: str = None, **kwargs):
         """Turn the remote off."""
         
    async def async_send_command(self, command, **kwargs):
        """Send commands to a device."""
        key = command[0]
        actionKeys = {
            'sleep': ['power', 'right', 'right', 'enter'],
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
            # ????????????????????????????????????????????????????????????????????????
            'adb': [
                # ?????????????????????
                'right', 'right', 'right', 'enter',
                # ??????ADB??????
                'down', 'down', 'enter', 
                # ????????????
                'up', 'enter', 
                # ????????????
                'down', 'left', 'enter']
        }
        # ????????????
        if ',' in key:
            actionKeys[key] = key.split(',')

        # ??????ADB
        if key == 'adb':
            await self.startapp('com.xiaomi.mitv.settings')
            time.sleep(1)

        if key in actionKeys:
            await self.send_keystrokes(actionKeys[key])

    # ????????????
    async def startapp(self, app_id):
        await keyevent(self.ip, 'home')
        time.sleep(1)
        await startapp(self.ip, app_id)
        time.sleep(1)

    # ??????????????????
    async def send_keystrokes(self, keystrokes):
        try:
            for keystroke in keystrokes:
                wait = 1.5
                if '-' in keystroke:
                    arr = keystroke.split('-')
                    keystroke = arr[0]
                    wait = float(arr[1])
                res = await keyevent(self.ip, keystroke)
                # print(res)
                # ?????????????????????????????????
                if len(keystrokes) > 1:
                    time.sleep(wait)

        except Exception as ex:
            _LOGGER.debug(ex)