import asyncio
from hungerlib import utils
from mapres import rprint, maps, setGlobalMaps
from .watcher import ServerWatcher

setGlobalMaps(maps.ascii_colors)

class WatcherCLI:
    def __init__(self, watcher: ServerWatcher):
        self.watcher = watcher
        self.buffer = utils.Buffer(enabled=True)

        # output mode: both | cli | silent
        self.outputMode = "both"

    # ---------------------------------------------------------
    # CLI buffer write
    # ---------------------------------------------------------
    def bprint(self, text):
        if self.buffer.enabled:
            self.buffer.captured.append(text)
        print(text)

    # ---------------------------------------------------------
    # MAIN CLI LOOP (no LiveCLI)
    # ---------------------------------------------------------
    async def run(self):
        while True:

            # show prompt only in CLI mode
            if self.outputMode == "cli":
                print("> ", end="")
                print('', end='')

            # Pterodactyl-safe input
            # print("", end="")
            line = await asyncio.to_thread(input)
            line = line.strip()

            if not line:
                continue

            parts = line.split()
            cmd = parts[0]
            args = parts[1:]

            # -------------------------------------------------
            # COMMAND ROUTING (simple if/elif)
            # -------------------------------------------------

            # view cli
            if cmd == "view" and len(args) == 1 and args[0] == "cli":
                self._view_cli()
                continue

            # view watcher
            if cmd == "view" and len(args) == 1 and args[0] == "watcher":
                self._view_watcher()
                continue

            # stats get <stat>
            if cmd == "stats" and len(args) == 2 and args[0] == "get":
                self._stats_get(args[1])
                continue

            # watcher restart
            if cmd == "watcher" and len(args) == 1 and args[0] == "restart":
                self.watcher.restart_and_wait()
                continue

            # watcher schedule <minutes>
            if cmd == "watcher" and len(args) == 2 and args[0] == "schedule":
                try:
                    minutes = int(args[1])
                    self.watcher.schedule_restart(minutes)
                except:
                    print("Invalid minutes")
                continue

            # watcher shutdown
            if cmd == "watcher" and len(args) == 1 and args[0] == "shutdown":
                self.watcher.shutdown()
                continue

            # unknown command
            print(f"Unknown command: '{line}'")
            print("Commands:")
            print("  view cli")
            print("  view watcher")
            print("  stats get <cpu|ram|uptime|tps|players>")
            print("  watcher restart")
            print("  watcher schedule <minutes>")
            print("  watcher shutdown")

    # ---------------------------------------------------------
    # VIEW COMMANDS
    # ---------------------------------------------------------
    def _view_cli(self):
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

    def _view_watcher(self):
        self.watcher.router.enableOriginOutput()
        self.outputMode = "both"

        utils.clearTerminal()
        print("", end="")
        self.watcher.router.buffer.printCaptured()

    # ---------------------------------------------------------
    # STATS COMMANDS
    # ---------------------------------------------------------
    def _stats_get(self, stat):
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
