from hungerlib import utils
from mapres import res, ascii_colors, setGlobalMaps
from .watcher import ServerWatcher
from .livecli import LiveCLI, command

setGlobalMaps(ascii_colors)


class WatcherCLI(LiveCLI):
    def __init__(self, watcher: ServerWatcher):
        super().__init__()
        self.watcher = watcher
        self.buffer = utils.Buffer(enabled=True)
        self.outputMode = 'both'

    def printHeader(self) -> None:
        self.safePrint(res('<yellow>-----------------------------------'))
        self.safePrint(res('<yellow>-------- <aqua>ServerWatcher CLI <yellow>--------'))
        self.safePrint(res('<yellow>-----------------------------------'))
        self.safePrint('\n')


# ---------------------------------------------------------------------------
# stats command
# ---------------------------------------------------------------------------

@command('stats', requires_children=True)
def stats():
    __description__ = 'Retrieve and print server statistics'


@stats.child('get', requires_arguments=False)
def stats_get(self, arg=None):
    __description__ = 'Retrieve and print all or specific server statistics'

    self.watcher.server.refresh()

    if arg is not None:
        gb = not raw()
        if formatted():
            fmt = True
        elif no_formatted():
            fmt = False
        else:
            fmt = True

        unit = ''
        match arg:
            case 'ram':
                value = self.watcher.server.getRAM(rounding=rounding(), gb=gb)
                name = 'RAM'
                unit = ' GB' if gb else ' MB'
            case 'cpu':
                value = self.watcher.server.getCPU(rounding=rounding())
                name = 'CPU'
                unit = '%'
            case 'uptime':
                value = self.watcher.server.getUptime(formatted=fmt)
                name = 'Uptime'
                unit = '' if fmt else 'ms'
            case 'tps':
                value = self.watcher.server.getTPS(rounding=rounding(), mode=mode())
                name = 'TPS'
            case 'players':
                value = self.watcher.server.getPlayers()
                name = 'Players'
            case 'version':
                value = self.watcher.server.version
                name = 'Minecraft version'
            case 'platform':
                value = self.watcher.server.platform
                name = 'Server platform'
            case _:
                return self.safePrint('Unknown stat')

        self.bprint(f'{name}: {value}{unit}')
    else:
        return  # later: print all stats for `stats get`


@stats.get.param('rounding', type=int, default=2)
def rounding(value: int):
    __description__ = 'placeholder'
    return value


@stats.get.param('mode', type=str, default='current')
def mode(value: str):
    return value


@stats.get.flag('raw')
def raw():
    __description__ = 'placeholder'
    return True  # DSL overrides with presence/absence


@stats.get.flag('formatted')
def formatted():
    return True  # DSL overrides with presence/absence


@stats.get.flag('no-formatted')
def no_formatted():
    return False  # DSL overrides with presence/absence


# ---------------------------------------------------------------------------
# view command
# ---------------------------------------------------------------------------

@command('view', requires_children=True)
def view():
    __description__ = 'Switch terminal view'


@view.child('cli')
def view_cli(self):
    __description__ = 'Switch to CLI view'

    self.watcher.router.disableOriginOutput()
    self.outputMode = 'cli'
    self.buffer.enabled = True
    utils.clearTerminal()
    self.printHeader()
    for msg in self.buffer.captured:
        self.safePrint(msg)


@view.child('watcher')
def view_watcher(self):
    __description__ = 'Switch to Watcher view'

    self.watcher.router.enableOriginOutput()
    self.outputMode = 'both'
    utils.clearTerminal()
    self.printHeader()
    for msg in self.watcher.router.buffer.captured:
        self.safePrint(msg)


# ---------------------------------------------------------------------------
# clear command
# ---------------------------------------------------------------------------

@command('clear')
def clear():
    __description__ = 'Clear the CLI terminal'


@clear.flag('no-buffer')
def no_buffer():
    return False  # DSL overrides with presence/absence
