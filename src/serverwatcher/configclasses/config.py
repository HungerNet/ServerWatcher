from dataclasses import field
from hungerlib.datamap import datamap, Syntax

def yaml_key(path: str, default=None):
    return field(default=default, metadata={"yaml_key": path})

@datamap(syntax=Syntax.braces)
class GlobalConfig:
    timezone: str = yaml_key("timezone")

    panel_name: str = yaml_key("panel.name")
    panel_url: str = yaml_key("panel.url")
    panel_api_key: str = yaml_key("panel.api_key")

    origin_server_id: str = yaml_key("origin.server_id")

    server_name: str = yaml_key("server.name")
    server_id: str = yaml_key("server.server_id")
    server_domain: str = yaml_key("server.domain")
    server_port: int = yaml_key("server.port")

    rcon_port: int = yaml_key("server.rcon_port")
    rcon_password: str = yaml_key("server.rcon_password")
    tps_command: str = yaml_key("server.tps_command")

    enable_logging: bool = yaml_key("logger.enabled")
    logger_name: str = yaml_key("logger.name")
    log_path: str = yaml_key("logger.log_path")

    console_backspaces: int = yaml_key("terminal.backspaces")
    clear_terminal: bool = yaml_key("terminal.enable_clearing")
