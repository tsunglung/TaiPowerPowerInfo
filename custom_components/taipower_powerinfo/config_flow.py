"""Config flow for TaiPower Power Info integration."""
import logging

import voluptuous as vol

from homeassistant import config_entries, core, exceptions
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import callback
from homeassistant.const import CONF_NAME
from homeassistant.helpers import config_validation as cv

from .const import (
    CONFIG_FLOW_VERSION,
    DOMAIN,
    POWER_INFOS
)
from .data import PowerInfoData

_LOGGER = logging.getLogger(__name__)


async def validate_input(hass: core.HomeAssistant, data):
    """Validate that the user input allows us to connect to DataPoint.

    Data has the keys from DATA_SCHEMA with values provided by the user.
    """

    power_info = data[CONF_NAME]

    power_info_data = PowerInfoData(hass, power_info)
    await power_info_data.async_update_power_infos()
    if power_info_data.info_name is None:
        raise CannotConnect()

    return {"power_info": power_info_data.power_info}


class PowerInfosConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Power Info integration."""

    VERSION = CONFIG_FLOW_VERSION
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry):
        """ get option flow """
        return PowerInfosOptionsFlow(config_entry)

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            power_infos = "taipower"
            for i in user_input[CONF_NAME]:
                power_infos = power_infos + "-" + i
            await self.async_set_unique_id(
                f"{power_infos}"
            )
            self._abort_if_unique_id_configured()

            try:
                await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                title = ""
                for i in user_input[CONF_NAME]:
                    title = title + " " + POWER_INFOS[i]
                return self.async_create_entry(
                    title=title, data=user_input
                )

        data_schema = vol.Schema(
            {
                vol.Required(CONF_NAME): cv.multi_select(
                    POWER_INFOS
                ),
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )


class PowerInfosOptionsFlow(config_entries.OptionsFlow):
    """Handle options."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=self._get_options_schema(),
        )

    def _get_options_schema(self):
        return vol.Schema(
            {
                vol.Optional(
                    CONF_NAME,
                    default=_get_config_value(
                        self.config_entry, CONF_NAME, "5")
                ): cv.multi_select(POWER_INFOS)
            }
        )


def _get_config_value(config_entry, key, default):
    if config_entry.options:
        return config_entry.options.get(key, default)
    return config_entry.data.get(key, default)

class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""
