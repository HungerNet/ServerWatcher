import asyncio
import cmd
import sys
import termios
import tty
from dataclasses import dataclass

from hungerlib import utils
from mapres import res, maps, setGlobalMaps
from .watcher import ServerWatcher

setGlobalMaps(maps.ascii_colors)

# parsed arguments
@dataclass
class ParsedArgs:
    subcommand: str | None
    positional: list[str]
    flags: dict[str, bool]
    params: dict[str, str]


def parse_line(raw: str) -> ParsedArgs:
    raw = raw.strip()
    if not raw:
        return ParsedArgs(None, [], {}, {})

    parts = raw.split()
    sub = parts[0]
    positional: list[str] = []
    flags: dict[str, bool] = {}
    params: dict[str, str] = {}

    for token in parts[1:]:
        if token.startswith('--'):
            flags[token[2:]] = True
        elif ':' in token:
            key, value = token.split(':', 1)
            params[key.lower()] = value
        else:
            positional.append(token)

    return ParsedArgs(sub, positional, flags, params)


# command registry
COMMANDS = {}

class ParamSpec:
    def __init__(self, name, type_, default):
        self.name = name
        self.type = type_
        self.default = default

class FlagSpec:
    def __init__(self, name):
        self.name = name

class ChildSpec:
    def __init__(self, name, func):
        self.name = name
        self.func = func
        self.params = {}
        self.flags = {}

    def param(self, name, type=str, default=None):
        def deco(func):
            self.params[name] = ParamSpec(name, type, default)
            return func
        return deco

    def flag(self, name):
        def deco(func):
            self.flags[name] = FlagSpec(name)
            return func
        return deco

class CommandSpec:
    def __init__(self, name, func):
        self.name = name
        self.func = func
        self.children = {}

    def child(self, name):
        def deco(func):
            child = ChildSpec(name, func)
            self.children[name] = child
            return func
        return deco

class CommandDSL:
    def __call__(self, name):
        def deco(func):
            spec = CommandSpec(name, func)
            COMMANDS[name] = spec
            return spec
        return deco

command = CommandDSL()


# base CLI helpers
class CLIBase:
    def safePrint(self, msg: object = '', end: str = '\n') -> None:
        print(str(msg), end=end)

    def bprint(self, msg: object) -> None:
        self.safePrint(msg)


# dispatcher
def dispatch(cli: CLIBase, line: str):
    parsed = parse_line(line)
    if not parsed.subcommand:
        return

    cmd = COMMANDS.get(parsed.subcommand)
    if cmd is None:
        return cli.safePrint(f'Unknown command {parsed.subcommand}')

    cmd.func(cli, parsed)

    if not parsed.positional:
        return cli.safePrint('Missing subcommand')

    child_name = parsed.positional[0]
    child = cmd.children.get(child_name)
    if child is None:
        return cli.safePrint(f'Unknown subcommand {child_name}')

    stat = parsed.positional[1] if len(parsed.positional) > 1 else None

    wrappers: dict[str, callable] = {}

    for pname, pspec in child.params.items():
        if pname in parsed.params:
            raw = parsed.params[pname]

            def make_param(raw=raw, pspec=pspec):
                try:
                    return pspec.type(raw)
                except Exception:
                    return pspec.default

            wrappers[pname] = make_param
        else:
            def make_default(pspec=pspec):
                return pspec.default

            wrappers[pname] = make_default

    for fname, _fspec in child.flags.items():
        present = fname in parsed.flags

        def make_flag(present=present):
            return present

        wrappers[fname] = make_flag

    return child.func(cli, stat, **wrappers)


# buffering stdout
class BufferingStdout:
    def __init__(self, buffer, real_stdout):
        self.buffer = buffer
        self.real_stdout = real_stdout

    def write(self, text: str) -> None:
        if self.buffer.enabled and text.strip():
            self.buffer.captured.append(text.rstrip('\n'))
        self.real_stdout.write(text)

    def flush(self) -> None:
        self.real_stdout.flush()


# main CLI
class WatcherCLI(cmd.Cmd, CLIBase):
    prompt = ''

    def __init__(self, watcher: ServerWatcher):
        self.watcher = watcher
        self.buffer = utils.Buffer(enabled=True)
        self.real_stdout = sys.stdout
        self.cli_stdout = BufferingStdout(self.buffer, self.real_stdout)
        super().__init__(stdout=self.cli_stdout)
        self.outputMode = 'both'
        self.use_rawinput = False

    def read_line_raw(self) -> str:
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            chars: list[str] = []
            while True:
                ch = sys.stdin.read(1)
                if ch in ('\r', '\n'):
                    break
                chars.append(ch)
            return ''.join(chars)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)

    async def run(self):
        while True:
            try:
                line = await asyncio.to_thread(self.read_line_raw)
                line = line.strip()
                if not line:
                    continue
                if self.buffer.enabled and not line.startswith('view'):
                    self.buffer.captured.append(line)
                stop = await asyncio.to_thread(self.onecmd, line)
                if stop:
                    break
            except KeyboardInterrupt:
                if self.watcher.config.handle_keyboard_interrupt:
                    self.watcher.shutdown()
                    return
                else:
                    raise

    def onecmd(self, line: str):
        return dispatch(self, line)

    def printHeader(self) -> None:
        self.safePrint(res('<yellow>-----------------------------------'))
        self.safePrint(res('<yellow>-------- <aqua>ServerWatcher CLI <yellow>--------'))
        self.safePrint(res('<yellow>-----------------------------------'))
        self.safePrint('\n')


# stats command
@command('stats')
def stats(self: WatcherCLI, parsed: ParsedArgs):
    pass


@stats.child('get')
def stats_get(self: WatcherCLI, stat: str, **kwargs):
    rounding = kwargs['rounding']
    mode = kwargs['mode']
    raw = kwargs['raw']
    formatted = kwargs['formatted']
    no_formatted = kwargs['no_formatted']

    self.watcher.server.refresh()

    gb = not raw()
    if formatted():
        fmt = True
    elif no_formatted():
        fmt = False
    else:
        fmt = True

    unit = ''
    match stat:
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
def rounding(value: int):
    return value


@stats.get.param('mode', type=str, default='current')
def mode(value: str):
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


# view command
@command('view')
def view(self: WatcherCLI, parsed: ParsedArgs):
    pass


@view.child('cli')
def view_cli(self: WatcherCLI, _arg: str, **kwargs):
    self.watcher.router.disableOriginOutput()
    self.outputMode = 'cli'
    self.buffer.enabled = True
    utils.clearTerminal()
    self.printHeader()
    for msg in self.buffer.captured:
        self.safePrint(msg)


@view.child('watcher')
def view_watcher(self: WatcherCLI, _arg: str, **kwargs):
    self.watcher.router.enableOriginOutput()
    self.outputMode = 'both'
    utils.clearTerminal()
    self.printHeader()
    for msg in self.watcher.router.buffer.captured:
        self.safePrint(msg)


# clear command
@command('clear')
def clear(self: WatcherCLI, parsed: ParsedArgs):
    pass


@clear.child('buffer')
def clear_buffer(self: WatcherCLI, _arg: str, **kwargs):
    buffer = kwargs['buffer']

    if buffer():
        self.buffer.clear()

    utils.clearTerminal()
    self.printHeader()


@clear.buffer.param('buffer', type=str, default='true')
def buffer(value: str):
    return value.lower() == 'true'


# watcher command
@command('watcher')
def watcher(self: WatcherCLI, parsed: ParsedArgs):
    pass


@watcher.child('restart')
def watcher_restart(self: WatcherCLI, _arg: str, **kwargs):
    self.watcher.restart_and_wait()


@watcher.child('schedule')
def watcher_schedule(self: WatcherCLI, _arg: str, **kwargs):
    minutes = kwargs['minutes']

    val = minutes()
    if val is None:
        return self.safePrint('Usage: watcher schedule minutes')
    self.watcher.schedule_restart(val)


@watcher.child('shutdown')
def watcher_shutdown(self: WatcherCLI, _arg: str, **kwargs):
    self.watcher.shutdown()
    return True


@watcher.schedule.param('minutes', type=int, default=None)
def minutes(value: int):
    return value
