from importlib.metadata import version as _pkg_version, PackageNotFoundError

# Package version
try:
    __version__ = _pkg_version('serverwatcher')
except PackageNotFoundError:
    __version__ = '0.0.0'

from .watcher import ServerWatcher
from .config import WatcherConfig
from .messages import WatcherMessages


__all__ = [
    # core utilities
    'ServerWatcher',
    'WatcherConfig',
    'WatcherMessages',
]
