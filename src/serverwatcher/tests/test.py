@command('stats') # removed requires_children=True, the DSL should interpret no logic as requiring children
def stats(self):
    '''
    Retrieve and print server statistics
    '''


@stats.child('get') # removed requires_arguments=False, the DSL should interpret logic for both as supporting both args and noargs. that and having arg=None. If it didn't support arguments it would just be self right? And if it required arguments it would have arg, not arg=None right?
def stats_get(self, arg=None):
    '''
    Retrieve and print all or specific server statistics
    '''
    # the below will render as not having indents correct? or not?
    __args__ =  '''
    ram: [rounding] [--raw]
    cpu: [rounding]
    uptime: [rounding] [mode]
    players
    version
    platform
    '''
    self.watcher.server.refresh()

    if arg is None:
        return # will add support later for showing all stats, but this acts as a placeholder for the DLS to know it supports optional arguments.

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
    '''The decimal place to round to''' # yes, descriptions need to be supported for flags and params too.
    return value


@stats.get.param('mode', type=str, default='current')
def mode(value):
    '''The mode for TPS. Accepted: current, 1m, 5m, tick_time'''
    return value


@stats.get.flag('raw')
def raw():
    '''Return the raw value instead of the calculated or formatted string'''
    return True