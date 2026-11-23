from mapres import datamap

@datamap.braces.config(recursive=True)
class DiscordConfig:
    __user_config_path__ = 'config/discord.yaml'
    __default_config_path__ = 'defaultconfigs/discord.yaml'

    discord_enabled: bool = 'discord.enabled'
    discord_token: str = 'discord.token'
    discord_url: str = 'discord.url'


class fallbacks:
    discord_enabled = True
    discord_token = 'CHANGE_ME'
    discord_url = 'https://bot.example.com/webhook'


class rules:
    discord_enabled = 'recommended'
    discord_token = 'recommended'
    discord_url = 'recommended'
    # everything else defaults to optional
