from mapres import datamap

@datamap.braces.config(recursive=True)
class GlobalConfig:
    __user_config_path__ = 'config/config.yaml'
    __default_config_path__ = 'defaultconfigs/config.yaml'

    server_name: str = 'server.name'
    server_domain: str = 'server.domain'
    server_port: int = 'server.port'

    panel_url: str = 'calagopus.url'
    panel_api_key: str = 'calagopus.api_key'
    server_id: str = 'calagopus.server_id'

    bridge_url: str = 'hungerbridge.url'
    bridge_token_id: str = 'hungerbridge.token_id'
    bridge_token_secret: str = 'hungerbridge.token_secret'
