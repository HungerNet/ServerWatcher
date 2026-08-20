from dataclasses import dataclass
import cmd
import sys
import termios
import tty
import asyncio

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
        requires_children=False,
        requires_arguments=False,
        requires_params=False,
        requires_flags=False,
        has_arguments=False,
    ):
        if has_arguments and requires_children:
            raise ValueError(f'Child {name} cannot have arguments and children')

        self.name = name
        self.func = func
        self.requires_children = requires_children
        self.requires_arguments = requires_arguments
        self.requires_params = requires_params
        self.requires_flags = requires_flags
        self.has_arguments = has_arguments

        self.params: dict[str, ParamSpec] = {}
        self.flags: dict[str, FlagSpec] = {}
        self.children: dict[str, ChildSpec] = {}

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
        requires_children=False,
        requires_arguments=False,
        requires_params=False,
        requires_flags=False,
        has_arguments=False,
    ):
        if has_arguments and requires_children:
            raise ValueError(f'Command {name} cannot have arguments and children')

        self.name = name
        self.func = func
        self.requires_children = requires_children
        self.requires_arguments = requires_arguments
        self.requires_params = requires_params
        self.requires_flags = requires_flags
        self.has_arguments = has_arguments

        self.children: dict[str, ChildSpec] = {}
        self.params: dict[str, ParamSpec] = {}
        self.flags: dict[str, FlagSpec] = {}

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


class CommandDSL:
    def __call__(self, name, **meta):
        def deco(func):
            spec = CommandSpec(name, func, **meta)
            COMMANDS[name] = spec
            return spec
        return deco


command = CommandDSL()


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
    positional = []
    flags = {}
    params = {}

    for token in parts[1:]:
        if token.startswith('--'):
            flags[token[2:]] = True
        elif ':' in token:
            key, value = token.split(':', 1)
            params[key.lower()] = value
        else:
            positional.append(token)

    return ParsedArgs(sub, positional, flags, params)


def parse_docstring_args(doc: str | None) -> dict[str, list[tuple[str, bool]]]:
    """
    Returns {arg_name: [(item_name, required_bool), ...]}.
    Syntax:

    args:
        ram [rounding] [--raw]
        cpu [rounding]
        uptime [--raw]
        tps [rounding] [mode]
        players
        version
        platform
    """
    result: dict[str, list[tuple[str, bool]]] = {}
    if not doc:
        return result

    lines = doc.splitlines()
    in_args = False

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        if stripped.startswith('args:'):
            in_args = True
            continue

        if not in_args:
            continue

        # stop if we hit something that looks like non-args section
        if ':' not in stripped and ' ' not in stripped and stripped != 'args:':
            # still allow bare "players" etc
            parts = stripped.split()
        else:
            parts = stripped.split()

        if not parts:
            continue

        name = parts[0]
        items: list[tuple[str, bool]] = []

        for token in parts[1:]:
            required = True
            if token.startswith('[') and token.endswith(']'):
                required = False
                token = token[1:-1]
            items.append((token, required))

        result[name] = items

    return result


def generate_help(obj):
    if isinstance(obj, CommandSpec):
        lines = []
        lines.append(f'{obj.name}: {obj.description or "No description"}')
        lines.append(f'Usage: {obj.name} [child] [arg] [--flags] [params]')

        if obj.children:
            lines.append('')
            lines.append('Children:')
            for cname, child in obj.children.items():
                lines.append(f'  {cname}: {child.description or "No description"}')

        if obj.flags:
            lines.append('')
            lines.append('Flags:')
            for fname in obj.flags:
                lines.append(f'  --{fname}')

        if obj.params:
            lines.append('')
            lines.append('Params:')
            for pname, pspec in obj.params.items():
                lines.append(f'  {pname} (type={pspec.type_.__name__}, default={pspec.default})')

        return '\n'.join(lines)

    if isinstance(obj, ChildSpec):
        lines = []
        lines.append(f'{obj.name}: {obj.description or "No description"}')
        lines.append(f'Usage: {obj.name} [arg] [--flags] [params]')

        # docstring-based args
        args_meta = parse_docstring_args(obj.func.__doc__)
        if args_meta:
            lines.append('')
            lines.append('Args:')
            for arg_name, items in args_meta.items():
                line = f'  {arg_name}'
                for item_name, required in items:
                    if required:
                        line += f' {item_name}'
                    else:
                        line += f' [{item_name}]'
                lines.append(line)

        if obj.flags:
            lines.append('')
            lines.append('Flags:')
            for fname in obj.flags:
                lines.append(f'  --{fname}')

        if obj.params:
            lines.append('')
            lines.append('Params:')
            for pname, pspec in obj.params.items():
                lines.append(f'  {pname} (type={pspec.type_.__name__}, default={pspec.default})')

        return '\n'.join(lines)

    return 'No help available'


def dispatch(cli, line: str):
    parsed = parse_line(line)
    if not parsed.subcommand:
        return

    cmd_spec = COMMANDS.get(parsed.subcommand)
    if cmd_spec is None:
        return cli.safePrint(f'Unknown command {parsed.subcommand}')

    if 'help' in parsed.flags and not parsed.positional:
        return cli.safePrint(generate_help(cmd_spec))

    cmd_spec.func()

    if not cmd_spec.children:
        if 'help' in parsed.flags:
            return cli.safePrint(generate_help(cmd_spec))
        return

    if not parsed.positional:
        return cli.safePrint('Missing subcommand')

    child_name = parsed.positional[0]
    child = cmd_spec.children.get(child_name)
    if child is None:
        return cli.safePrint(f'Unknown subcommand {child_name}')

    if 'help' in parsed.flags:
        return cli.safePrint(generate_help(child))

    arg = parsed.positional[1] if len(parsed.positional) > 1 else None

    if child.requires_arguments and arg is None:
        return cli.safePrint(f'Subcommand {child.name} requires an argument')

    g = child.func.__globals__

    # params
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

    # flags
    for fname, fspec in child.flags.items():
        present = fname in parsed.flags

        def make_flag_func(func=fspec.func, present=present):
            def wrapper():
                return present
            return wrapper

        g[fname] = make_flag_func()

    func = child.func
    argc = func.__code__.co_argcount

    if argc >= 2:
        return func(cli, arg)
    else:
        return func(cli)


class LiveCLI(cmd.Cmd):
    prompt = ''

    def safePrint(self, msg='', end='\n'):
        print(str(msg), end=end)

    def bprint(self, msg):
        self.safePrint(msg)

    def read_line_raw(self):
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            chars = []
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

    def onecmd(self, line):
        return dispatch(self, line)
