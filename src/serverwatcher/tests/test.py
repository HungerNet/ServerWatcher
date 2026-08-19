# @command      (name='name', requires_children=False, requires_arguments=False, requires_params=False, requires_flags=False)
# @command.child(name='name', requires_children=False, requires_arguments=False, requires_params=False, requires_flags=False)
# a command or child command that has arguments cannot have children. it can have params and flags though.

@command('stats', requires_children=True)
def stats():
    __description__ = 'Retrieve and print server statistics'


@stats.child('get', requires_arguments=False)
def stats_get(self, arg=None):
    __description__ = 'Retrieve and print all or specific server statistics'
    
    self.watcher.server.refresh()
    
    if arg is not None:
        # flag setup
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
        return # later i'll make it print ALL the stats, this is valid, because `stats get` (correct usage)


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
    return True # should mean that without flag, is False, with is True

@stats.get.flag('formatted')
def formatted():
    return True # should mean that without flag, is False, with is True

@stats.get.flag('no-formatted')
def no_formatted():
    return False # should mean that without flag, is True, with is False





# view command
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


# clear command
@command('clear')
def clear():
    __description__ = 'Clear the CLI terminal'

@clear.flag('no-buffer')
def no_buffer():
    return False # should clear buffer by default, with flag should not
