from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from .const import DOMAIN, PLATFORMS

CONFIG_SCHEMA = cv.deprecated(DOMAIN)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    ''' 安装集成 '''
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(update_listener))
    return True

async def update_listener(hass, entry):
    ''' 更新配置 '''
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    ''' 删除集成 '''
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)