import sys
from dataclasses import fields

from hungerlib import utils, loadConfig

from serverwatcher.configclasses.config import GlobalConfig
from serverwatcher.configclasses.messages import MessagesConfig
from serverwatcher.configclasses.watcher import WatcherConfig


utils.clearTerminal()
errors = []
warnings = []
defaults = []


def validate_key_types(config_obj, schema):
    for f in fields(schema):
        if f.name.startswith("__"):
            continue

        expected_type = f.type
        value = getattr(config_obj, f.name, None)

        # allow None (missing + no fallback) to be handled by other validators
        if value is None:
            continue

        if not isinstance(value, expected_type):
            errors.append(
                f'{schema.__name__}.{f.name}: expected {expected_type.__name__}, '
                f'got "{type(value).__name__}" ({value!r})'
            )


def check_field(config_obj, name, allow_fallback=True):
    """
    Unified check for:
    - missing YAML key (config.raw.<name> is None)
    - fallback usage (config.<name> == config.fallbacks.<name>)
    - whether fallback is allowed or not
    """
    raw = config_obj.raw
    fb = config_obj.fallbacks

    val = getattr(config_obj, name)
    raw_val = getattr(raw, name)
    fb_val = getattr(fb, name)

    # 1) YAML key missing
    if raw_val is None:
        if allow_fallback:
            warnings.append(f'{name}: key does not exist, using fallback "{fb_val}"')
        else:
            errors.append(f'{name}: key does not exist and fallback is not allowed')
        return

    # 2) YAML key exists but value equals fallback
    if val == fb_val and not allow_fallback:
        defaults.append(f'{name}: must not be left default or empty (got "{val}")')


def validate_global_config(config):
    c = config

    # Fallback policy:
    # - NOT allowed (must be set by user): panel_url, panel_api_key,
    #   server_id, server_domain, bridge_token
    # - Allowed: everything else

    # timezone
    check_field(c, "timezone")
    if c.timezone == "":
        errors.append('timezone: must not be empty')

    # panel
    check_field(c, "panel_name")
    check_field(c, "panel_url", allow_fallback=False)
    check_field(c, "panel_api_key", allow_fallback=False)

    if c.panel_url and not (c.panel_url.startswith("http://") or c.panel_url.startswith("https://")):
        errors.append(f'panel_url: must start with "http://" or "https://" (got "{c.panel_url}")')

    if c.panel_api_key and not c.panel_api_key.startswith("ptlc_"):
        errors.append(f'panel_api_key: must be a valid Pterodactyl client API key (got "{c.panel_api_key}")')
    if c.panel_api_key and c.panel_api_key.startswith("plta_"):
        errors.append(f'panel_api_key: should not be an application key (got "{c.panel_api_key}")')

    # server
    check_field(c, "server_name")
    check_field(c, "server_id", allow_fallback=False)
    check_field(c, "server_domain", allow_fallback=False)
    check_field(c, "server_port")
    if c.server_domain and (c.server_domain.startswith("http://") or c.server_domain.startswith("https://")):
        errors.append(f'server_domain: must not contain protocol (got "{c.server_domain}")')
    if c.server_port is not None and not (1 <= c.server_port <= 65535):
        errors.append(f'server_port: must be 1–65535 (got "{c.server_port}")')

    # tps_command
    check_field(c, "tps_command")

    # hungerbridge
    check_field(c, "bridge_token", allow_fallback=False)
    check_field(c, "bridge_port")
    if c.bridge_port is not None and not (1 <= c.bridge_port <= 65535):
        errors.append(f'bridge_port: must be 1–65535 (got "{c.bridge_port}")')

    # logger
    check_field(c, "enable_logging")
    check_field(c, "logger_name")
    check_field(c, "log_path")
    check_field(c, "info_prefix")
    check_field(c, "warn_prefix")
    check_field(c, "error_prefix")

    # terminal
    check_field(c, "clear_terminal")
    check_field(c, "handle_keyboard_interrupt")


def validate_watcher_config(watcherconfig):
    c = watcherconfig
    raw = c.raw
    fb = c.fallbacks

    # basic numeric sanity
    if c.restart_wait_seconds <= 0:
        errors.append(f'restart_wait_seconds: must be > 0 (got {c.restart_wait_seconds})')

    if c.threshold_cpu <= 0:
        errors.append(f'threshold_cpu: must be > 0 (got {c.threshold_cpu})')

    if c.threshold_ram <= 0:
        errors.append(f'threshold_ram: must be > 0 (got {c.threshold_ram})')

    if c.threshold_tps <= 0 or c.threshold_tps > 20:
        errors.append(f'threshold_tps: must be 1–20 (got {c.threshold_tps})')

    # snap_minutes: must be a non-empty list of ints 0–59
    if raw.snap_minutes is None:
        warnings.append(f'snap_minutes: key does not exist, using fallback "{fb.snap_minutes}"')

    if not isinstance(c.snap_minutes, list) or not c.snap_minutes:
        errors.append(f'snap_minutes: must be a non-empty list of minute marks (got {c.snap_minutes!r})')
    else:
        bad = [m for m in c.snap_minutes if not isinstance(m, int) or not (0 <= m <= 59)]
        if bad:
            errors.append(f'snap_minutes: all values must be integers 0–59 (bad values: {bad})')


def validate_messages_config(messages):
    pass
    # m = messages

    # for f in fields(MessagesConfig):
    #     if f.name.startswith("__"):
    #         continue
    #     value = getattr(m, f.name)
    #     if not isinstance(value, str) or value.strip() == "":
    #         errors.append(f'MessagesConfig.{f.name}: must be a non-empty string')


def validate_all():
    config = loadConfig(GlobalConfig)
    messages = loadConfig(MessagesConfig)
    watcherconfig = loadConfig(WatcherConfig)

    # type checks
    validate_key_types(config, GlobalConfig)
    validate_key_types(messages, MessagesConfig)
    validate_key_types(watcherconfig, WatcherConfig)

    # semantic checks
    validate_global_config(config)
    validate_watcher_config(watcherconfig)
    validate_messages_config(messages)

    # if too many critical defaults, assume "not configured at all"
    critical_default_keys = [
        "panel_url",
        "panel_api_key",
        "server_id",
        "server_domain",
        "bridge_token",
    ]
    critical_defaults_used = [
        d for d in defaults
        if any(d.startswith(k) for k in critical_default_keys)
    ]

    if len(critical_defaults_used) >= 3:
        print('❌ CONFIG VALIDATION FAILED:\nIt looks like you haven\'t configured this yet! Please change these defaults:')
        for d in critical_defaults_used:
            print(' -', d)
        sys.exit(1)

    if errors or defaults:
        print('❌ CONFIG VALIDATION FAILED:')
        for e in errors:
            print(' -', e)
        for d in defaults:
            print(' -', d)
        if warnings:
            print('\nWarnings:')
            for w in warnings:
                print(' -', w)
        sys.exit(1)

    if warnings:
        print('⚠️  CONFIG VALIDATION WARNINGS:')
        for w in warnings:
            print(' -', w)

    print('✅ All configs are valid.')


if __name__ == '__main__':
    validate_all()
