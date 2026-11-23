from mapres import datamap

@datamap.braces.config(recursive=True)
class EnvironmentConfig:
    __user_config_path__ = 'config/environment.yaml'
    __default_config_path__ = 'defaultconfigs/environment.yaml'

    bridge_url: str = 'hungerbridge.url'
    bridge_token_id: str = 'hungerbridge.token_id'
    bridge_token_secret: str = 'hungerbridge.token_secret'

    ptero_enabled: bool = 'pterodactyl.enabled'
    ptero_url: str = 'pterodactyl.url'
    ptero_api_key: str = 'pterodactyl.api_key'
    ptero_server_id: str = 'pterodactyl.server_id'


class fallbacks:
    bridge_token_id = 'CHANGE_ME'
    bridge_token_secret = 'CHANGE_ME'
    bridge_url = 'https://api.example.com'

    ptero_enabled = False
    ptero_url = 'https://example.com'
    ptero_api_key = 'CHANGE_ME'
    ptero_server_id = 'CHANGE_ME'


class rules:
    bridge_token_id = 'required'
    bridge_token_secret = 'required'
    bridge_url = 'required'

    ptero_enabled = 'recommended'
    ptero_url = 'recommended'
    ptero_api_key = 'recommended'
    ptero_server_id = 'recommended'
    # everything else defaults to optional
