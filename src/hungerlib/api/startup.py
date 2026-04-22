class StartupAPI:
    """
    Raw startup variable endpoints.
    """

    def __init__(self, panel):
        self.panel = panel

    def list(self, server_id):
        return self.panel.get(f"/api/client/servers/{server_id}/startup")

    def update(self, server_id, key, value):
        return self.panel.post(
            f"/api/client/servers/{server_id}/startup/variable",
            json={"key": key, "value": value}
        )
