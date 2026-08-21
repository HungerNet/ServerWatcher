from dataclasses import dataclass
import cmd
import sys
import termios
import tty
import asyncio
import inspect

COMMANDS = {}

@dataclass
class ParamSpec:
    name: str
    type_: type
    default: object
    func: callable
    desc: str | None

@dataclass
class FlagSpec:
    name: str
    func: callable
    desc: str | None

@dataclass
class ArgMeta:
    name: str
    params: list[str]
    flags: list[str]
    required_params: set[str]
    required_flags: set[str]

class ChildSpec:
    def __init__(self, parent, name, func):
        self.parent = parent
        self.name = name
        self.func = func
        self.params = {}
        self.flags = {}
        self.args_meta = {}
        self.desc = self._doc(func)
        self._extract_args_block()
        self._parse_args_meta()
        self._infer_arg_requirement()

    def _doc(self, f):
        d = f.__doc__
        return d.strip().splitlines()[0].strip() if d else None

    def _extract_args_block(self):
        src = inspect.getsource(self.func)
        lines = src.splitlines()
        block = []
        in_block = False
        for line in lines:
            s = line.strip()
            if s.startswith('__args__'):
                in_block = True
                continue
            if in_block:
                if s.startswith("'''") or s.startswith('"""'):
                    if not block:
                        continue
                    else:
                        break
                block.append(line)
        if block:
            raw = '\n'.join(l.strip() for l in block)
            setattr(self.func, '__args__', raw)

    def _parse_args_meta(self):
        raw = getattr(self.func, '__args__', None)
        if not raw:
            return
        for line in raw.splitlines():
            s = line.strip()
            if not s:
                continue
            if ':' in s:
                arg, rest = s.split(':', 1)
                arg = arg.strip()
                tokens = [t.strip() for t in rest.split(',') if t.strip()]
            else:
                arg = s
                tokens = []
            params = []
            flags = []
            req_p = set()
            req_f = set()
            for t in tokens:
                required = True
                if t.startswith('[') and t.endswith(']'):
                    required = False
                    t = t[1:-1].strip()
                if t.startswith('--'):
                    f = t[2:]
                    flags.append(f)
                    if required:
                        req_f.add(f)
                else:
                    params.append(t)
                    if required:
                        req_p.add(t)
            self.args_meta[arg] = ArgMeta(arg, params, flags, req_p, req_f)

    def _infer_arg_requirement(self):
        sig = inspect.signature(self.func)
        ps = list(sig.parameters.values())
        if len(ps) == 1:
            self.requires_arg = False
            self.optional_arg = False
        elif len(ps) == 2:
            p = ps[1]
            if p.default is inspect._empty:
                self.requires_arg = True
                self.optional_arg = False
            else:
                self.requires_arg = False
                self.optional_arg = True
        else:
            self.requires_arg = False
            self.optional_arg = False

    def param(self, name, type=str, default=None):
        def deco(f):
            py = name.replace('-', '_')
            d = f.__doc__.strip().splitlines()[0].strip() if f.__doc__ else None
            self.params[py] = ParamSpec(name, type, default, f, d)
            return f
        return deco

    def flag(self, name):
        def deco(f):
            py = name.replace('-', '_')
            d = f.__doc__.strip().splitlines()[0].strip() if f.__doc__ else None
            self.flags[py] = FlagSpec(name, f, d)
            return f
        return deco

class CommandSpec:
    def __init__(self, name, func):
        self.name = name
        self.func = func
        self.children = {}
        self.params = {}
        self.flags = {}
        self.desc = self._doc(func)
        self.is_namespace = self._infer_namespace()

    def _doc(self, f):
        d = f.__doc__
        return d.strip().splitlines()[0].strip() if d else None

    def _infer_namespace(self):
        src = inspect.getsource(self.func)
        lines = src.splitlines()

        stripped = []
        for line in lines[1:]:
            s = line.strip()
            if not s:
                continue
            if s == 'pass':
                continue
            if s.startswith(("'''", '"""')) or s.endswith(("'''", '"""')):
                continue
            stripped.append(s)
        return stripped == []

    def param(self, name, type=str, default=None):
        def deco(f):
            py = name.replace('-', '_')
            d = f.__doc__.strip().splitlines()[0].strip() if f.__doc__ else None
            self.params[py] = ParamSpec(name, type, default, f, d)
            return f
        return deco

    def flag(self, name):
        def deco(f):
            py = name.replace('-', '_')
            d = f.__doc__.strip().splitlines()[0].strip() if f.__doc__ else None
            self.flags[py] = FlagSpec(name, f, d)
            return f
        return deco

    def child(self, name):
        def deco(f):
            c = ChildSpec(self, name, f)
            self.children[name] = c
            setattr(self, name, c)
            return c
        return deco

class CommandDSL:
    def __call__(self, name):
        def deco(f):
            spec = CommandSpec(name, f)
            COMMANDS[name] = spec
            return spec
        return deco

command = CommandDSL()

@dataclass
class ParsedArgs:
    sub: str | None
    pos: list[str]
    flags: dict[str, bool]
    params: dict[str, str]

def parse_line(raw):
    raw = raw.strip()
    if not raw:
        return ParsedArgs(None, [], {}, {})
    parts = raw.split()
    sub = parts[0]
    pos = []
    flags = {}
    params = {}
    for t in parts[1:]:
        if t.startswith('--'):
            flags[t[2:]] = True
        elif ':' in t:
            k, v = t.split(':', 1)
            params[k.lower()] = v
        else:
            pos.append(t)
    return ParsedArgs(sub, pos, flags, params)

def help_command(cmd):
    lines = []
    d = cmd.desc or 'No description'
    lines.append(f'{cmd.name}: {d}')

    if cmd.children:
        if cmd.is_namespace and len(cmd.children) > 0:
            u = f'Usage: {cmd.name} <child>'
        else:
            u = f'Usage: {cmd.name} [child]'
    else:
        u = f'Usage: {cmd.name}'

    if cmd.flags:
        u += ' [--flags]'

    lines.append(u)

    if cmd.flags:
        lines.append('')
        lines.append('\0    Flags:')
        for n, fs in cmd.flags.items():
            d = fs.desc or 'No description'
            lines.append(f'\0        --{fs.name}: {d}')

    if cmd.children:
        lines.append('')
        lines.append('\0    Children:')
        for n, c in cmd.children.items():
            cd = c.desc or 'No description'
            lines.append(f'\0        {n}: {cd}')

    return '\n'.join(lines)

def help_child(child):
    lines = []
    d = child.desc or 'No description'
    p = child.parent.name
    lines.append(f'{child.name}: {d}')
    u = f'Usage: {p} {child.name}'
    if child.requires_arg:
        u += ' <arg>'
    elif child.optional_arg:
        u += ' [arg]'
    if child.params:
        u += ' [params]'
    if child.flags:
        u += ' [--flags]'
    lines.append(u)
    if child.args_meta:
        lines.append('')
        lines.append('\0    Args:')
        for a, m in child.args_meta.items():
            parts = [a]
            for pn in m.params:
                parts.append(f'[{pn}]')
            for fn in m.flags:
                parts.append(f'[--{fn}]')
            lines.append('\0        ' + ' '.join(parts))
    if child.params:
        lines.append('')
        lines.append('\0    Params:')
        for n, ps in child.params.items():
            t = ps.type_.__name__
            d = ps.desc or 'No description'
            lines.append(f'\0        {n} (type={t}, default={ps.default}): {d}')
    if child.flags:
        lines.append('')
        lines.append('\0    Flags:')
        for n, fs in child.flags.items():
            d = fs.desc or 'No description'
            lines.append(f'\0        --{fs.name}: {d}')
    return '\n'.join(lines)

def help_arg(child, meta):
    lines = []
    p = child.parent.name
    a = meta.name
    lines.append(f'{a}: Retrieve and print the {a} of the server')
    u = f'Usage: {p} {child.name} {a}'
    req = []
    opt = []
    for pn in meta.params:
        ps = child.params.get(pn)
        t = ps.type_.__name__ if ps else 'str'
        if pn in meta.required_params:
            req.append(f'<{pn}:{t}>')
        else:
            opt.append(f'[{pn}:{t}]')
    if req:
        u += ' ' + ' '.join(req)
    if opt:
        u += ' ' + ' '.join(opt)
    if meta.flags:
        u += ' [--flags]'
    lines.append(u)
    if meta.params:
        lines.append('')
        lines.append('\0    Params:')
        for pn in meta.params:
            ps = child.params.get(pn)
            if not ps:
                continue
            t = ps.type_.__name__
            d = ps.desc or 'No description'
            lines.append(f'\0        {pn} (type={t}, default={ps.default}): {d}')
    if meta.flags:
        lines.append('')
        lines.append('\0    Flags:')
        for fn in meta.flags:
            fs = child.flags.get(fn)
            if not fs:
                continue
            d = fs.desc or 'No description'
            lines.append(f'\0        --{fn}: {d}')
    return '\n'.join(lines)

def dispatch(cli, line):
    p = parse_line(line)
    if not p.sub:
        return
    cmd = COMMANDS.get(p.sub)
    if not cmd:
        return cli.safePrint(f'Unknown command {p.sub}')
    if 'help' in p.flags and not p.pos:
        return cli.safePrint(help_command(cmd))
    if cmd.children:
        if not p.pos:
            return cli.safePrint('Missing subcommand')
    else:
        return cmd.func(cli)
    cname = p.pos[0]
    child = cmd.children.get(cname)
    if not child:
        return cli.safePrint(f'Unknown subcommand {cname}')
    if 'help' in p.flags and len(p.pos) == 1:
        return cli.safePrint(help_child(child))
    if 'help' in p.flags and len(p.pos) >= 2:
        an = p.pos[1]
        meta = child.args_meta.get(an)
        if not meta:
            return cli.safePrint(f'Unknown argument {an}')
        return cli.safePrint(help_arg(child, meta))
    arg = p.pos[1] if len(p.pos) > 1 else None
    if child.requires_arg and arg is None:
        return cli.safePrint(f'Subcommand {child.name} requires an argument')
    g = child.func.__globals__
    for n, ps in child.params.items():
        if n in p.params:
            try:
                v = ps.type_(p.params[n])
            except:
                v = ps.default
        else:
            v = ps.default
        def wrap(f=ps.func, val=v):
            def w():
                return f(val)
            return w
        g[n] = wrap()
    for n, fs in child.flags.items():
        present = n in p.flags
        def wrap(f=fs.func, pr=present):
            def w():
                return pr
            return w
        g[n] = wrap()
    f = child.func
    if f.__code__.co_argcount >= 2:
        return f(cli, arg)
    return f(cli)

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
