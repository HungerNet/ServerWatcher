import asyncio
import argparse
import cmd2

from hungerlib import utils
from mapres import rprint, maps, setGlobalMaps
from .watcher import ServerWatcher

setGlobalMaps(maps.ascii_colors)


# ---------------------------------------------------------
# ARGPARSE DEFINITIONS
# ---------------------------------------------------------

stats_parser = argparse.ArgumentParser()
stats_parser.add_argument(
    "stat",
    choices=["cpu", "ram", "uptime", "tps", "players"],
    help="Statistic to retrieve"
)

schedule_parser = argparse.ArgumentParser()
schedule_parser.add_argument(
    "minutes",
    type=int,
    help="Minutes until restart"
)


# ---------------------------------------------------------
# MAIN SHELL
# ---------------------------------------------------------

class WatcherCLI(cmd2.Cmd):
    prompt = "> "

    def __init__(self, watcher: ServerWatcher):
        super().__init__(allow_cli_args=False)

        self.watcher = watcher
        self.buffer = utils.Buffer(enabled=True)

        # output mode: both | cli | silent
        self.outputMode = "both"

        self.use_rawinput = False
        self.echo = False
        self.disable_history = True

    async def run(self):
        while True:
            if self.outputMode == "cli":
                print("> ", end="")
                print('', end='')

            line = await asyncio.to_thread(input)
            line = line.strip()

            if not line:
                continue

            # cmd2 handles dispatching
            stop = await asyncio.to_thread(self.onecmd, line)
            if stop:
                break

    # ---------------------------------------------------------
    # VIEW COMMANDS
    # ---------------------------------------------------------

    def do_view(self, arg):
        """
        view cli
        view watcher
        """
        if arg == "cli":
            self._view_cli()
        elif arg == "watcher":
            self._view_watcher()
        else:
            self.poutput("Usage: view <cli|watcher>")

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

    @cmd2.with_argparser(stats_parser)
    def do_stats(self, args):
        """
        stats get <cpu|ram|uptime|tps|players>
        """
        # cmd2 already validated the stat
        self._stats_get(args.stat)

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

    # ---------------------------------------------------------
    # WATCHER COMMANDS
    # ---------------------------------------------------------

    def do_watcher(self, arg):
        """
        watcher restart
        watcher schedule <minutes>
        watcher shutdown
        """
        parts = arg.split()

        if len(parts) == 0:
            self.poutput("Usage: watcher <restart|schedule|shutdown>")
            return

        sub = parts[0]

        if sub == "restart":
            self.watcher.restart_and_wait()

        elif sub == "schedule":
            # delegate to argparse version
            try:
                args = schedule_parser.parse_args(parts[1:])
                self.watcher.schedule_restart(args.minutes)
            except SystemExit:
                self.poutput("Usage: watcher schedule <minutes>")

        elif sub == "shutdown":
            self.watcher.shutdown()
            return True

        else:
            self.poutput("Usage: watcher <restart|schedule|shutdown>")

    # ---------------------------------------------------------
    # BUFFER PRINT
    # ---------------------------------------------------------

    def bprint(self, text):
        if self.buffer.enabled:
            self.buffer.captured.append(text)
        self.poutput(text)
