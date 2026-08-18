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

#  ARGUMENT PARSING ENGINE
COMMANDS: dict[str, callable] = {}


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


@dataclass
class ArgSpec:
    name: str
    kind: str  # 'flag' or 'param'
    type: callable = str
    default: object = None
    func: callable | None = None
    present: bool = False
    raw_value: str | None = None

    def __call__(self):
        if not self.present:
            return self.default
        if self.kind == 'flag':
            return True
        if self.raw_value is None:
            return self.default
        return self.type(self.raw_value)


class CommandContext:
    def __init__(self, parsed: ParsedArgs):
        self.parsed = parsed
        self.arg_specs: dict[str, ArgSpec] = {}
        self.child_name: str | None = None
        self.child_func: callable | None = None

    def register_param(self, name: str, type_: callable, default: object, func: callable) -> ArgSpec:
        spec = ArgSpec(name=name, kind='param', type=type_, default=default, func=func)
        self.arg_specs[name] = spec
        return spec

    def register_flag(self, name: str, func: callable) -> ArgSpec:
        spec = ArgSpec(name=name, kind='flag', default=False, func=func)
        self.arg_specs[name] = spec
        return spec

    def register_child(self, name: str, func: callable) -> callable:
        self.child_name = name
        self.child_func = func
        return func

    def bind(self) -> None:
        for name, spec in self.arg_specs.items():
            if spec.kind == 'flag' and name in self.parsed.flags:
                spec.present = True

        for name, spec in self.arg_specs.items():
            if spec.kind == 'param' and name in self.parsed.params:
                spec.present = True
                spec.raw_value = self.parsed.params[name]

    def positional(self, index: int, default: object = None) -> object:
        try:
            return self.parsed.positional[index]
        except IndexError:
            return default


# decorators
def command(name: str):
    def decorator(func: callable):
        COMMANDS[name] = func
        return func
    return decorator


def child(name: str):
    def decorator(func: callable):
        func.__child_name__ = name
        return func
    return decorator


def param(name: str, type: callable = str, default: object = None):
    def decorator(func: callable):
        func.__arg_kind__ = 'param'
        func.__arg_name__ = name
        func.__arg_type__ = type
        func.__arg_default__ = default
        return func
    return decorator


def flag(name: str):
    def decorator(func: callable):
        func.__arg_kind__ = 'flag'
        func.__arg_name__ = name
        return func
    return decorator


# DISPATCHER
class CLIBase:
    def safePrint(self, msg: object = '', end: str = '\n') -> None:
        print(str(msg), end=end)

    def bprint(self, msg: object) -> None:
        self.safePrint(msg)


def dispatch(cli: CLIBase, line: str):
    parsed = parse_line(line)
    if not parsed.subcommand:
        return

    handler = COMMANDS.get(parsed.subcommand)
    if handler is None:
        cli.safePrint(f'Unknown command \'{parsed.subcommand}\'')
        return

    ctx = CommandContext(parsed)

    # Register decorators
    handler(cli, ctx)

    # Bind parsed values
    ctx.bind()

    # Execute child command
    if ctx.child_func:
        stat = ctx.positional(0)
        return ctx.child_func(stat)


# CLI Implementation
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


# commands
@command('stats')
def stats(self: WatcherCLI, ctx: CommandContext):

    @child('get')
    def get(stat: str):

        @param('rounding', type=int, default=2)
        def rounding(value: int) -> int:
            return value

        @param('mode', default='current')
        def mode(value: str) -> str:
            return value

        @flag('raw')
        def raw() -> bool:
            return False

        @flag('formatted')
        def formatted() -> bool:
            return True

        @flag('no-formatted')
        def no_formatted() -> bool:
            return False

        # extract specs
        r = ctx.arg_specs['rounding']
        m = ctx.arg_specs['mode']
        raw_f = ctx.arg_specs['raw']
        fmt_f = ctx.arg_specs['formatted']
        nofmt_f = ctx.arg_specs['no-formatted']

        rounding_val = r()
        mode_val = m()

        gb: bool = False if raw_f.present else True

        if fmt_f.present:
            fmt: bool = True
        elif nofmt_f.present:
            fmt = False
        else:
            fmt = True

        self.watcher.server.refresh()

        unit: str = ''
        match stat:
            case 'ram':
                value = self.watcher.server.getRAM(rounding=rounding_val, gb=gb)
                name = 'RAM'
                unit = ' GB' if gb else ' MB'
            case 'cpu':
                value = self.watcher.server.getCPU(rounding=rounding_val)
                name = 'CPU'
                unit = '%'
            case 'uptime':
                value = self.watcher.server.getUptime(formatted=fmt)
                name = 'Uptime'
                unit = '' if fmt else 'ms'
            case 'tps':
                value = self.watcher.server.getTPS(rounding=rounding_val, mode=mode_val)
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


@command('view')
def view(self: WatcherCLI, ctx: CommandContext):

    @child('cli')
    def cli_view(_):
        self.watcher.router.disableOriginOutput()
        self.outputMode = 'cli'
        self.buffer.enabled = True
        utils.clearTerminal()
        self.printHeader()
        for msg in self.buffer.captured:
            self.safePrint(msg)

    @child('watcher')
    def watcher_view(_):
        self.watcher.router.enableOriginOutput()
        self.outputMode = 'both'
        utils.clearTerminal()
        self.printHeader()
        for msg in self.watcher.router.buffer.captured:
            self.safePrint(msg)


@command('clear')
def clear(self: WatcherCLI, ctx: CommandContext):

    @param('buffer', type=str, default='true')
    def buffer_param(value: str) -> bool:
        return value.lower() == 'true'

    buf = ctx.arg_specs['buffer']()

    if buf:
        self.buffer.clear()

    utils.clearTerminal()
    self.printHeader()


@command('watcher')
def watcher(self: WatcherCLI, ctx: CommandContext):

    @child('restart')
    def restart(_):
        self.watcher.restart_and_wait()

    @child('schedule')
    def schedule(_):
        minutes = ctx.positional(1)
        if minutes is None:
            return self.safePrint('Usage: watcher schedule <minutes>')
        try:
            minutes = int(minutes)
        except ValueError:
            return self.safePrint('Minutes must be an integer')
        self.watcher.schedule_restart(minutes)

    @child('shutdown')
    def shutdown(_):
        self.watcher.shutdown()
        return True
