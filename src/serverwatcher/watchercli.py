from hungerlib import utils
from mapres import res, ascii_colors, setGlobalMaps
from .watcher import ServerWatcher
from c2e import LiveCLI, command

setGlobalMaps(ascii_colors)

class BufferingStdout:
    def __init__(self, buffer, real_stdout):
        self.buffer = buffer
        self.real_stdout = real_stdout
    def write(self, text):
        if self.buffer.enabled:
            self.buffer.captured.append(text)
        self.real_stdout.write(text)
    def flush(self):
        self.real_stdout.flush()

class WatcherCLI(LiveCLI):
    def __init__(self, watcher: ServerWatcher):
        super().__init__()
        self.watcher = watcher
        self.buffer = utils.Buffer(enabled=True)
        self.outputMode = 'both'
    def printHeader(self):
        self.safePrint(res('<yellow>-----------------------------------'), write_buffer=False)
        self.safePrint(res('<yellow>-------- <aqua>ServerWatcher CLI <yellow>--------'), write_buffer=False)
        self.safePrint(res('<yellow>-----------------------------------'), write_buffer=False)
        self.safePrint('', write_buffer=False)

@command('stats')
def stats(self, arg=None):
    '''Retrieve and print all or specific server statistics'''
    __args__ = '''
    ram: rounding, --raw
    cpu: rounding
    uptime: rounding, mode
    players
    version
    platform
    '''
    self.watcher.server.refresh()
    if arg is None:
        self.safePrint(res('<gray>Fetching server statistics...'))
        self.safePrint(res(
            f'''<blue>RAM: <reset>{self.watcher.server.getRAM(gb=True)} GiB
            <blue>CPU: <reset>{self.watcher.server.getCPU()}%
            <blue>Uptime: <reset>{self.watcher.server.getUptime(formatted=True)}
            <blue>TPS: <reset>{self.watcher.server.getTPS()}
            <blue>Players: <reset>{self.watcher.server.getPlayers()}
            <blue>Version: <reset>{self.watcher.server.getVersion()}
            <blue>Platform: <reset>{self.watcher.server.getPlatform().title()}
            <blue>Bridge: <reset>v{self.watcher.server.getBridgeVersion()}'''
        ))
        return
    gb = not raw()
    fmt = not raw()
    unit = ''
    match arg:
        case 'ram':
            value = self.watcher.server.getRAM(rounding=rounding(), gb=gb)
            name = 'RAM'
            unit = ' GiB' if gb else ' MiB'
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
            value = self.watcher.server.getVersion()
            name = 'Minecraft version'
        case 'platform':
            value = self.watcher.server.getPlatform().title()
            name = 'Server platform'
        case 'bridge':
            value = res(f'<gray>v<reset>{self.watcher.server.getBridgeVersion()}')
            name = 'Bridge version'
        case _:
            return self.safePrint('Unknown stat')
    self.safePrint(res(f'<blue>{name}: <reset>{value}{unit}'))

@stats.param('rounding', type=int, default=2)
def rounding(value):
    '''The decimal place to round to'''
    return value

@stats.param('mode', type=str, default='current')
def mode(value):
    '''The mode for TPS. Accepted: current, 1m, 5m, tick_time'''
    return value

@stats.flag('raw')
def raw():
    '''Return the raw value instead of the formatted string'''
    return True

@command('view', namespace=True)
def view(self):
    '''Switch terminal view'''
    pass

@view.child('cli')
def view_cli(self):
    '''Switch to CLI view'''
    self.watcher.router.disableOriginOutput()
    self.outputMode = 'cli'
    self.buffer.enabled = True
    utils.clearTerminal()
    self.safePrint('', end='')
    self.printHeader()
    for msg in self.buffer.captured:
        self.safePrint(msg, write_buffer=False)

@view.child('watcher')
def view_watcher(self):
    '''Switch to Watcher view'''
    self.watcher.router.enableOriginOutput()
    self.outputMode = 'both'
    utils.clearTerminal()
    self.safePrint('', end='')
    for msg in self.watcher.router.buffer.captured:
        self.safePrint(msg, write_buffer=False)
        self.safePrint()

@command('clear')
def clear(self):
    '''Clear the CLI terminal'''
    if not no_buffer():
        self.buffer.clear()
    utils.clearTerminal()
    self.printHeader()

@clear.flag('no-buffer')
def no_buffer():
    '''Do not clear buffer'''
    return True
