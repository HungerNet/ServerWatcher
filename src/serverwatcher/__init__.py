from importlib.metadata import version as _pkg_version, PackageNotFoundError

# Package version
try:
    __version__ = _pkg_version('serverwatcher')
except PackageNotFoundError:
    __version__ = '0.0.0'

from .watcher import ServerWatcher
from .schema import validate_config_schema, validate_messages_schema flatten_nested


__all__ = [
    # core utilities
    'ServerWatcher',
    'validate_config_schema',
    'validate_messages_schema',
    'flatten_nested',
]
