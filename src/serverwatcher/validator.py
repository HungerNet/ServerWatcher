import sys
from dataclasses import fields

from hungerlib import utils, loadConfig, Validator

from .configclasses.config import GlobalConfig
from .configclasses.messages import MessagesConfig
from .configclasses.watcher import WatcherConfig


utils.clearTerminal()

v = Validator()


def validate_global_config(c):
    for f in fields(GlobalConfig):
        if not f.name.startswith('__'):
            v.check_field(c, f.name)

    # --- URL validation ---
    if c.discord_enabled:
        url = c.discord_url.strip()

        if not url.startswith('https://'):
            v.errors.append(f'discord_url: must start with https:// (got "{url}")')

        # optional: detect example.com placeholder
        if 'example.com' in url:
            v.errors.append(f'discord_url: placeholder URL detected ("{url}")')
        
        if c.discord_token == 'CHANGE_ME':
            v.errors.append('discord_token: must be configured (got "CHANGE_ME")')


def validate_watcher_config(c):
    for f in fields(WatcherConfig):
        if not f.name.startswith('__'):
            v.check_field(c, f.name)


def validate_messages_config(c):
    for f in fields(MessagesConfig):
        if not f.name.startswith('__'):
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
