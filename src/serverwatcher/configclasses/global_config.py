from dataclasses import dataclass, field

def yaml_key(name: str):
    return field(metadata={"yaml_key": name})

@dataclass
class GlobalConfig:
    watch_interval: int = yaml_key("watch_interval")

    panel_name: str = yaml_key("panel_name")
    panel_url: str = yaml_key("panel_url")
    panel_api_key: str = yaml_key("panel_api_key")

    origin_server_id: str = yaml_key("origin_server_id")

    server_name: str = yaml_key("server_name")
    server_id: str = yaml_key("server_id")
    server_domain: str = yaml_key("server_domain")
    server_port: int = yaml_key("server_port")
    rcon_port: int = yaml_key("rcon_port")
    rcon_password: str = yaml_key("rcon_password")
    tps_command: str = yaml_key("tps_command")
    
    do_logging: bool = yaml_key("do_logging")
    logger_name: str = yaml_key("logger_name")
    log_path: str = yaml_key("log_path")
    timezone: str = yaml_key("timezone")

    console_backspaces: int = yaml_key("console_backspaces")
    clear_terminal: bool = yaml_key("clear_terminal")
