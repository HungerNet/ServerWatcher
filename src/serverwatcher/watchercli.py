from hungerlib import utils
from mapres import res, ascii_colors, setGlobalMaps
from .watcher import ServerWatcher
from .livecli import LiveCLI, command

setGlobalMaps(ascii_colors)

class BufferingStdout:
    def __init__(self, buffer, real_stdout):
        self.buffer = buffer
        self.real_stdout = real_stdout
    def write(self, text):
        if self.buffer.enabled and text.strip():
            self.buffer.captured.append(text.rstrip('\n'))
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
        self.safePrint(res('<yellow>-----------------------------------'))
        self.safePrint(res('<yellow>-------- <aqua>ServerWatcher CLI <yellow>--------'))
        self.safePrint(res('<yellow>-----------------------------------'))
        self.safePrint('')

@command('stats')
def stats(self):
    '''
    Retrieve and print server statistics
    '''
    pass

@stats.child('get')
def stats_get(self, arg=None):
    '''
    Retrieve and print all or specific server statistics
    '''
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
        return
    gb = not raw()
    fmt = not raw()
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

@stats.get.param('rounding', type=int, default=2)
def rounding(value):
    '''The decimal place to round to'''
    return value

@stats.get.param('mode', type=str, default='current')
def mode(value):
    '''The mode for TPS. Accepted: current, 1m, 5m, tick_time'''
    return value

@stats.get.flag('raw')
def raw():
    '''Return the raw value instead of the formatted string'''
    return True

@command('view')
def view(self):
    '''
    Switch terminal view
    '''
    pass

@view.child('cli')
def view_cli(self):
    '''
    Switch to CLI view
    '''
    self.watcher.router.disableOriginOutput()
    self.outputMode = 'cli'
    self.buffer.enabled = True
    utils.clearTerminal()
    self.safePrint('', end='')
    self.printHeader()
    for msg in self.buffer.captured:
        self.safePrint(msg)

@view.child('watcher')
def view_watcher(self):
    '''
    Switch to Watcher view
    '''
    self.watcher.router.enableOriginOutput()
    self.outputMode = 'both'
    utils.clearTerminal()
    self.safePrint('', end='')
    for msg in self.watcher.router.buffer.captured:
        self.safePrint(msg)

@command('clear')
def clear(self):
    '''
    Clear the CLI terminal
    '''
    no_buf = no_buffer()
    if not no_buf:
        self.buffer.clear()
    utils.clearTerminal()
    self.printHeader()

@clear.flag('no-buffer')
def no_buffer():
    '''Do not clear buffer'''
    return True
Z