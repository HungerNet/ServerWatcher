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


# we keep this only for the positional stat name
stats_parser = argparse.ArgumentParser(add_help=False)
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

        # CLI stdout goes through BufferingStdout → captured in self.buffer
        self.cli_stdout = BufferingStdout(self.buffer, self.real_stdout)

        # permanently override cmd.Cmd stdout
        super().__init__(stdout=self.cli_stdout)

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
        self.real_stdout.write(str(msg) + end)
        self.real_stdout.flush()
    
    def printHeader(self):
        self.safePrint(res("<yellow>-----------------------------------"))
        self.safePrint(res("<yellow>-------- <aqua>ServerWatcher CLI <yellow>--------"))
        self.safePrint(res("<yellow>-----------------------------------"))
        self.safePrint("\n")

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

        # CLI capture always enabled
        self.buffer.enabled = True

        utils.clearTerminal()
        self.safePrint("", end="")

        # header is always printed fresh, not stored in buffer
        self.printHeader()

        # replay captured CLI output
        for msg in self.buffer.captured:
            self.safePrint(msg)

    def _view_watcher(self):
        self.watcher.router.enableOriginOutput()
        self.outputMode = "both"

        # do NOT touch self.buffer.enabled here

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
        stats get <cpu|ram|uptime|tps|players> [gb:true|false] [rounding:<int>]
        Example:
          stats get ram
          stats get ram gb:false
          stats get ram gb:false rounding:1
        """
        parts = arg.split()
        if len(parts) == 0 or parts[0] != "get":
            self.safePrint("Usage: stats get <cpu|ram|uptime|tps|players> [gb:true|false] [rounding:<int>]")
            return

        # strip the leading "get"
        tokens = parts[1:]
        if not tokens:
            self.safePrint("Usage: stats get <cpu|ram|uptime|tps|players> [gb:true|false] [rounding:<int>]")
            return

        # first token is the stat name, validated by stats_parser
        try:
            args = stats_parser.parse_args([tokens[0]])
            stat = args.stat
        except SystemExit:
            self.safePrint("Usage: stats get <cpu|ram|uptime|tps|players> [gb:<bool>] [rounding:<int>] [formatted:<bool>]")
            return

        # defaults
        gb = True
        rounding = 2
        formatted = True

        # parse optional key:value tokens
        for token in tokens[1:]:
            if ":" not in token:
                continue
            key, value = token.split(":", 1)
            key = key.strip().lower()
            value = value.strip().lower()

            if key == "gb":
                gb = value == "true"
            elif key == "rounding":
                try:
                    rounding = int(value)
                except ValueError:
                    self.safePrint("rounding must be an integer")
                    return
            elif key == 'formatted':
                formatted = value == 'true'

        self._stats_get(stat, gb=gb, rounding=rounding, formatted=formatted)

    def _stats_get(self, stat: str, gb: bool=True, rounding: int=2, formatted: bool=True):
        self.watcher.server.refresh()

        if stat == "ram":
            value = self.watcher.server.getRAM(rounding=rounding, gb=gb)
            stat_name = 'RAM'
            unit = ' GB' if gb else ' MB'
        elif stat == "cpu":
            value = self.watcher.server.getCPU(rounding=rounding)
            stat_name = 'CPU'
            unit = '%'
        elif stat == "uptime":
            value = self.watcher.server.getUptime(formatted=formatted)
            stat_name = 'Uptime'
            unit = '' if formatted else 'ms'
        elif stat == "tps":
            value = self.watcher.server.getTPS()
            stat_name = 'TPS'
            unit = ''
        elif stat == "players":
            value = self.watcher.server.getPlayers()
            stat_name = 'Players'
            unit = ''
        else:
            self.safePrint("Unknown stat")
            return

        self.bprint(f'{stat_name}: {value}{unit}')

    # ---------------------------------------------------------
    # CLEAR COMMAND
    # ---------------------------------------------------------
    def do_clear(self, arg):
        """
        clear buffer:true
        clear buffer:false
        """
        parts = arg.split()

        # default: buffer:false
        clear_buffer = False

        # parse key:value pairs
        for token in parts:
            if ":" not in token:
                continue
            key, value = token.split(":", 1)
            key = key.strip().lower()
            value = value.strip().lower()

            if key == "buffer":
                clear_buffer = (value == "true")

        # clear CLI buffer only
        if clear_buffer:
            self.buffer.clear()

        # clear terminal (but NOT watcher buffer)
        utils.clearTerminal()

        # print header (not captured)
        self.printHeader()


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
            self.buffer.captured.append(str(text))
        self.safePrint(str(text))
