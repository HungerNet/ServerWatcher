import sys
from dataclasses import fields

from hungerlib import utils, loadConfig, Validator

from serverwatcher.configclasses.config import GlobalConfig
from serverwatcher.configclasses.messages import MessagesConfig
from serverwatcher.configclasses.watcher import WatcherConfig


utils.clearTerminal()
v = Validator()


def validate_global_config(config):
    c = config

    # timezone
    v.check_field(c, "timezone")
    if c.timezone == "":
        v.errors.append('timezone: must not be empty')

    # panel
    v.check_field(c, "panel_name")
    v.check_field(c, "panel_url", allow_fallback=False)
    v.check_field(c, "panel_api_key", allow_fallback=False)

    if c.panel_url and not (c.panel_url.startswith("http://") or c.panel_url.startswith("https://")):
        v.errors.append(f'panel_url: must start with "http://" or "https://" (got "{c.panel_url}")')

    if c.panel_api_key and not c.panel_api_key.startswith("ptlc_"):
        v.errors.append(f'panel_api_key: must be a valid Pterodactyl client API key (got "{c.panel_api_key}")')
    if c.panel_api_key and c.panel_api_key.startswith("plta_"):
        v.errors.append(f'panel_api_key: should not be an application key (got "{c.panel_api_key}")')

    # server
    v.check_field(c, "server_name")
    v.check_field(c, "server_id", allow_fallback=False)
    v.check_field(c, "server_domain", allow_fallback=False)
    v.check_field(c, "server_port")

    if c.server_domain and (c.server_domain.startswith("http://") or c.server_domain.startswith("https://")):
        v.errors.append(f'server_domain: must not contain protocol (got "{c.server_domain}")')

    if c.server_port is not None and not (1 <= c.server_port <= 65535):
        v.errors.append(f'server_port: must be 1–65535 (got "{c.server_port}")')

    # hungerbridge
    v.check_field(c, "bridge_token", allow_fallback=False)
    v.check_field(c, "bridge_port")
    if c.bridge_port is not None and not (1 <= c.bridge_port <= 65535):
        v.errors.append(f'bridge_port: must be 1–65535 (got "{c.bridge_port}")')

    # logger
    for key in [
        "enable_logging", "logger_name", "log_path",
        "info_prefix", "warn_prefix", "error_prefix"
    ]:
        v.check_field(c, key)

    # terminal
    v.check_field(c, "clear_terminal")
    v.check_field(c, "handle_keyboard_interrupt")


def validate_watcher_config(watcherconfig):
    c = watcherconfig
    raw = c.raw
    fb = c.fallbacks

    if c.restart_wait_seconds <= 0:
        v.errors.append(f'restart_wait_seconds: must be > 0 (got {c.restart_wait_seconds})')

    if c.threshold_cpu <= 0:
        v.errors.append(f'threshold_cpu: must be > 0 (got {c.threshold_cpu})')

    if c.threshold_ram <= 0:
        v.errors.append(f'threshold_ram: must be > 0 (got {c.threshold_ram})')

    if c.threshold_tps <= 0 or c.threshold_tps > 20:
        v.errors.append(f'threshold_tps: must be 1–20 (got "{c.threshold_tps}")')

    if raw.snap_minutes is None:
        v.warnings.append(f'snap_minutes: key does not exist, using fallback "{fb.snap_minutes}"')

    if not isinstance(c.snap_minutes, list) or not c.snap_minutes:
        v.errors.append(f'snap_minutes: must be a non-empty list of minute marks (got {c.snap_minutes!r})')
    else:
        bad = [m for m in c.snap_minutes if not isinstance(m, int) or not (0 <= m <= 59)]
        if bad:
            v.errors.append(f'snap_minutes: all values must be integers 0–59 (bad values: {bad})')


def validate_messages_config(messages):
    pass # may add validation later
    # for f in fields(MessagesConfig):
    #     if f.name.startswith("__"):
    #         continue
    #     value = getattr(messages, f.name)
    #     if not isinstance(value, str) or value.strip() == "":
    #         v.errors.append(f'MessagesConfig.{f.name}: must be a non-empty string')


def validate_all():
    config = loadConfig(GlobalConfig)
    messages = loadConfig(MessagesConfig)
    watcherconfig = loadConfig(WatcherConfig)

    v.validate_key_types(config, GlobalConfig)
    v.validate_key_types(messages, MessagesConfig)
    v.validate_key_types(watcherconfig, WatcherConfig)

    validate_global_config(config)
    validate_watcher_config(watcherconfig)
    validate_messages_config(messages)

    return v.run(config, messages, watcherconfig)


if __name__ == '__main__':
    validate_all()
