from .watcher import ServerWatcher
from .validator import validate_all

def main():
    validate_all()
    
    watcher = ServerWatcher()
    watcher.run()

if __name__ == "__main__":
    main()