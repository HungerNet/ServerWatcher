from importlib.metadata import version as _pkg_version, PackageNotFoundError

# Package version
try:
    __version__ = _pkg_version("hungerlib")
except PackageNotFoundError:
    __version__ = "0.0.0"

# --- Core modules ---
from .panel import Panel
from .logger import HungerLogger

# --- API endpoints ---
from .api.schedule import ScheduleAPI
from .api.filemanager import FileManagerAPI
from .api.backups import BackupsAPI
from .api.databases import DatabasesAPI
from .api.startup import StartupAPI

__all__ = [
    "__version__",

    # core utilities
    "Panel",
    "HungerLogger",

    # API endpoints
    "ScheduleAPI",
    "FileManagerAPI",
    "BackupsAPI",
    "DatabasesAPI",
    "StartupAPI",
]
