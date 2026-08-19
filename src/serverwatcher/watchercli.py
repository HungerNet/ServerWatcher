# watchercli.py

from .livecli import (
    LiveCLI,
    command,
    COMMANDS,
    generate_help,
)
from hungerlib import utils
from mapres import res, maps, setGlobalMaps
from .watcher import ServerWatcher

setGlobalMaps(maps.ascii_colors)


# -------------------------
# WatcherCLI
# -------------------------

class WatcherCLI(LiveCLI):
    def __init__(self, watcher: ServerWatcher):
        super().__init__()
        self.watcher = watcher
        self.buffer = utils.Buffer(enabled=True)
        self.outputMode = "both"

    def printHeader(self):
        self.safePrint(res("<yellow>-----------------------------------"))
        self.safePrint(res("<yellow>-------- <aqua>ServerWatcher CLI <yellow>--------"))
        self.safePrint(res("<yellow>-----------------------------------"))
        self.safePrint("")


# -------------------------
# Commands
# -------------------------

@command("stats", requires_children=True)
def stats():
    __description__ = "Retrieve and print server statistics"


@stats.child("get", requires_arguments=False)
def stats_get(self: WatcherCLI, arg=None, **kwargs):
    __description__ = "Retrieve and print all or specific server statistics"

    rounding = kwargs["rounding"]
    mode = kwargs["mode"]
    raw = kwargs["raw"]
    formatted = kwargs["formatted"]
    no_formatted = kwargs["no_formatted"]

    self.watcher.server.refresh()

    if arg is None:
        return  # later: print all stats

    gb = not raw()
    fmt = formatted() or not no_formatted()

    unit = ""
    match arg:
        case "ram":
            value = self.watcher.server.getRAM(rounding=rounding(), gb=gb)
            name = "RAM"
            unit = " GB" if gb else " MB"
        case "cpu":
            value = self.watcher.server.getCPU(rounding=rounding())
            name = "CPU"
            unit = "%"
        case "uptime":
            value = self.watcher.server.getUptime(formatted=fmt)
            name = "Uptime"
            unit = "" if fmt else "ms"
        case "tps":
            value = self.watcher.server.getTPS(rounding=rounding(), mode=mode())
            name = "TPS"
        case "players":
            value = self.watcher.server.getPlayers()
            name = "Players"
        case "version":
            value = self.watcher.server.version
            name = "Minecraft version"
        case "platform":
            value = self.watcher.server.platform
            name = "Server platform"
        case _:
            return self.safePrint("Unknown stat")

    self.bprint(f"{name}: {value}{unit}")


@stats.get.param("rounding", type=int, default=2)
def rounding(value):
    return value


@stats.get.param("mode", type=str, default="current")
def mode(value):
    return value


@stats.get.flag("raw")
def raw():
    return True


@stats.get.flag("formatted")
def formatted():
    return True


@stats.get.flag("no-formatted")
def no_formatted():
    return False


# -------------------------
# view command
# -------------------------

@command("view", requires_children=True)
def view():
    __description__ = "Switch terminal view"


@view.child("cli")
def view_cli(self: WatcherCLI, arg=None, **kwargs):
    __description__ = "Switch to CLI view"

    self.watcher.router.disableOriginOutput()
    self.outputMode = "cli"
    utils.clearTerminal()
    self.printHeader()
    for msg in self.buffer.captured:
        self.safePrint(msg)


@view.child("watcher")
def view_watcher(self: WatcherCLI, arg=None, **kwargs):
    __description__ = "Switch to Watcher view"

    self.watcher.router.enableOriginOutput()
    self.outputMode = "both"
    utils.clearTerminal()
    self.printHeader()
    for msg in self.watcher.router.buffer.captured:
        self.safePrint(msg)


# -------------------------
# clear command
# -------------------------

@command("clear")
def clear():
    __description__ = "Clear the CLI terminal"


@clear.child("buffer")
def clear_buffer(self: WatcherCLI, arg=None, **kwargs):
    __description__ = "Clear or keep the CLI buffer"

    no_buffer = kwargs["no_buffer"]

    if not no_buffer():
        self.buffer.clear()

    utils.clearTerminal()
    self.printHeader()


@clear_buffer.flag("no-buffer")
def no_buffer():
    return True


# -------------------------
# help command
# -------------------------

@command("help", requires_arguments=True)
def help():
    __description__ = "Show help for a command"


@help.child("command", requires_arguments=True)
def help_command(self: WatcherCLI, cmd_name=None, **kwargs):
    __description__ = "Show help for a specific command"

    if cmd_name is None:
        return self.safePrint("Usage: help command <name>")

    cmd = COMMANDS.get(cmd_name)
    if not cmd:
        return self.safePrint(f"Unknown command '{cmd_name}'")

    self.safePrint(generate_help(cmd))
