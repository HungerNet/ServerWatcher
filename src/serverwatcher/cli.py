import asyncio
import argparse
import cmd
import sys

from hungerlib import utils
from mapres import res, maps, setGlobalMaps
from .watcher import ServerWatcher

setGlobalMaps(maps.ascii_colors)


class BufferingStdout:
    def __init__(self, buffer, real_stdout):
        self.buffer = buffer
        self.real_stdout = real_stdout

    def write(self, text):
        # store only non-empty lines
        if text.strip():
            self.buffer.captured.append(text.rstrip("\n"))
        self.real_stdout.write(text)

    def flush(self):
        self.real_stdout.flush()



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


class WatcherCLI(cmd.Cmd):
    prompt = "> "

    def __init__(self, watcher: ServerWatcher):
        super().__init__()

        self.watcher = watcher
        self.buffer = utils.Buffer(enabled=True)

        # output mode: both | cli | silent
        self.outputMode = "both"

        # override with custom stdout
        self.real_stdout = sys.stdout
        # sys.stdout = BufferingStdout(self.buffer, self.real_stdout)

        self.use_rawinput = False

    async def run(self):
        while True:
            if self.outputMode == "cli":
                print("> ", end="")
                print('', end='')

            line = await asyncio.to_thread(input)
            line = line.strip()

            if not line:
                continue

            # override stdout ONLY during CLI command execution
            old_stdout = sys.stdout
            sys.stdout = BufferingStdout(self.buffer, old_stdout)

            try:
                stop = await asyncio.to_thread(self.onecmd, line)
            finally:
                # restore real stdout so watcher logs bypass capture
                sys.stdout = old_stdout

            if stop:
                break


    def safePrint(self, msg="", end="\n"):
        self.real_stdout.write(msg + end)
        self.real_stdout.flush()


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
            print("Usage: view <cli|watcher>")

    def _view_cli(self):
        self.watcher.router.disableOriginOutput()
        self.outputMode = "cli"

        utils.clearTerminal()
        self.safePrint("", end="")

        self.safePrint(res("<yellow>-----------------------------------"))
        self.safePrint(res("<yellow>-------- <aqua>ServerWatcher CLI <yellow>--------"))
        self.safePrint(res("<yellow>-----------------------------------"))
        self.safePrint("\n")

        # print buffer WITHOUT capturing
        for msg in self.buffer.captured:
            self.safePrint(msg)


    def _view_watcher(self):
        self.watcher.router.enableOriginOutput()
        self.outputMode = "both"

        utils.clearTerminal()
        self.safePrint("", end="")
        self.watcher.router.buffer.printCaptured()

    # ---------------------------------------------------------
    # STATS COMMANDS
    # ---------------------------------------------------------
    def do_stats(self, arg):
        """
        stats get <cpu|ram|uptime|tps|players>
        """
        try:
            args = stats_parser.parse_args(arg.split())
            self._stats_get(args.stat)
        except SystemExit:
            print("Usage: stats get <cpu|ram|uptime|tps|players>")

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
            print("Usage: watcher <restart|schedule|shutdown>")
            return

        sub = parts[0]

        if sub == "restart":
            self.watcher.restart_and_wait()

        elif sub == "schedule":
            try:
                args = schedule_parser.parse_args(parts[1:])
                self.watcher.schedule_restart(args.minutes)
            except SystemExit:
                print("Usage: watcher schedule <minutes>")

        elif sub == "shutdown":
            self.watcher.shutdown()
            return True

        else:
            print("Usage: watcher <restart|schedule|shutdown>")

    # ---------------------------------------------------------
    # BUFFER PRINT
    # ---------------------------------------------------------
    def bprint(self, text):
        if self.buffer.enabled:
            self.buffer.captured.append(text)
        print(text)
