@command('stats')
def stats(): pass

@stats.child('get')
def get(stat: str):
    self.watcher.server.refresh()

    unit = ''
    match stat:
        case 'ram':
            value = self.watcher.server.getRAM(rounding=rounding(), gb=raw())
            name = 'RAM'
            unit = ' GB' if gb else ' MB'
        case 'cpu':
            value = self.watcher.server.getCPU(rounding=rounding())
            name = 'CPU'
            unit = '%'
        case 'uptime':
            value = self.watcher.server.getUptime(formatted=formatted())
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
    return value

@stats.get.param('mode', type=str, default='current')
def mode(value):
    return value

@stats.get.flag('raw')
def raw():
    return False

@stats.get.flag('formatted')
def formatted():
    return True

@stats.get.flag('no-formatted')
def no_formatted():
    return False
