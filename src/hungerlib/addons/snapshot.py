class Snapshot:
    def __init__(self, Server, rounding=2, gb=False):
        self.Server = Server

        # generic
        self.ram = self.Server.getRAM(rounding, gb)
        self.cpu = self.Server.getCPU()
        self.network_in = self.Server.getNetworkIn(rounding, gb)
        self.network_out = self.Server.getNetworkOut(rounding, gb)
        self.uptime = self.Server.getUptime()
        self.uptime_formatted = self.Server.getUptime(True)

        # server-specific
        self.tps = self.Server.getTPS() if hasattr(self.Server, 'getTPS') else None
        self.players = self.Server.getPlayers() if hasattr(self.Server, 'getPlayers') else None

    def __str__(self):
        base = (
            f'Server: {self.Server.name}\n'
            f'Uptime: {self.uptime_formatted}\n'
            f'RAM: {self.ram}\n'
            f'CPU: {self.cpu}\n'
            f'Network (in): {self.network_in}\n'
            f'Network (out): {self.network_out}'
        )
        if self.tps is not None:
            base += f'\nTPS: {self.tps}'
        if self.players is not None:
            base += f'\nOnline players: {self.players}'

        return base