from __future__ import annotations

from typing import Any
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN

DATA_SCHEMA = vol.Schema({
    vol.Required("name", default = "小米电视"): str,
    vol.Required("host"): str
})

class SimpleConfigFlow(ConfigFlow, domain=DOMAIN):

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
    
        if user_input is None:
            errors = {}
            return self.async_show_form(step_id="user", data_schema=DATA_SCHEMA, errors=errors)

        return self.async_create_entry(title=DOMAIN, data=user_input)