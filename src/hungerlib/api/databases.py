class DatabasesAPI:
    """
    Raw database endpoints.
    """

    def __init__(self, panel):
        self.panel = panel

    def list(self, server_id):
        return self.panel.get(f"/api/client/servers/{server_id}/databases")

    def create(self, server_id, name, remote="%", host=None):
        payload = {"database": name, "remote": remote}
        if host:
            payload["host"] = host
        return self.panel.post(
            f"/api/client/servers/{server_id}/databases",
            json=payload
        )

    def rotate_password(self, server_id, db_id):
        return self.panel.post(
            f"/api/client/servers/{server_id}/databases/{db_id}/rotate-password"
        )

    def delete(self, server_id, db_id):
        return self.panel.delete(
            f"/api/client/servers/{server_id}/databases/{db_id}"
        )
