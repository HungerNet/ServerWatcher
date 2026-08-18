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

# DSL core
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


class CommandContext:
    def __init__(self, parsed: ParsedArgs):
        self.parsed = parsed
        self.child_func = None

    def positional(self, index: int, default=None):
        try:
            return self.parsed.positional[index]
        except IndexError:
            return default


class CommandDSL:
    def __init__(self):
        self.registry: dict[str, callable] = {}

    def __call__(self, name: str):
        def deco(func: callable):
            self.registry[name] = func
            return func
        return deco

    def child(self, name: str):
        def deco(func: callable):
            func.__child_name__ = name
            return func
        return deco

    def param(self, name: str, type: callable = str, default: object = None):
        def deco(func: callable):
            func.__arg_kind__ = 'param'
            func.__arg_name__ = name
            func.__arg_type__ = type
            func.__arg_default__ = default
            return func
        return deco

    def flag(self, name: str):
        def deco(func: callable):
            func.__arg_kind__ = 'flag'
            func.__arg_name__ = name
            return func
        return deco


command = CommandDSL()


def bind_nested_functions(ctx: CommandContext, namespace: dict):
    for name, obj in namespace.items():
        if not callable(obj):
            continue

        # child
        if hasattr(obj, '__child_name__'):
            ctx.child_func = obj

        # param / flag
        if hasattr(obj, '__arg_kind__'):
            kind = obj.__arg_kind__
            argname = obj.__arg_name__
            default = getattr(obj, '__arg_default__', None)
            type_ = getattr(obj, '__arg_type__', str)

            if kind == 'flag':
                present = argname in ctx.parsed.flags

                def wrapper(present=present):
                    return present

                namespace[name] = wrapper

            elif kind == 'param':
                if argname in ctx.parsed.params:
                    raw = ctx.parsed.params[argname]

                    def wrapper(raw=raw, type_=type_, default=default):
                        try:
                            return type_(raw)
                        except Exception:
                            return default

                    namespace[name] = wrapper
                else:
                    def wrapper(default=default):
                        return default

                    namespace[name] = wrapper


# Dispatcher / base
class CLIBase:
    def safePrint(self, msg: object = '', end: str = '\n') -> None:
        print(str(msg), end=end)

    def bprint(self, msg: object) -> None:
        self.safePrint(msg)


def dispatch(cli: CLIBase, line: str):
    parsed = parse_line(line)
    if not parsed.subcommand:
        return

    handler = command.registry.get(parsed.subcommand)
    if handler is None:
        cli.safePrint(f'Unknown command \'{parsed.subcommand}\'')
        return

    ctx = CommandContext(parsed)
    handler(cli, ctx)

    if ctx.child_func:
        stat = ctx.positional(0)
        return ctx.child_func(stat)


# CLI implementation
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

    @command.child('get')
    def get(stat: str):

        @command.param('rounding', type=int, default=2)
        def rounding(value):
            return value

        @command.param('mode', type=str, default='current')
        def mode(value):
            return value

        @command.flag('raw')
        def raw():
            return False

        @command.flag('formatted')
        def formatted():
            return True

        @command.flag('no-formatted')
        def no_formatted():
            return False

        bind_nested_functions(ctx, locals())

        self.watcher.server.refresh()

        gb = not raw()
        fmt = formatted() if formatted() else not no_formatted()

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


@command('view')
def view(self: WatcherCLI, ctx: CommandContext):

    @command.child('cli')
    def cli_view(_stat: str):

        self.watcher.router.disableOriginOutput()
        self.outputMode = 'cli'
        self.buffer.enabled = True
        utils.clearTerminal()
        self.printHeader()
        for msg in self.buffer.captured:
            self.safePrint(msg)

    @command.child('watcher')
    def watcher_view(_stat: str):

        self.watcher.router.enableOriginOutput()
        self.outputMode = 'both'
        utils.clearTerminal()
        self.printHeader()
        for msg in self.watcher.router.buffer.captured:
            self.safePrint(msg)

    bind_nested_functions(ctx, locals())


@command('clear')
def clear(self: WatcherCLI, ctx: CommandContext):

    @command.param('buffer', type=str, default='true')
    def buffer_param(value: str):
        return value.lower() == 'true'

    bind_nested_functions(ctx, locals())

    buf = buffer_param()
    if buf:
        self.buffer.clear()

    utils.clearTerminal()
    self.printHeader()


@command('watcher')
def watcher(self: WatcherCLI, ctx: CommandContext):

    @command.child('restart')
    def restart(_stat: str):
        self.watcher.restart_and_wait()

    @command.child('schedule')
    def schedule(_stat: str):

        minutes = ctx.positional(1)
        if minutes is None:
            return self.safePrint('Usage: watcher schedule <minutes>')
        try:
            minutes = int(minutes)
        except ValueError:
            return self.safePrint('Minutes must be an integer')
        self.watcher.schedule_restart(minutes)

    @command.child('shutdown')
    def shutdown(_stat: str):
        self.watcher.shutdown()
        return True

    bind_nested_functions(ctx, locals())
