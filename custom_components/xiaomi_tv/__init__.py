from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from .const import DOMAIN, PLATFORMS, SEND_KEY
from .utils import send_keystrokes, open_app, ACTION_KEYS

CONFIG_SCHEMA = cv.deprecated(DOMAIN)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    ''' 安装集成 '''
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(update_listener))

    if hass.services.has_service(DOMAIN, SEND_KEY) == False:
        async def async_send_key(call):
            data = call.data
            entity_id = data.get('entity_id')
            key = data.get('key')
            state = hass.states.get(entity_id)
            ip = state.attributes.get('ip')

            # 打开ADB
            if key == 'adb':
                await open_app(ip, 'com.xiaomi.mitv.settings')
            elif key in ACTION_KEYS:
                await send_keystrokes(ip, ACTION_KEYS[key])
            else:
                await send_keystrokes(ip, key.split(','))

        hass.services.async_register(DOMAIN, SEND_KEY, async_send_key)
    return True

async def update_listener(hass, entry):
    ''' 更新配置 '''
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    ''' 删除集成 '''
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)