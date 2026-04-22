class FileManagerAPI:
    """
    Raw file manager endpoints.
    """

    def __init__(self, panel):
        self.panel = panel

    def list(self, server_id, directory="/"):
        return self.panel.get(
            f"/api/client/servers/{server_id}/files/list?directory={directory}"
        )

    def download(self, server_id, file_path):
        return self.panel.get(
            f"/api/client/servers/{server_id}/files/download?file={file_path}"
        )

    def upload(self, server_id, directory, file_data):
        return self.panel._raw_upload(
            f"/api/client/servers/{server_id}/files/upload",
            file_data
        )

    def delete(self, server_id, root, files):
        return self.panel.post(
            f"/api/client/servers/{server_id}/files/delete",
            json={"root": root, "files": files}
        )

    def rename(self, server_id, root, files):
        return self.panel.post(
            f"/api/client/servers/{server_id}/files/rename",
            json={"root": root, "files": files}
        )

    def copy(self, server_id, root, files):
        return self.panel.post(
            f"/api/client/servers/{server_id}/files/copy",
            json={"root": root, "files": files}
        )

    def move(self, server_id, root, files):
        return self.panel.post(
            f"/api/client/servers/{server_id}/files/move",
            json={"root": root, "files": files}
        )

    def create_folder(self, server_id, directory, name):
        return self.panel.post(
            f"/api/client/servers/{server_id}/files/create-folder",
            json={"root": directory, "name": name}
        )

    def compress(self, server_id, root, files):
        return self.panel.post(
            f"/api/client/servers/{server_id}/files/compress",
            json={"root": root, "files": files}
        )

    def decompress(self, server_id, file_path):
        return self.panel.post(
            f"/api/client/servers/{server_id}/files/decompress",
            json={"file": file_path}
        )
