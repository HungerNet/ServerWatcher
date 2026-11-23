from mapres import loadConfig

from serverwatcher.configclasses.config import GlobalConfig
from serverwatcher.configclasses.evaluation import EvaluatorConfig
from serverwatcher.configclasses.logging import LoggingConfig
from serverwatcher.configclasses.messages import MessagesConfig
from serverwatcher.configclasses.watcher import WatcherConfig


class SettingsManager:
    def __init__(self):
        self.config = loadConfig(GlobalConfig)
        self.evaluation = loadConfig(EvaluatorConfig)
        self.logging = loadConfig(LoggingConfig)
        self.messages = loadConfig(MessagesConfig)
        self.watcher = loadConfig(WatcherConfig)

settings = SettingsManager()
