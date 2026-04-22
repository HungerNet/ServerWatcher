class ScheduleAPI:
    """
    Raw schedule endpoints.
    No logic. No models. No convenience.
    """

    def __init__(self, panel):
        self.panel = panel

    def list(self, server_id):
        return self.panel.get(f"/api/client/servers/{server_id}/schedules")

    def create(self, server_id, payload):
        return self.panel.post(f"/api/client/servers/{server_id}/schedules", json=payload)

    def update(self, server_id, schedule_id, payload):
        # Your panel uses POST for full updates
        return self.panel.post(
            f"/api/client/servers/{server_id}/schedules/{schedule_id}",
            json=payload
        )

    def delete(self, server_id, schedule_id):
        return self.panel.delete(f"/api/client/servers/{server_id}/schedules/{schedule_id}")

    def run(self, server_id, schedule_id):
        return self.panel.post(
            f"/api/client/servers/{server_id}/schedules/{schedule_id}/execute"
        )
