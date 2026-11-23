from calagoapi import Panel
from calagoapi.utils.exceptions import CalagoAPIError
from .settings import settings


def setupServer():
    panel = Panel(url=settings.config.panel_url, api_key=settings.config.panel_api_key)

    if not panel.ping():
        raise CalagoAPIError(f'Panel unreachable: {settings.config.panel_url}')
    if not panel.validateAPI():
        raise CalagoAPIError('Invalid panel API key')

    # wrap this in some kind of validation
    server = panel.minecraft.getServer(
        server_id = settings.config.server_id,
        address = settings.config.bridge_url
    )

    return panel, server
