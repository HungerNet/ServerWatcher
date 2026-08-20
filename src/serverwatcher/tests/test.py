@stats.child('get', requires_arguments=False)
def stats_get(self, arg=None):
    '''
    args:
        ram [rounding] [--raw]
        cpu [rounding]
        uptime [--raw]
        tps [rounding] [mode]
        players
        version
        platform
    '''
    stats_get.__description__ = 'Retrieve and print all or specific server statistics'

    self.watcher.server.refresh()

    if arg is not None:
        gb = raw()
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
    else:
        return
