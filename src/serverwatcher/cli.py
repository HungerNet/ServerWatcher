import asyncio
from hungerlib import utils
from mapres import rprint, maps, setGlobalMaps
from .watcher import ServerWatcher
import inspect

setGlobalMaps(maps.ascii_colors)

class WatcherCLI:
    def __init__(self, watcher: ServerWatcher):
        self.watcher = watcher
        self.buffer = utils.Buffer(enabled=True)

        # command registry
        self.commands = {}
        self.aliases = {}

        # output mode: both | cli | silent
        self.outputMode = "both"

        self._register_types()
        self._register_aliases()
        self._register_commands()

    # ---------------------------------------------------------
    # Registration helpers
    # ---------------------------------------------------------
    def command(self, name, args=None, description=None):
        def decorator(func):
            self.commands[name] = {
                "handler": func,
                "args": args or [],
                "description": description or ""
            }
            return func
        return decorator

    def alias(self, name, target):
        self.aliases[name] = target

    # ---------------------------------------------------------
    # CLI buffer write
    # ---------------------------------------------------------
    def bprint(self, text):
        if self.buffer.enabled:
            self.buffer.captured.append(text)
        print(text)  # raw print for CLI mode

    # ---------------------------------------------------------
    # MAIN CLI LOOP (replaces LiveCLI.run)
    # ---------------------------------------------------------
    async def run(self):
        while True:

            # show prompt only in CLI mode
            if self.outputMode == "cli":
                print("> ", end="")

            # Pterodactyl-safe input
            print("", end="")
            line = await asyncio.to_thread(input, "")
            line = line.strip()

            if not line:
                continue

            # alias resolution
            if line in self.aliases:
                line = self.aliases[line]

            parts = line.split()
            cmd_name = parts[0]
            args = parts[1:]

            # unknown command
            if cmd_name not in self.commands:
                print(f"Unknown command: '{cmd_name}'")
                print("Root commands:", ", ".join(self.commands.keys()))
                continue

            cmd = self.commands[cmd_name]
            handler = cmd["handler"]

            try:
                # run command
                if inspect.iscoroutinefunction(handler):
                    result = await handler(*args)
                else:
                    result = handler(*args)

                # print result
                if result is not None and self.outputMode in ("both", "cli"):
                    print(result)

                # print CLI buffer
                if self.outputMode == "cli":
                    for msg in self.buffer.captured:
                        print(msg)

            except Exception as e:
                print(f"Error: {e}")

    # ---------------------------------------------------------
    # Types
    # ---------------------------------------------------------
    def _register_types(self):
        pass  # your types are handled manually in commands

    # ---------------------------------------------------------
    # Aliases
    # ---------------------------------------------------------
    def _register_aliases(self):
        self.alias("stats", "stats.get")
        self.alias("view", "view.cli")
        self.alias("watcher", "watcher.restart")

    # ---------------------------------------------------------
    # Commands
    # ---------------------------------------------------------
    def _register_commands(self):
        self._register_view_commands()
        self._register_stats_commands()
        self._register_watcher_commands()

    # ---------------------------------------------------------
    # VIEW COMMANDS
    # ---------------------------------------------------------
    def _register_view_commands(self):

        @self.command("view.cli", description="Switch output mode to CLI only")
        def view_cli():
            self.watcher.router.disableOriginOutput()
            self.outputMode = "cli"

            utils.clearTerminal()
            print("", end="")

            rprint("<yellow>-----------------------------------")
            rprint("<yellow>-------- <aqua>ServerWatcher CLI <yellow>--------")
            rprint("<yellow>-----------------------------------")
            print("\n")

            for msg in self.buffer.captured:
                print(msg)

        @self.command("view.watcher", description="Switch output mode to watcher logs")
        def view_watcher():
            self.watcher.router.enableOriginOutput()
            self.outputMode = "both"

            utils.clearTerminal()
            print("", end="")
            self.watcher.router.buffer.printCaptured()

    # ---------------------------------------------------------
    # STATS COMMANDS
    # ---------------------------------------------------------
    def _register_stats_commands(self):

        @self.command("stats.get", description="Get a server statistic")
        def stats_get(stat):
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

    # ---------------------------------------------------------
    # WATCHER COMMANDS
    # ---------------------------------------------------------
    def _register_watcher_commands(self):

        @self.command("watcher.restart", description="Restart the server")
        def watcher_restart():
            self.watcher.restart_and_wait()

        @self.command("watcher.schedule", description="Schedule a restart")
        def watcher_schedule(minutes):
            self.watcher.schedule_restart(int(minutes))

        @self.command("watcher.shutdown", description="Shutdown watcher")
        def watcher_shutdown():
            self.watcher.shutdown()
