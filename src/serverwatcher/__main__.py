# serverwatcher/__main__.py

import argparse
from .watcher import ServerWatcher
from serverwatcher.validator import validate_all

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--init", action="store_true")
    args = parser.parse_args()

    if args.init:
        # Create default configs
        from .initializer import initialize
        initialize()
        return

    validate_all()
    
    watcher = ServerWatcher()
    watcher.run()

if __name__ == "__main__":
    main()