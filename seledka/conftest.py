
import logging
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from seledka.logger import Logger


log = logging.getLogger(__name__)


# --------------------------------------------------------------------------- #
#                                ATTRIBUTES
# --------------------------------------------------------------------------- #
def pytest_configure(config):
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    logging.getLogger("requests").setLevel(logging.WARNING)
    config.pluginmanager.register(Logger(), "logger")
