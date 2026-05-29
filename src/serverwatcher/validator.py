import sys
from dataclasses import fields

from hungerlib import utils, loadConfig, Validator

from serverwatcher.configclasses.config import GlobalConfig
from serverwatcher.configclasses.messages import MessagesConfig
from serverwatcher.configclasses.watcher import WatcherConfig


utils.clearTerminal()

v = Validator(
    throw_on_required=True,
    throw_on_type_mismatch=True,
    throw_on_fallback=True,
    throw_on_recommended=True,
)


def validate_global_config(c):
    for f in fields(GlobalConfig):
        if not f.name.startswith("__"):
            v.check_field(c, f.name)


def validate_watcher_config(c):
    for f in fields(WatcherConfig):
        if not f.name.startswith("__"):
            v.check_field(c, f.name)


def validate_messages_config(c):
    for f in fields(MessagesConfig):
        if not f.name.startswith("__"):
            v.check_field(c, f.name)


def validate_all():
    config = loadConfig(GlobalConfig)
    messages = loadConfig(MessagesConfig)
    watcher = loadConfig(WatcherConfig)

    v.validate_key_types(config, GlobalConfig)
    v.validate_key_types(messages, MessagesConfig)
    v.validate_key_types(watcher, WatcherConfig)

    validate_global_config(config)
    validate_watcher_config(watcher)
    validate_messages_config(messages)

    return v.run(config, messages, watcher)


if __name__ == '__main__':
    validate_all()
