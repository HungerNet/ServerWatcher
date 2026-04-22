# src/hungerlib/api/command.py

class CommandAPI:
    """
    Raw command endpoint.
    """

    def __init__(self, panel):
        self.panel = panel

    def send(self, server_id, command):
        return self.panel.post(
            f"/api/client/servers/{server_id}/command",
            json={"command": command}
        )
