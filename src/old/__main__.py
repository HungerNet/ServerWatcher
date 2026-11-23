from .watcher import ServerWatcher


def main() -> None:
    watcher = ServerWatcher()
    watcher.run()


if __name__ == "__main__":
    main()
