from hungerlib import datamap, datamap_api

@datamap(syntax=datamap_api.braces, mode='config')
class GlobalConfig:
    __user_config_path__ = 'config/config.yaml'
    __default_config_path__ = 'defaultconfigs/config.yaml'

    timezone: str = ('timezone', 'America/Chicago')

    panel_name: str = ('panel.name', 'My Panel')
    panel_url: str = ('panel.url', 'https://example.com')
    panel_api_key: str = ('panel.api_key', 'CHANGE_ME')

    origin_server_id: str = ('origin.server_id', 'CHANGE_ME')

    server_name: str = ('server.name', 'My SMP')
    server_id: str = ('server.server_id', 'CHANGE_ME')
    server_domain: str = ('server.domain', 'mc.example.com')
    server_port: int = ('server.port', 25565)

    tps_command: str = ('server.tps_command', 'ticks')

    bridge_token: str = ('hungerbridge.token', 'CHANGE_ME')
    bridge_port: int = ('hungerbridge.port', 1913)

    enable_logging: bool = ('logger.enabled', True)
    logger_name: str = ('logger.name', 'Server Watcher')
    log_path: str = ('logger.log_path', '/home/container/logs/')

    info_prefix: str = ('logger.prefixes.info', '<white>[INFO]: ')
    warn_prefix: str = ('logger.prefixes.warn', '<yellow>[WARN]: ')
    error_prefix: str = ('logger.prefixes.error', '<red>[ERROR]: ')

    clear_terminal: bool = ('terminal.enable_clearing', True)
