import asyncio
from hungerlib import LiveCLI
from .watcher import ServerWatcher


class WatcherCLI:
    def __init__(self, watcher: ServerWatcher):
        self.watcher = watcher
        self.cli = LiveCLI(prefix=None)

        self._register_types()
        self._register_aliases()
        self._register_commands()

    async def run(self):
        await self.cli.run()

    # Types
    def _register_types(self):
        # enum for stats
        self.cli.register_type("Stat", lambda s: s if s in (
            "cpu", "ram", "uptime", "tps", "players"
        ) else (_ for _ in ()).throw(ValueError(
            f"Invalid stat '{s}'. Expected: cpu, ram, uptime, tps, players"
        )))

    # aliases (optional)
    def _register_aliases(self):
        self.cli.alias("stats", "stats")
        self.cli.alias("view", "view")
        self.cli.alias("watcher", "watcher")

    # commands
    def _register_commands(self):
        self._register_view_commands()
        self._register_stats_commands()
        self._register_watcher_commands()

    # view cli / view watcher
    def _register_view_commands(self):

        @self.cli.command("view.cli", description="Switch output mode to CLI only")
        def view_cli():
            self.cli.outputMode = "cli"
            self.watcher.router.enableBuffer()
            print("Output mode set to cli")

        @self.cli.command("view.watcher", description="Switch output mode to watcher logs")
        def view_watcher():
            self.cli.outputMode = "both"
            self.watcher.router.disableBuffer()
            self.watcher.router.flushBuffer()
            print("Output mode set to watcher")

    # stats get <stat>
    def _register_stats_commands(self):

        @self.cli.command(
            "stats.get",
            args=["stat:Stat"],
            description="Get a server statistic"
        )
        def stats_get(stat):
            # refresh server snapshot
            self.watcher.server.refresh()

            if stat == "cpu":
                print(self.watcher.server.cpu)
            elif stat == "ram":
                print(self.watcher.server.ram)
            elif stat == "uptime":
                print(self.watcher.server.uptime)
            elif stat == "tps":
                print(self.watcher.server.tps)
            elif stat == "players":
                print(self.watcher.server.players)
            else:
                print(f"Unknown stat: {stat}")

    # watcher commands
    def _register_watcher_commands(self):

        @self.cli.command(
            "watcher.restart",
            description="Restart the server and wait for it to come online"
        )
        def watcher_restart():
            self.watcher.restart_and_wait()

        @self.cli.command(
            "watcher.schedule",
            args=["minutes:int"],
            description="Schedule a restart in N minutes"
        )
        def watcher_schedule(minutes):
            self.watcher.schedule_restart(minutes)

        @self.cli.command(
            "watcher.shutdown",
            description="Shutdown the watcher"
        )
        def watcher_shutdown():
            self.watcher.shutdown()
