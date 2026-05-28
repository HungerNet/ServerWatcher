from mapres import datamap, syntax

@datamap(syntax=syntax.braces, mode='config')
class GlobalConfig:
    __user_config_path__ = 'config/config.yaml'
    __default_config_path__ = 'defaultconfigs/config.yaml'

    timezone: str = 'timezone'

    panel_name: str = 'panel.name'
    panel_url: str = 'panel.url'
    panel_api_key: str = 'panel.api_key'

    server_name: str = 'server.name'
    server_id: str = 'server.server_id'
    server_domain: str = 'server.domain'
    server_port: int = 'server.port'

    bridge_token: str = 'hungerbridge.token'
    bridge_port: int = 'hungerbridge.port'

    enable_logging: bool = 'logger.enabled'
    logger_name: str = 'logger.name'
    log_path: str = 'logger.log_path'

    info_prefix: str = 'logger.prefixes.info'
    warn_prefix: str = 'logger.prefixes.warn'
    error_prefix: str = 'logger.prefixes.error'

    clear_terminal: bool = 'terminal.enable_clearing'
    handle_keyboard_interrupt: bool = 'terminal.handle_keyboard_interrupt'


class fallbacks:
    timezone = 'America/Chicago'

    panel_name = 'My Panel'
    panel_url = 'https://example.com'
    panel_api_key = 'CHANGE_ME'

    server_name = 'My SMP'
    server_id = 'CHANGE_ME'
    server_domain = 'mc.example.com'
    server_port = 25565

    bridge_token = 'CHANGE_ME'
    bridge_port = 1913

    enable_logging = True
    logger_name = 'Server Watcher'
    log_path = '/home/container/logs/'

    info_prefix = '<white>[INFO]: '
    warn_prefix = '<yellow>[WARN]: '
    error_prefix = '<red>[ERROR]: '

    clear_terminal = True
    handle_keyboard_interrupt = True


class rules:
    panel_url = "required"
    panel_api_key = "required"
    server_id = "required"
    server_domain = "required"
    bridge_token = "required"

    timezone = "recommended"
    panel_name = "recommended"
    server_port = "recommended"
    bridge_port = "recommended"

    # everything else defaults to optional
