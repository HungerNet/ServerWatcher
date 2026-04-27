from dataclasses import dataclass

@dataclass
class GlobalConfig:
    watch_interval: int

    panel_name: str
    panel_url: str
    panel_api_key: str

    origin_server_id: str

    server_name: str
    server_id: str
    server_domain: str
    server_port: int
    rcon_port: int
    rcon_password: str
    tps_command: str
    
    do_logging: bool
    logger_name: str
    log_path: str
    timezone: str

    console_backspaces: int
    clear_terminal: bool