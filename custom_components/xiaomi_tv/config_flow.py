from __future__ import annotations

from typing import Any
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, OptionsFlow, ConfigEntry
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN
from homeassistant.components import zeroconf
from .discovery import AsyncXiaomiTVScanner



class XiaomiConfigFlow(ConfigFlow, domain=DOMAIN):

    VERSION = 1
    devices = []

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
    
        if user_input is None:
            errors = {}
            zc = await zeroconf.async_get_instance(self.hass)
            devices = await AsyncXiaomiTVScanner(zc)
            self.devices = devices
            if len(devices) > 0:
                hosts = list(map(lambda item: f"{item['name'].split('.')[0]}（{item['ip']}）", devices))
                default_host = hosts[0]
                DATA_SCHEMA = vol.Schema({
                    vol.Required("host", default = default_host): vol.In(hosts)
                })
            else:
                DATA_SCHEMA = vol.Schema({
                    vol.Required("name", default = '小米电视'): str,
                    vol.Required("host"): str
                })
                            
            return self.async_show_form(step_id="user", data_schema=DATA_SCHEMA, errors=errors)

        host = user_input.get('host')
        name = user_input.get('name')
        if '（' in host:
            dv = list(filter(lambda item: f"{item['name'].split('.')[0]}（{item['ip']}）" == host, self.devices))
            obj = dv[0]
            name = obj['name']
            host = obj['ip']

        return self.async_create_entry(title=host, data={
            'name': name,
            'host': host
        })
