from mapres import datamap

@datamap.braces.config(recursive=True)
class GlobalConfig:
    __user_config_path__ = 'config/config.yaml'
    __default_config_path__ = 'defaultconfigs/config.yaml'

    debug: bool = 'debug'
    timezone: str = 'timezone'

    server_name: str = 'server.name'
    server_domain: str = 'server.domain'
    server_port: int = 'server.port'

    enable_logging: bool = 'logger.enabled'
    logger_name: str = 'logger.name'
    log_path: str = 'logger.log_path'

    info_prefix: str = 'logger.prefixes.info'
    warn_prefix: str = 'logger.prefixes.warn'
    error_prefix: str = 'logger.prefixes.error'
    fatal_prefix: str = 'logger.prefixes.fatal'
    debug_prefix: str = 'logger.prefixes.debug'

    clear_terminal: bool = 'terminal.enable_clearing'
    handle_keyboard_interrupt: bool = 'terminal.handle_keyboard_interrupt'


class fallbacks:
    debug = False
    timezone = 'America/Chicago'

    server_name = 'My SMP'
    server_domain = 'mc.example.com'
    server_port = 25565

    enable_logging = True
    logger_name = 'Server Watcher'
    log_path = '/home/container/logs/'

    info_prefix = '<white>[%hh%:%mm%:%ss%] [INFO]: '
    warn_prefix = '<yellow>[%hh%:%mm%:%ss%] [WARN]: '
    error_prefix = '<red>[%hh%:%mm%:%ss%] [ERROR]: '
    fatal_prefix = '<dark_red>[%hh%:%mm%:%ss%] [FATAL]: '
    debug_prefix = '<aqua>[%hh%:%mm%:%ss%] [DEBUG]: '

    clear_terminal = True
    handle_keyboard_interrupt = True


class rules:
    pass # everything defaults to optional
