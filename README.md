# ServerWatcher

A configurable server monitoring and restart engine for HungerLib / Pterodactyl-based Minecraft servers.

## Usage
```bash
pip install serverwatcher
```
```python
from serverwatcher.watcher import ServerWatcher
from serverwatcher.config import WatcherConfig
from serverwatcher.messages import WatcherMessages

watcher = ServerWatcher(server, origin, panel, logger, WatcherConfig(), WatcherMessages())
watcher.evaluate()
```