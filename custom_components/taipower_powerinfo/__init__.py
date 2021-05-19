"""The TaiPower PowerInfo integration."""
import asyncio
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    POWER_INFOS_COORDINATOR,
    POWER_INFOS_DATA,
    POWER_INFOS_NAME,
    PLATFORMS,
    UPDATE_LISTENER,
)
from .data import PowerInfoData

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    """Set up a Power Info entry."""

    power_info = _get_config_value(config_entry, CONF_NAME, "load_briefing3")

    power_info_data = PowerInfoData(hass, power_info)
    await power_info_data.async_update_power_infos()
    if power_info_data.info_name is None:
        raise ConfigEntryNotReady()

    power_info_coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"TaiPower Power Info for {power_info}",
        update_method=power_info_data.async_update,
        update_interval=DEFAULT_SCAN_INTERVAL,
    )

    power_info_hass_data = hass.data.setdefault(DOMAIN, {})
    power_info_hass_data[config_entry.entry_id] = {
        POWER_INFOS_DATA: power_info_data,
        POWER_INFOS_COORDINATOR: power_info_coordinator,
        POWER_INFOS_NAME: power_info,
    }

    # Fetch initial data so we have data when entities subscribe
    await power_info_coordinator.async_refresh()
    if power_info_data.info_name is None:
        raise ConfigEntryNotReady()

    for platform in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(config_entry, platform)
        )

    update_listener = config_entry.add_update_listener(async_update_options)
    hass.data[DOMAIN][config_entry.entry_id][UPDATE_LISTENER] = update_listener

    return True


async def async_update_options(hass: HomeAssistant, config_entry: ConfigEntry):
    """Update options."""
    await hass.config_entries.async_reload(config_entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(config_entry, platform)
                for platform in PLATFORMS
            ]
        )
    )
    if unload_ok:
        update_listener = hass.data[DOMAIN][config_entry.entry_id][UPDATE_LISTENER]
        update_listener()
        hass.data[DOMAIN].pop(config_entry.entry_id)
        if not hass.data[DOMAIN]:
            hass.data.pop(DOMAIN)
    return unload_ok


def _get_config_value(config_entry, key, default):
    if config_entry.options:
        return config_entry.options.get(key, default)
    return config_entry.data.get(key, default)

