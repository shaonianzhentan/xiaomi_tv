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
        errors = {}
        if user_input is None:
            DATA_SCHEMA = vol.Schema({})
            return self.async_show_form(step_id="user", data_schema=DATA_SCHEMA, errors=errors)
        return self.async_create_entry(title=DOMAIN, data=user_input)

    @staticmethod
    @callback
    def async_get_options_flow(entry: ConfigEntry):
        return OptionsFlowHandler(entry)


class OptionsFlowHandler(OptionsFlow):
    def __init__(self, config_entry: ConfigEntry):
        self.config_entry = config_entry
        self.hosts = None

    async def async_step_init(self, user_input=None):
        return await self.async_step_user(user_input)

    async def discovery(self):
        zc = await zeroconf.async_get_instance(self.hass)
        devices = await AsyncXiaomiTVScanner(zc)
        if len(devices) > 0:
            hosts = {}
            for item in devices:
                ip = item['ip']
                name = item['name'].split('.')[0]
                hosts[ip] = f"{name}（{ip}）"
            self.hosts = hosts
            return hosts

    async def async_step_user(self, user_input=None):
        hosts = self.hosts
        options = self.config_entry.options
        errors = {}
        if user_input is not None and hosts is not None:
            ip = user_input['ip']
            print(ip)
            name = hosts[ip].split('（')[0]
            return self.async_create_entry(title=name, data={
                'name': name,
                'ip': ip
            })

        hosts = await self.discovery()

        if hosts is None:
            errors['base'] = { '404' }
            DATA_SCHEMA = vol.Schema({})
        else:
            DATA_SCHEMA = vol.Schema({
                vol.Required("ip", default=options.get('ip', '')): vol.In(hosts)
            })
        return self.async_show_form(step_id="user", data_schema=DATA_SCHEMA, errors=errors)
