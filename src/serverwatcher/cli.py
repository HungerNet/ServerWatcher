import asyncio
import argparse
import cmd
import sys

import termios
import tty

from hungerlib import utils
from mapres import res, maps, setGlobalMaps

from .watcher import ServerWatcher

setGlobalMaps(maps.ascii_colors)


class BufferingStdout:
    def __init__(self, buffer, real_stdout):
        self.buffer = buffer
        self.real_stdout = real_stdout

    def write(self, text):
        # capture only non-empty lines
        if self.buffer.enabled and text.strip():
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
    prompt = ""

    def __init__(self, watcher: ServerWatcher):
        self.watcher = watcher

        # buffer for CLI output
        self.buffer = utils.Buffer(enabled=True)

        # real stdout (terminal)
        self.real_stdout = sys.stdout

        # permanently override cmd.Cmd stdout
        super().__init__(stdout=BufferingStdout(self.buffer, self.real_stdout))

        # output mode: both | cli | silent
        self.outputMode = "both"

        # disable rawinput in order to control input manually
        self.use_rawinput = False

    def read_line_raw(self):
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)

        try:
            tty.setraw(fd)
            chars = []
            while True:
                ch = sys.stdin.read(1)
                if ch in ("\r", "\n"):
                    break
                chars.append(ch)

            return "".join(chars)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)

    async def run(self):
        while True:

            # read input without echo (Pterodactyl will echo anyway)
            line = await asyncio.to_thread(self.read_line_raw)
            line = line.strip()

            if not line:
                continue

            # capture command (Pterodactyl already printed it)
            if self.buffer.enabled and not line.startswith("view"):
                self.buffer.captured.append(line)

            # run command (self.stdout is already overridden)
            stop = await asyncio.to_thread(self.onecmd, line)

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
            self.safePrint("Usage: view <cli|watcher>")

    def _view_cli(self):
        self.watcher.router.disableOriginOutput()
        self.outputMode = "cli"

        # enable CLI capture
        self.buffer.enabled = True

        utils.clearTerminal()
        self.safePrint("", end="")

        # header is always printed fresh, not stored in buffer
        self.safePrint(res("<yellow>-----------------------------------"))
        self.safePrint(res("<yellow>-------- <aqua>ServerWatcher CLI <yellow>--------"))
        self.safePrint(res("<yellow>-----------------------------------"))
        self.safePrint("\n")

        # replay captured CLI output
        for msg in self.buffer.captured:
            self.safePrint(msg)

    def _view_watcher(self):
        self.watcher.router.enableOriginOutput()
        self.outputMode = "both"

        # disable CLI capture
        self.buffer.enabled = False

        utils.clearTerminal()
        self.safePrint("", end="")

        # replay watcher output
        for msg in self.watcher.router.buffer.captured:
            self.safePrint(msg)

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
            self.safePrint("Usage: stats get <cpu|ram|uptime|tps|players>")

    def _stats_get(self, stat):
        self.watcher.server.refresh()

        value = getattr(self.watcher.server, stat)
        self.bprint(value)

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
            self.safePrint("Usage: watcher <restart|schedule|shutdown>")
            return

        sub = parts[0]

        if sub == "restart":
            self.watcher.restart_and_wait()

        elif sub == "schedule":
            try:
                args = schedule_parser.parse_args(parts[1:])
                self.watcher.schedule_restart(args.minutes)
            except SystemExit:
                self.safePrint("Usage: watcher schedule <minutes>")

        elif sub == "shutdown":
            self.watcher.shutdown()
            return True

        else:
            self.safePrint("Usage: watcher <restart|schedule|shutdown>")

    # ---------------------------------------------------------
    # BUFFER PRINT
    # ---------------------------------------------------------
    def bprint(self, text):
        if self.buffer.enabled:
            self.buffer.captured.append(text)
        self.safePrint(text)
