"""Support for TaiPower Power Infos service."""

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import ATTR_ATTRIBUTION, DEVICE_CLASS_TIMESTAMP
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.typing import ConfigType

from .const import (
    ATTRIBUTION,
    ATTR_PUBLISH_TIME,
    ATTR_CURRENT_LOAD,
    ATTR_CURRENT_RATE,
    ATTR_MAX_CAPACITY,
    ATTR_PEAK_HOUR_RANGE,
    ATTR_PEAK_DEMA_LOAD,
    ATTR_PEAK_INDICATOR,
    CONF_POWER_INFO,
    DOMAIN,
    POWER_INFOS_COORDINATOR,
    POWER_INFOS_DATA,
    POWER_INFOS_NAME,
    POWER_INFOS
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigType, async_add_entities
) -> None:
    """Set up the TaiPower Power Info sensor platform."""
    hass_data = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        [
            PowerInfoSensor(entry.data, hass_data, power_info)
            for power_info in hass_data[POWER_INFOS_NAME]
        ],
        False,
    )


class PowerInfoSensor(SensorEntity):
    """Implementation of a TaiPower Power Info sensor."""

    def __init__(self, entry_data, hass_data, power_info):
        """Initialize the sensor."""
        self._data = hass_data[POWER_INFOS_DATA]
        self._coordinator = hass_data[POWER_INFOS_COORDINATOR]

        self._name = f"{POWER_INFOS[power_info]}"
        self._unique_id = f"{POWER_INFOS[power_info]} {power_info}"

        self.power_infos_power_info = power_info
        self.power_infos_info_name = None
        self.power_infos = None
        self._info = {}

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def unique_id(self):
        """Return the unique of the sensor."""
        return self._unique_id

    @property
    def state(self):
        """Return the state of the sensor."""
        state = None
        for i in self.power_infos:
            for j, k in i.items():
                if self.power_infos_power_info == j:
                    state = k[ATTR_PEAK_INDICATOR]
                    self._info[ATTR_PUBLISH_TIME] = k[ATTR_PUBLISH_TIME]
                    self._info[ATTR_CURRENT_LOAD] = k[ATTR_CURRENT_LOAD]
                    self._info[ATTR_CURRENT_RATE] = k[ATTR_CURRENT_RATE]
                    self._info[ATTR_MAX_CAPACITY] = k[ATTR_MAX_CAPACITY]
                    self._info[ATTR_PEAK_HOUR_RANGE] = k[ATTR_PEAK_HOUR_RANGE]
                    self._info[ATTR_PEAK_DEMA_LOAD] = k[ATTR_PEAK_DEMA_LOAD]

        return state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return None

    @property
    def icon(self):
        """Return the icon for the entity card."""
        return "mdi:information"

    @property
    def device_class(self):
        """Return the device class of the sensor."""
        return None

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the device."""
        return {
            ATTR_ATTRIBUTION: ATTRIBUTION,
            ATTR_PUBLISH_TIME: self._info[ATTR_PUBLISH_TIME] if self.power_infos else None,
            ATTR_CURRENT_LOAD: self._info[ATTR_CURRENT_LOAD] if self.power_infos else None,
            ATTR_CURRENT_RATE: self._info[ATTR_CURRENT_RATE] if self.power_infos else None,
            ATTR_MAX_CAPACITY: self._info[ATTR_MAX_CAPACITY] if self.power_infos else None,
            ATTR_PEAK_HOUR_RANGE: self._info[ATTR_PEAK_HOUR_RANGE] if self.power_infos else None,
            ATTR_PEAK_DEMA_LOAD: self._info[ATTR_PEAK_DEMA_LOAD] if self.power_infos else None,
        }

    async def async_added_to_hass(self) -> None:
        """Set up a listener and load data."""
        self.async_on_remove(
            self._coordinator.async_add_listener(self._update_callback)
        )
        self._update_callback()

    async def async_update(self):
        """Schedule a custom update via the common entity update service."""
        await self._coordinator.async_request_refresh()

    @callback
    def _update_callback(self) -> None:
        """Load data from integration."""
        self.power_infos = self._data.infos
        self.async_write_ha_state()

    @property
    def should_poll(self) -> bool:
        """Entities do not individually poll."""
        return False

    @property
    def available(self):
        """Return if state is available."""
        return self.power_infos is not None
