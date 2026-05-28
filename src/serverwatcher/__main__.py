from .watcher import ServerWatcher
from .validator import validate_all
from hungerlib.utils.exceptions import (
    ValidationError,
    FatalValidationError,
    ValidationFallbacks,
)
import time

def main():
    try:
        validate_all()

    except FatalValidationError as e:
        print("❌ FATAL CONFIG ERROR:")
        print(e)
        return  # fully cancel

    except ValidationFallbacks as e:
        print("⚠️ CONFIG DEFAULTS IN USE:")
        print(e)
        print("Continuing in 5 seconds...")
        time.sleep(5)

    except ValidationError as e:
        print("❌ CONFIG ERROR:")
        print(e)
        return  # non-fatal but still cancel

    watcher = ServerWatcher()
    watcher.run()

if __name__ == "__main__":
    main()
