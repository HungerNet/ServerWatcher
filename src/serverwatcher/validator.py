import sys
from dataclasses import fields

from hungerlib.addons import loadConfig

from serverwatcher.configclasses.global_config import GlobalConfig
from serverwatcher.configclasses.messages import MessagesConfig
from serverwatcher.configclasses.watcher import WatcherConfig


# -----------------------------
# Generic validation helpers
# -----------------------------

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
    """
    Validate all fields in a dataclass:
    - type correctness
    - non-negative numbers
    - non-empty strings
    """
    for f in fields(schema):
        name = f.name
        expected_type = f.type
        value = getattr(config_obj, name)

        # Type check
        validate_type(name, value, expected_type, errors)

        # String checks
        if expected_type is str:
            validate_nonempty(name, value, errors)

        # Numeric checks
        if expected_type in (int, float):
            validate_positive(name, value, errors)


# -----------------------------
# Config-specific validation
# -----------------------------

def validate_global_config(cfg, errors):
    if cfg.watch_interval < 1:
        errors.append(f"watch_interval: must be >= 1 (got {cfg.watch_interval})")

    # Example: ensure ports are valid
    if cfg.server_port <= 0 or cfg.server_port > 65535:
        errors.append(f"server_port: must be 1–65535 (got {cfg.server_port})")

    if cfg.rcon_port <= 0 or cfg.rcon_port > 65535:
        errors.append(f"rcon_port: must be 1–65535 (got {cfg.rcon_port})")


def validate_watcher_config(cfg, errors):
    if cfg.restart_wait_seconds < 1:
        errors.append(f"restart_wait_seconds: must be >= 1 (got {cfg.restart_wait_seconds})")

    if cfg.cpu_threshold <= 0:
        errors.append(f"cpu_threshold: must not be less than 1 (got {cfg.cpu_threshold})")

    if cfg.ram_threshold <= 0:
        errors.append(f"ram_threshold: must be > 0 (got {cfg.ram_threshold})")

    if cfg.tps_threshold <= 0 or cfg.tps_threshold > 20:
        errors.append(f"tps_threshold: must be 1–20 (got {cfg.tps_threshold})")


def validate_messages_config(cfg, errors):
    # Ensure all message templates contain {prefix}
    for name, value in vars(cfg).items():
        if isinstance(value, str) and "{prefix}" not in value:
            # Not required for every field, but warn if missing
            pass

def ensure_no_global_defaults(cfg, defaults):
    if cfg.panel_url == "https://example.com":
        defaults.append('panel_url')
    
    if cfg.panel_api_key == 'CHANGE_ME':
        defaults.append('panel_api_key')

    if cfg.origin_server_id == 'CHANGE_ME':
        defaults.append('origin_server_id')

    if cfg.server_id == 'CHANGE_ME':
        defaults.append('server_id')

    if cfg.server_domain == 'mc.example.com':
        defaults.append('server_domain')

    if cfg.rcon_password == 'password':
        defaults.append('rcon_password')


def ensure_no_watcher_defaults(cfg, defaults):
    if cfg.restart_soon_schedule_id == 0:
        defaults.append('restart_soon_schedule_id')

    if cfg.origin_disable_schedule_id == 0:
        defaults.append('origin_disable_schedule_id')


# -----------------------------
# Main validator
# -----------------------------

def validate_all():
    errors = []
    defaults = []

    # Load configs
    global_cfg = loadConfig("config/global.yaml", "/defaultconfigs/global.yaml", GlobalConfig)
    messages_cfg = loadConfig("config/messages.yaml", "/defaultconfigs/messages.yaml", MessagesConfig)
    watcher_cfg = loadConfig("config/watcher.yaml", "/defaultconfigs/watcher.yaml", WatcherConfig)

    # Generic dataclass validation
    validate_dataclass(global_cfg, GlobalConfig, errors)
    validate_dataclass(messages_cfg, MessagesConfig, errors)
    validate_dataclass(watcher_cfg, WatcherConfig, errors)

    # Config-specific validation
    validate_global_config(global_cfg, errors)
    validate_messages_config(messages_cfg, errors)
    validate_watcher_config(watcher_cfg, errors)

    # Check for defaults
    ensure_no_global_defaults(global_cfg, defaults)
    ensure_no_watcher_defaults(watcher_cfg, defaults)


    # Print results
    if len(defaults) >= 8:
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
