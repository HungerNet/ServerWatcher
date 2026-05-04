import sys
from dataclasses import fields
from hungerlib import loadConfig, clearTerminal

from serverwatcher.configclasses.config import GlobalConfig
from serverwatcher.configclasses.messages import MessagesConfig
from serverwatcher.configclasses.watcher import WatcherConfig

clearTerminal()

def deep_get_attr(obj, dotted):
    parts = dotted.split(".")
    cur = obj
    for p in parts:
        if not hasattr(cur, p):
            return None
        cur = getattr(cur, p)
    return cur

def validate_type(name, value, expected_type, errors):
    if not isinstance(value, expected_type):
        errors.append(f"{name}: expected {expected_type.__name__}, got {type(value).__name__}")

def validate_positive(name, value, errors):
    if isinstance(value, (int, float)) and value < 0:
        errors.append(f"{name}: must be >= 0 (got {value})")

def validate_nonempty(name, value, errors):
    if isinstance(value, str) and value.strip() == "":
        errors.append(f"{name}: cannot be empty")

def validate_dataclass(config_obj, schema, errors):
    for f in fields(schema):
        name = f.name
        expected_type = f.type
        value = deep_get_attr(config_obj, name)

        validate_type(name, value, expected_type, errors)

        if expected_type is str:
            validate_nonempty(name, value, errors)

        if expected_type in (int, float):
            validate_positive(name, value, errors)

def validate_global_config(config, errors):
    if config.server_port <= 0 or config.server_port > 65535:
        errors.append(f"server_port: must be 1–65535 (got {config.server_port})")

    if config.rcon_port <= 0 or config.rcon_port > 65535:
        errors.append(f"rcon_port: must be 1–65535 (got {config.rcon_port})")

def validate_watcher_config(watcherconfig, errors):
    if watcherconfig.restart_wait_seconds < 1:
        errors.append(f"restart_wait_seconds: must be >= 1 (got {watcherconfig.restart_wait_seconds})")

    if watcherconfig.threshold_cpu <= 0:
        errors.append(f"threshold_cpu: must not be less than 1 (got {watcherconfig.threshold_cpu})")

    if watcherconfig.threshold_ram <= 0:
        errors.append(f"threshold_ram: must be > 0 (got {watcherconfig.threshold_ram})")

    if watcherconfig.threshold_tps <= 0 or watcherconfig.threshold_tps > 20:
        errors.append(f"threshold_tps: must be 1–20 (got {watcherconfig.threshold_tps})")

def validate_messages_config(messages, errors):
    for name, value in vars(messages).items():
        if isinstance(value, str) and "{prefix}" not in value:
            pass

def ensure_no_global_defaults(config, defaults):
    if config.panel_url == "https://example.com":
        defaults.append('panel_url')
    
    if config.panel_api_key == 'CHANGE_ME':
        defaults.append('panel_api_key')

    if config.origin_server_id == 'CHANGE_ME':
        defaults.append('origin_server_id')

    if config.server_id == 'CHANGE_ME':
        defaults.append('server_id')

    if config.server_domain == 'mc.example.com':
        defaults.append('server_domain')

    if config.rcon_password == 'password':
        defaults.append('rcon_password')

def ensure_no_watcher_defaults(watcherconfig, defaults):
    if watcherconfig.schedule_control and watcherconfig.restart_soon_id == 0:
        defaults.append('restart_soon_id')

def validate_all():
    errors = []
    defaults = []

    config = loadConfig("config/config.yaml", "/defaultconfigs/config.yaml", GlobalConfig)
    messages = loadConfig("config/messages.yaml", "/defaultconfigs/messages.yaml", MessagesConfig)
    watcher = loadConfig("config/watcher.yaml", "/defaultconfigs/watcher.yaml", WatcherConfig)

    validate_dataclass(config, GlobalConfig, errors)
    validate_dataclass(messages, MessagesConfig, errors)
    validate_dataclass(watcher, WatcherConfig, errors)

    validate_global_config(config, errors)
    validate_messages_config(messages, errors)
    validate_watcher_config(watcher, errors)

    ensure_no_global_defaults(config, defaults)
    ensure_no_watcher_defaults(watcher, defaults)

    if len(defaults) >= 5:
        print("❌ CONFIG VALIDATION FAILED:\nIt looks like you haven't configured this yet! Please change these defaults:")
        for d in defaults:
            print(" -", d)
        sys.exit(1)

    if errors or defaults:
        print("❌ CONFIG VALIDATION FAILED:")
        for e in errors:
            print(" -", e)
        for d in defaults:
            print(" -", d, ": must not be left default")
        sys.exit(1)

    print("✅ All configs are valid.")

if __name__ == "__main__":
    validate_all()
