"""Common TaiPower Power Info Data class used by both sensor and entity."""
import logging
import json
from json import JSONDecodeError
from http import HTTPStatus

from aiohttp.hdrs import USER_AGENT
import requests

from .const import (
    POWER_INFOS,
    ATTR_PUBLISH_TIME,
    ATTR_CURRENT_LOAD,
    ATTR_CURRENT_RATE,
    ATTR_MAX_CAPACITY,
    ATTR_PEAK_HOUR_RANGE,
    ATTR_PEAK_DEMA_LOAD,
    ATTR_PEAK_INDICATOR,
    INFO_WRAPPER,
    BASE_URL,
    REQUEST_TIMEOUT
)

_LOGGER = logging.getLogger(__name__)


class PowerInfoData:
    """Get  Power Info from TaiPower. """

    def __init__(self, hass, power_infos):
        """Initialize the data object."""
        self._hass = hass

        # Holds the current data from the NCDR
        self.data = []
        self.infos = None
        self.info_name = None
        self.power_infos = power_infos
        self.power_info = None
        self.uri = None

    async def async_update_power_infos(self):
        """Async wrapper for getting power info data."""
        return await self._hass.async_add_executor_job(self._update_infos)

    def get_data_for_power_info(self, power_info, data):
        """ return data """
        self._update_infos()
        return self.data

    def _parser_json(self, power_info, text):
        """ parser json """
        try:
            the_dict = json.loads(text)
        except JSONDecodeError:
            _LOGGER.error("Received error from TaiPower")

        if "success" in the_dict and the_dict["success"] == "true":
            try:
                data = {}
                value = {}
                if "records" in the_dict:
                    value[ATTR_CURRENT_LOAD] = the_dict["records"][0][ATTR_CURRENT_LOAD]
                    value[ATTR_CURRENT_RATE] = the_dict["records"][0][ATTR_CURRENT_RATE]
                    value[ATTR_MAX_CAPACITY] = the_dict["records"][1][ATTR_MAX_CAPACITY]
                    value[ATTR_PEAK_HOUR_RANGE] = the_dict["records"][1][ATTR_PEAK_HOUR_RANGE]
                    value[ATTR_PEAK_DEMA_LOAD] = the_dict["records"][1][ATTR_PEAK_DEMA_LOAD]
                    value[ATTR_PEAK_INDICATOR] = the_dict["records"][1][ATTR_PEAK_INDICATOR]
                    value[ATTR_PUBLISH_TIME] = the_dict["records"][1][ATTR_PUBLISH_TIME]
                data[power_info] = value

                return data
            except KeyError:
                _LOGGER.error("Received error from TaiPower")
        return None


    def _update_infos(self):
        """Return the power info json."""

        for i in self.power_infos:
            self.uri = BASE_URL.format(INFO_WRAPPER[i])
            req = None
            try:
                req = requests.get(
                    self.uri,
                    timeout=REQUEST_TIMEOUT)

            except requests.exceptions.RequestException as err:
                _LOGGER.error("Failed fetching data for %s", POWER_INFOS[i])

            if req and req.status_code == HTTPStatus.OK:
                value = self._parser_json(i, req.text)
                if value:
                    self.data.append(value)
                    if self.info_name is None:
                        self.info_name = "taipower"
                    self.info_name = self.info_name + "-" + i
            else:
                _LOGGER.error("Received error from TaiPower: %s", POWER_INFOS[i])

        return self.info_name

    async def async_update(self):
        """Async wrapper for update method."""
        return await self._hass.async_add_executor_job(self._update)

    def _update(self):
        """Get the latest data from TaiPower."""
        if self.info_name is None:
            _LOGGER.error("No TaiPower held, check logs for problems")
            return

        try:
            infos = self.get_data_for_power_info(
                self.power_info, self.data
            )
            self.infos = infos
        except (ValueError) as err:
            _LOGGER.error("Check TaiPower connection: %s", err.args)
            self.info_name = None
