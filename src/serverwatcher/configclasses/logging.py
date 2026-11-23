from mapres import datamap

@datamap.braces.config(recursive=True)
class LoggingConfig:
    __user_config_path__ = 'config/config.yaml'
    __default_config_path__ = 'defaultconfigs/config.yaml'

    logger_name: str = 'logger.name'
    log_path: str = 'logger.log_path'

    enable_terminal_clearing: bool = 'terminal.enable_clearing'
    handle_keyboard_interrupt: bool = 'terminal.handle_keyboard_interrupt'

    debug: bool = 'debug'
    timezone: str = 'timezone'