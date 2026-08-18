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


# command model
class ParamSpec:
    def __init__(self, name: str, type_: callable, default: object):
        self.name = name
        self.type = type_
        self.default = default


class FlagSpec:
    def __init__(self, name: str):
        self.name = name


class ChildSpec:
    def __init__(self, name: str, func: callable):
        self.name = name
        self.func = func
        self.params: dict[str, ParamSpec] = {}
        self.flags: dict[str, FlagSpec] = {}


class CommandSpec:
    def __init__(self, name: str, func: callable):
        self.name = name
        self.func = func
        self.children: dict[str, ChildSpec] = {}


# DSL object
class CommandDSL:
    def __init__(self):
        self.registry: dict[str, CommandSpec] = {}
        self._current_command: CommandSpec | None = None
        self._current_child: ChildSpec | None = None

    def __call__(self, name: str):
        def deco(func: callable):
            cmd = CommandSpec(name, func)
            self.registry[name] = cmd
            self._current_command = cmd
            self._current_child = None
            return func
        return deco

    def child(self, name: str):
        def deco(func: callable):
            if self._current_command is None:
                raise RuntimeError('child() used outside of a command')
            child = ChildSpec(name, func)
            self._current_command.children[name] = child
            self._current_child = child
            return func
        return deco

    def param(self, name: str, type: callable = str, default: object = None):
        def deco(func: callable):
            if self._current_child is None:
                raise RuntimeError('param() used outside of a child')
            spec = ParamSpec(name, type, default)
            self._current_child.params[name] = spec
            return func
        return deco

    def flag(self, name: str):
        def deco(func: callable):
            if self._current_child is None:
                raise RuntimeError('flag() used outside of a child')
            spec = FlagSpec(name)
            self._current_child.flags[name] = spec
            return func
        return deco


command = CommandDSL()


# base CLI
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

    cmd = command.registry.get(parsed.subcommand)
    if cmd is None:
        cli.safePrint(f'Unknown command \'{parsed.subcommand}\'')
        return

    # run command handler to allow any setup logic
    cmd.func(cli, parsed)

    # first positional selects child
    child_name = parsed.positional[0] if parsed.positional else None
    if not child_name:
        cli.safePrint('Missing subcommand')
        return

    child = cmd.children.get(child_name)
    if child is None:
        cli.safePrint(f'Unknown subcommand '{child_name}'')
        return

    # second positional is the main argument (stat, etc.)
    stat = parsed.positional[1] if len(parsed.positional) > 1 else None

    # build wrappers for params and flags
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

    # call child with stat and wrappers injected
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
    # no setup needed for stats right now
    pass


@command.child('get')
def stats_get(self: WatcherCLI, stat: str,
              rounding, mode, raw, formatted, no_formatted):

    @command.param('rounding', type=int, default=2)
    def _rounding(value):
        return value

    @command.param('mode', type=str, default='current')
    def _mode(value):
        return value

    @command.flag('raw')
    def _raw():
        return False

    @command.flag('formatted')
    def _formatted():
        return True

    @command.flag('no-formatted')
    def _no_formatted():
        return False

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


# view command
@command('view')
def view(self: WatcherCLI, parsed: ParsedArgs):
    # no setup needed for view
    pass


@command.child('cli')
def view_cli(self: WatcherCLI, _stat: str):
    self.watcher.router.disableOriginOutput()
    self.outputMode = 'cli'
    self.buffer.enabled = True
    utils.clearTerminal()
    self.printHeader()
    for msg in self.buffer.captured:
        self.safePrint(msg)


@command.child('watcher')
def view_watcher(self: WatcherCLI, _stat: str):
    self.watcher.router.enableOriginOutput()
    self.outputMode = 'both'
    utils.clearTerminal()
    self.printHeader()
    for msg in self.watcher.router.buffer.captured:
        self.safePrint(msg)


# clear command
@command('clear')
def clear(self: WatcherCLI, parsed: ParsedArgs):
    # no setup needed
    pass


@command.child('buffer')
def clear_buffer(self: WatcherCLI, _stat: str, buffer):
    @command.param('buffer', type=str, default='true')
    def _buffer(value: str):
        return value.lower() == 'true'

    if buffer():
        self.buffer.clear()

    utils.clearTerminal()
    self.printHeader()


# watcher command
@command('watcher')
def watcher(self: WatcherCLI, parsed: ParsedArgs):
    # no setup needed
    pass


@command.child('restart')
def watcher_restart(self: WatcherCLI, _stat: str):
    self.watcher.restart_and_wait()


@command.child('schedule')
def watcher_schedule(self: WatcherCLI, _stat: str, minutes):
    @command.param('minutes', type=int, default=None)
    def _minutes(value: int):
        return value

    val = minutes()
    if val is None:
        return self.safePrint('Usage: watcher schedule <minutes>')
    self.watcher.schedule_restart(val)


@command.child('shutdown')
def watcher_shutdown(self: WatcherCLI, _stat: str):
    self.watcher.shutdown()
    return True
