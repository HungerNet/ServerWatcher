from hungerlib import datamap, datamap_api

@datamap(syntax=datamap_api.braces, mode="config")
class GlobalConfig:
    timezone: str = "timezone"

    panel_name: str = "panel.name"
    panel_url: str = "panel.url"
    panel_api_key: str = "panel.api_key"

    origin_server_id: str = "origin.server_id"

    server_name: str = "server.name"
    server_id: str = "server.server_id"
    server_domain: str = "server.domain"
    server_port: int = "server.port"

    tps_command: str = "server.tps_command"

    bridge_token: str = "hungerbridge.token"
    bridge_port: int = "hungerbridge.port"

    enable_logging: bool = "logger.enabled"
    logger_name: str = "logger.name"
    log_path: str = "logger.log_path"

    clear_terminal: bool = "terminal.enable_clearing"
