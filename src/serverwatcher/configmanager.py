from typing import Any
import os
import shutil
from dataclasses import fields

from hungerlib import utils, loadConfig, Validator

from serverwatcher.configclasses.config import GlobalConfig
from serverwatcher.configclasses.discord import DiscordConfig
from serverwatcher.configclasses.environment import EnvironmentConfig
from serverwatcher.configclasses.evaluation import EvaluatorConfig
from serverwatcher.configclasses.watcher import WatcherConfig


class ConfigManager:
    def __init__(self):
        utils.clearTerminal()
        self.validator = Validator()

        self.config = loadConfig(GlobalConfig)
        self.discordcfg = loadConfig(DiscordConfig)
        self.env = loadConfig(EnvironmentConfig)
        self.evaluatorcfg = loadConfig(EvaluatorConfig)
        self.watchercfg = loadConfig(WatcherConfig)

        self.ALL_CONFIG_CLASSES: list[Any] = [
            GlobalConfig,
            DiscordConfig,
            EnvironmentConfig,
            EvaluatorConfig,
            WatcherConfig
        ]

        self.ALL_LOADED_CONFIGS: list[Any] = [
            self.config,
            self.discordcfg,
            self.env,
            self.evaluatorcfg,
            self.watchercfg,
        ]

        self.CONFIG_DICT: dict[Any] = {
            GlobalConfig: self.config,
            DiscordConfig: self.discordcfg,
            EnvironmentConfig: self.env,
            EvaluatorConfig: self.evaluatorcfg,
            WatcherConfig: self.watchercfg
        }



    # existence checking
    def checkExistence(self, *config_classes):
        for cls in config_classes:
            user_path: Any | None = getattr(cls, '__user_config_path__', None)
            if not user_path or not os.path.exists(user_path):
                return False
        return True

    def checkAllExistence(self):
        return self.checkExistence(*self.ALL_CONFIG_CLASSES)

    # config generation
    def generateConfigs(self, overwrite=False, *config_classes):
        for cls in config_classes:
            user_path: Any | None = getattr(cls, '__user_config_path__', None)
            default_path: Any | None = getattr(cls, '__default_config_path__', None)

            if not user_path or not default_path:
                continue

            if os.path.exists(user_path) and not overwrite:
                continue

            os.makedirs(os.path.dirname(user_path), exist_ok=True)
            shutil.copy(default_path, user_path)

    def generateAllConfigs(self, overwrite=False):
        self.generateConfigs(overwrite, *self.ALL_CONFIG_CLASSES)

    # validation helpers
    def _validate_fields(self, config_obj, config_cls):
        for f in fields(config_cls):
            if not f.name.startswith('__'):
                self.validator.check_field(config_obj, f.name)

    # validation rules
    def validate_config(self):
        c = self.config
        self._validate_fields(c, GlobalConfig)

    def validate_discordcfg(self):
        c = self.discordcfg
        self._validate_fields(c, DiscordConfig)

        if c.discord_enabled:
            if c.discord_token == 'CHANGE_ME':
                self.validator.errors.append('discord_token: must be configured (got "CHANGE_ME")')
            if c.discord_url == 'https://bot.example.com/webhook':
                self.validator.errors.append('discord_url: must be configured (got placeholder URL)')

    def validate_env(self):
        c = self.env
        self._validate_fields(c, EnvironmentConfig)

        if c.bridge_url == 'https://api.example.com':
            self.validator.errors.append('bridge_url: must be configured (got placeholder URL)')
        if c.bridge_token_id == 'CHANGE_ME':
            self.validator.errors.append('bridge_token_id: must be configured (got "CHANGE_ME")')
        if c.bridge_token_secret == 'CHANGE_ME':
            self.validator.errors.append('bridge_token_secret: must be configured (got "CHANGE_ME")')

        if c.ptero_enabled:
            if c.ptero_url == 'https://example.com':
                self.validator.errors.append('ptero_url: must be configured (got placeholder URL)')
            if c.ptero_api_key == 'CHANGE_ME':
                self.validator.errors.append('ptero_api_key: must be configured (got "CHANGE_ME")')
            if c.ptero_server_id == 'CHANGE_ME':
                self.validator.errors.append('ptero_server_id: must be configured (got "CHANGE_ME")')

    def validate_watchercfg(self):
        c = self.watchercfg
        self._validate_fields(c, WatcherConfig)

    # full validation
    def validateAll(self):
        # type validation
        for config_cls, config_obj in self.CONFIG_DICT.items():
            self.validator.validate_key_types(config_obj, config_cls)

        # field validation
        self.validate_config()
        self.validate_discordcfg()
        self.validate_env()
        self.validate_watchercfg()

        # return final validation result
        return self.validator.run(
            self.config,
            self.discordcfg,
            self.env,
            self.evaluatorcfg,
            self.watchercfg
        )

config_manager = ConfigManager()
