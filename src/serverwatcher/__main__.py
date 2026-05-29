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
        print("❌ FATAL CONFIG ERROR:")
        print(e)
        return

    except TypeMismatchError as e:
        print("❌ TYPE MISMATCH ERROR:")
        print(e)
        return

    except FallbackError as e:
        print("⚠️ FALLBACKS IN USE:")
        print(e)
        print("Continuing in 5 seconds...")
        time.sleep(5)

    except RecommendedError as e:
        print("⚠️ RECOMMENDED KEYS MISSING:")
        print(e)
        print("Continuing in 5 seconds...")
        time.sleep(5)

    except ValidationError as e:
        print("❌ CONFIG ERROR:")
        print(e)
        return

    watcher = ServerWatcher()
    watcher.run()

if __name__ == "__main__":
    main()
