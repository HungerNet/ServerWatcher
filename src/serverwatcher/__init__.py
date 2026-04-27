from importlib.metadata import version as _pkg_version, PackageNotFoundError

# Package version
try:
    __version__ = _pkg_version('serverwatcher')
except PackageNotFoundError:
    __version__ = '0.0.0'

from .watcher import ServerWatcher
from .configclasses.global_config import GlobalConfig
from .configclasses.messages import MessagesConfig
from .configclasses.watcher import WatcherConfig

__all__ = [
    'ServerWatcher',
    'GlobalConfig',
    'MessagesConfig',
    'WatcherConfig',
]
