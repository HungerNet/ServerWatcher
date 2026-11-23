from importlib.metadata import version as _pkg_version, PackageNotFoundError

# Package version
try:
    __version__ = _pkg_version('serverwatcher')
except PackageNotFoundError:
    __version__ = '0.0.0'

from serverwatcher.watcher import ServerWatcher
from serverwatcher.configclasses.config import GlobalConfig
from serverwatcher.configclasses.watcher import WatcherConfig

__all__: list[str] = [
    'ServerWatcher',
    'GlobalConfig',
    'WatcherConfig',
]
