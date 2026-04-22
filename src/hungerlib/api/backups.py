class BackupsAPI:
    """
    Raw backups endpoints.
    """

    def __init__(self, panel):
        self.panel = panel

    def list(self, server_id):
        return self.panel.get(f"/api/client/servers/{server_id}/backups")

    def create(self, server_id, name="Auto Backup"):
        return self.panel.post(
            f"/api/client/servers/{server_id}/backups",
            json={"name": name}
        )

    def delete(self, server_id, backup_id):
        return self.panel.delete(
            f"/api/client/servers/{server_id}/backups/{backup_id}"
        )

    def download(self, server_id, backup_id):
        return self.panel.get(
            f"/api/client/servers/{server_id}/backups/{backup_id}/download"
        )
