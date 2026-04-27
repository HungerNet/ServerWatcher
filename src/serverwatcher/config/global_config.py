from dataclasses import dataclass

@dataclass
class GlobalConfig:
    panel_name: str
    panel_url: str
    panel_api_key: str

    origin_server_id: str

    server_name: str
    server_server_id: str
    server_domain: str
    server_port: int
    server_rcon_port: int
    server_rcon_password: str
    server_tps_command: str
