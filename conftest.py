
import logging
from .logger import Logger

log = logging.getLogger(__name__)


# --------------------------------------------------------------------------- #
#                                ATTRIBUTES
# --------------------------------------------------------------------------- #
def pytest_configure(config):
    config.pluginmanager.register(Logger(), "logger")
