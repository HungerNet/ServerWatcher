from .watcher import ServerWatcher
from .validator import validate_all
from hungerlib.validator import (
    ValidationError,
    FatalError,
    TypeMismatchError,
    FallbackError,
    RecommendedError,
)
import time

def main():
    try:
        validate_all()

    except FatalError as e:
        print('❌ FATAL CONFIG ERROR:')
        print(e)
        print('\nIt looks like ServerWatcher is not configured yet.')
        print('Please edit your config files in config/ and try again.')
        return

    except TypeMismatchError as e:
        print('❌ TYPE MISMATCH ERROR:')
        print(e)
        print('\nYour configuration contains values of the wrong type.')
        print('Please fix your config files and try again.')
        return

    except FallbackError as e:
        print('⚠️ FALLBACKS IN USE:')
        print(e)
        print('\nIt looks like you have not configured ServerWatcher yet.')
        print('Please edit your config files in config/ and try again.')
        return

    except RecommendedError as e:
        print('⚠️ RECOMMENDED KEYS MISSING:')
        print(e)
        print('\nYour configuration is missing recommended keys.')
        print('Continuing in 5 seconds...')
        time.sleep(5)

    except ValidationError as e:
        print('❌ CONFIG ERROR:')
        print(e)
        print('\nYour configuration is invalid.')
        print('Please edit your config files and try again.')
        return

    except Exception as e:
        print('❌ UNEXPECTED ERROR:')
        print(e)
        print('\nSomething went wrong before ServerWatcher could start.')
        print('Please check your configuration and environment.')
        return

    # if validation passes, start ServerWatcher
    watcher = ServerWatcher()
    watcher.run()

if __name__ == '__main__':
    main()
