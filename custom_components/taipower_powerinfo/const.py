"""Constants for TaiPower Power Info Integration."""
from datetime import timedelta

DOMAIN = "taipower_powerinfo"

DEFAULT_NAME = "Power Info"
ATTRIBUTION = "Data provided by the TaiPower"
ATTR_PUBLISH_TIME = "publish_time"
ATTR_CURRENT_LOAD = "curr_load"
ATTR_CURRENT_RATE = "curr_util_rate"
ATTR_MAX_CAPACITY = "fore_maxi_sply_capacity"
ATTR_PEAK_HOUR_RANGE = "fore_peak_hour_range"
ATTR_PEAK_DEMA_LOAD = "fore_peak_dema_load"
ATTR_PEAK_INDICATOR = "fore_peak_resv_indicator"
CONF_POWER_INFO = "power_info"
CONFIG_FLOW_VERSION = 1
UPDATE_LISTENER = "update_listener"
PLATFORMS = ["sensor"]

DEFAULT_SCAN_INTERVAL = timedelta(minutes=10)

POWER_INFOS_DATA = "power_infos_data"
POWER_INFOS_COORDINATOR = "power_infos_coordinator"
POWER_INFOS_MONITORED_CONDITIONS = "power_infos_monitored_conditions"
POWER_INFOS_NAME = "power_infos_name"

USER_AGENT = ""
HA_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36 OPR/38.0.2220.41"
BASE_URL = 'https://www.taipower.com.tw/d006/loadGraph/loadGraph/data/{}'

REQUEST_TIMEOUT = 10  # seconds

POWER_INFOS = {
    "load_briefing3": "\u4eca\u65e5\u96fb\u529b\u8cc7\u8a0a",
#    "genshx_": "\u53f0\u96fb\u7cfb\u7d71\u5404\u6a5f\u7d44\u767c\u96fb\u91cf",
}

INFO_WRAPPER = {
    "load_briefing3": "loadpara.json",
    "genshx_": "reserve_forecast.txt",
    "load_forecast_": ""
}