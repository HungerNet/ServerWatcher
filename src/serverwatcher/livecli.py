from dataclasses import dataclass
import cmd
import sys
import termios
import tty
import asyncio

# ---------------------------------------------------------------------------
# DSL core
# ---------------------------------------------------------------------------

COMMANDS: dict[str, 'CommandSpec'] = {}


@dataclass
class ParamSpec:
    name: str
    type_: type
    default: object
    func: callable


@dataclass
class FlagSpec:
    name: str
    func: callable


class ChildSpec:
    def __init__(
        self,
        name,
        func,
        requires_children: bool = False,
        requires_arguments: bool = False,
        requires_params: bool = False,
        requires_flags: bool = False,
        has_arguments: bool = False,
    ):
        if has_arguments and requires_children:
            raise ValueError(
                f'Child \'{name}\' cannot both have arguments and require children'
            )

        self.name = name
        self.func = func
        self.requires_children = requires_children
        self.requires_arguments = requires_arguments
        self.requires_params = requires_params
        self.requires_flags = requires_flags
        self.has_arguments = has_arguments

        self.params: dict[str, ParamSpec] = {}
        self.flags: dict[str, FlagSpec] = {}
        self.children: dict[str, 'ChildSpec'] = {}

        self.description = getattr(func, '__description__', None)

    def param(self, name, type=str, default=None):
        def deco(func):
            pyname = name.replace('-', '_')
            self.params[pyname] = ParamSpec(name, type, default, func)
            return func
        return deco

    def flag(self, name):
        def deco(func):
            pyname = name.replace('-', '_')
            self.flags[pyname] = FlagSpec(name, func)
            return func
        return deco

    def child(self, name, **meta):
        def deco(func):
            child = ChildSpec(name, func, **meta)
            self.children[name] = child
            setattr(self, name, child)
            return child
        return deco


class CommandSpec:
    def __init__(
        self,
        name,
        func,
        requires_children: bool = False,
        requires_arguments: bool = False,
        requires_params: bool = False,
        requires_flags: bool = False,
        has_arguments: bool = False,
    ):
        if has_arguments and requires_children:
            raise ValueError(
                f'Command \'{name}\' cannot both have arguments and require children'
            )

        self.name = name
        self.func = func
        self.requires_children = requires_children
        self.requires_arguments = requires_arguments
        self.requires_params = requires_params
        self.requires_flags = requires_flags
        self.has_arguments = has_arguments

        self.children: dict[str, ChildSpec] = {}
        self.description = getattr(func, '__description__', None)

    def child(self, name, **meta):
        def deco(func):
            child = ChildSpec(name, func, **meta)
            self.children[name] = child
            setattr(self, name, child)
            return child
        return deco


class CommandDSL:
    def __call__(self, name, **meta):
        def deco(func):
            spec = CommandSpec(name, func, **meta)
            COMMANDS[name] = spec
            return spec
        return deco


command = CommandDSL()


# ---------------------------------------------------------------------------
# Help generation
# ---------------------------------------------------------------------------

def generate_help(cmd: CommandSpec) -> str:
    lines: list[str] = []
    lines.append(f'{cmd.name}: {cmd.description or 'No description'}')

    if cmd.children:
        lines.append('')
        lines.append('Children:')
        for cname, child in cmd.children.items():
            lines.append(f'  {cname}: {child.description or 'No description'}')

            if child.params:
                lines.append('    Params:')
                for pname, pspec in child.params.items():
                    lines.append(
                        f'      {pname} (CLI: {pspec.name}, type={pspec.type_.__name__}, default={pspec.default})'
                    )

            if child.flags:
                lines.append('    Flags:')
                for fname, fspec in child.flags.items():
                    lines.append(f'      --{fspec.name}')

    return '\n'.join(lines)


# ---------------------------------------------------------------------------
# Parsing + dispatch
# ---------------------------------------------------------------------------

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


def dispatch(cli, line: str):
    parsed = parse_line(line)
    if not parsed.subcommand:
        return

    cmd = COMMANDS.get(parsed.subcommand)
    if cmd is None:
        return cli.safePrint(f'Unknown command \'{parsed.subcommand}\'')

    if cmd.requires_children and not cmd.children:
        return cli.safePrint(f'Command \'{cmd.name}\' requires children')

    cmd.func()

    if not parsed.positional:
        if cmd.requires_arguments:
            return cli.safePrint(f'Command \'{cmd.name}\' requires an argument')
        return cli.safePrint('Missing subcommand')

    child_name = parsed.positional[0]
    child = cmd.children.get(child_name)
    if child is None:
        return cli.safePrint(f'Unknown subcommand \'{child_name}\'')

    arg = parsed.positional[1] if len(parsed.positional) > 1 else None

    if child.requires_arguments and arg is None:
        return cli.safePrint(f'Subcommand \'{child.name}\' requires an argument')

    # Inject param/flag functions into child.func globals
    g = child.func.__globals__

    # Params: use provided value or default, then call original func(value)
    for pname, pspec in child.params.items():
        if pname in parsed.params:
            raw_value = parsed.params[pname]
            try:
                converted = pspec.type_(raw_value)
            except Exception:
                converted = pspec.default
        else:
            converted = pspec.default

        def make_param_func(func=pspec.func, value=converted):
            def wrapper():
                return func(value)
            return wrapper

        g[pname] = make_param_func()

    # Flags: presence → True, absence → False
    for fname, fspec in child.flags.items():
        present = fname in parsed.flags

        def make_flag_func(func=fspec.func, present=present):
            def wrapper():
                return present
            return wrapper

        g[fname] = make_flag_func()

    return child.func(cli, arg)


# ---------------------------------------------------------------------------
# Base LiveCLI
# ---------------------------------------------------------------------------

class LiveCLI(cmd.Cmd):
    prompt = ''

    def safePrint(self, msg: object = '', end: str = '\n') -> None:
        print(str(msg), end=end)

    def bprint(self, msg: object) -> None:
        self.safePrint(msg)

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
            line = await asyncio.to_thread(self.read_line_raw)
            line = line.strip()
            if not line:
                continue
            stop = await asyncio.to_thread(self.onecmd, line)
            if stop:
                break

    def onecmd(self, line: str):
        return dispatch(self, line)
