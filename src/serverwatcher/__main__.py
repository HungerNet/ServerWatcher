from mapres import rprint, setGlobalMaps, ascii_colors
import time
import asyncio
import threading
from .watchercli import WatcherCLI

from hungerlib.validator import (
    ValidationError,
    FatalError,
    TypeMismatchError,
    FallbackError,
    RecommendedError,
)

from .watcher import ServerWatcher
from .validator import validate_all


# mapres setup
setGlobalMaps(ascii_colors)

# pretty printer for validator reports
def pretty_report(report: str) -> str:
    lines = report.splitlines()
    out = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('errors:'):
            out.append('<red>Errors:')
            continue
        if stripped.startswith('recommended:'):
            out.append('<yellow>Recommended:')
            continue
        if stripped.startswith('fallbacks:'):
            out.append('<yellow>Fallbacks:')
            continue
        if stripped.startswith('warnings:'):
            out.append('<aqua>Warnings:')
            continue
        if stripped.startswith('- '):
            out.append(f'  {stripped}')
            continue
        out.append(line)
    return '\n'.join(out)

# main function
def main():
    try:
        validate_all()

    except FatalError as e:
        rprint('<bold><red>FATAL CONFIG ERROR:')
        rprint(pretty_report(e.report))
        rprint('\nIt looks like ServerWatcher is not configured yet.')
        rprint('<aqua>Please edit your config files in config/ and try again.')
        return

    except TypeMismatchError as e:
        rprint('<bold><red>TYPE MISMATCH ERROR:')
        rprint(pretty_report(e.report))
        rprint('\nYour configuration contains values of the wrong type.')
        rprint('<aqua>Please fix your config files and try again.')
        return

    except FallbackError as e:
        rprint('<bold><yellow>FALLBACKS IN USE:')
        rprint(pretty_report(e.report))
        rprint('\nIt looks like you have not configured ServerWatcher yet.')
        rprint('<aqua>Please edit your config files in config/ and try again.')
        return

    except RecommendedError as e:
        rprint('<bold><yellow>RECOMMENDED KEYS MISSING:')
        rprint(pretty_report(e.report))
        rprint('\nYour configuration is missing recommended keys.')
        rprint('<aqua>Continuing in 5 seconds...')
        time.sleep(5)

    except ValidationError as e:
        rprint('<bold><red>CONFIG ERROR:')
        rprint(pretty_report(e.report))
        rprint('\nYour configuration is invalid.')
        rprint('<aqua>Please edit your config files and try again.')
        return

    except Exception as e:
        rprint('<bold><red>UNEXPECTED ERROR:')
        rprint(str(e))
        rprint('\nSomething went wrong before ServerWatcher could start.')
        rprint('<aqua>Please check your configuration and environment.')
        return

    # Start watcher thread
    watcher = ServerWatcher()
    threading.Thread(target=watcher.run, daemon=True).start()

    cli = WatcherCLI(watcher)
    asyncio.run(cli.run())

if __name__ == '__main__':
    main()
