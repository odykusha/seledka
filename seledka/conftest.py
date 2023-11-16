
import logging
import urllib3

from seledka.logger import Logger


# --------------------------------------------------------------------------- #
#                                ATTRIBUTES
# --------------------------------------------------------------------------- #
def pytest_configure(config):
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    logging.getLogger("requests").setLevel(logging.WARNING)
    config.pluginmanager.register(Logger(), "logger")
