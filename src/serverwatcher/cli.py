import asyncio
from hungerlib import LiveCLI, utils
from mapres import rprint, maps, setGlobalMaps
from .watcher import ServerWatcher

setGlobalMaps(maps.ascii_colors)

class WatcherCLI:
    def __init__(self, watcher: ServerWatcher):
        self.watcher = watcher
        self.cli = LiveCLI(prefix=None)

        self.buffer = utils.Buffer(enabled=True)

        self._register_types()
        self._register_aliases()
        self._register_commands()

    def bprint(self, text):
        if self.buffer.enabled:
            self.buffer.captured.append(text)
        print(text)

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

            # trigger Pterodactyl clear
            utils.clearTerminal()
            print('\b')

            # print header, newline, buffer, prompt
            rprint("<yellow>-------------------------")
            rprint("<yellow>--- <aqua>ServerWatcher CLI <yellow>---")
            rprint("<yellow>-------------------------")
            print('\n')
            self.buffer.printCaptured()
            print("> ", end="")

        @self.cli.command("view.watcher", description="Switch output mode to watcher logs")
        def view_watcher():
            self.cli.outputMode = "both"

            # trigger Pterodactyl clear
            utils.clearTerminal()
            print('\b')

            # print watcher buffer
            self.watcher.router.buffer.printCaptured()

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
                self.bprint(self.watcher.server.cpu)
            elif stat == "ram":
                self.bprint(self.watcher.server.ram)
            elif stat == "uptime":
                self.bprint(self.watcher.server.uptime)
            elif stat == "tps":
                self.bprint(self.watcher.server.tps)
            elif stat == "players":
                self.bprint(self.watcher.server.players)
            else:
                self.bprint(f"Unknown stat: {stat}")

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
