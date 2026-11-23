from mapres import datamap

@datamap.braces.config(recursive=True)
class WatcherConfig:
    __user_config_path__ = 'config/watcher.yaml'
    __default_config_path__ = 'defaultconfigs/watcher.yaml'

    # Restart behavior
    restart_wait_seconds: int = 'restart.wait_seconds'
    restart_timeout: int = 'restart.timeout'
    restart_online_interval: int = 'restart.online_interval'

    # Scheduling behavior
    threshold_low_gap: int = 'schedule.threshold_low_gap'
    low_gap_minutes: int = 'schedule.low_gap_minutes'
    high_gap_minutes: int = 'schedule.high_gap_minutes'
    snap_minutes: list = 'schedule.snap_minutes'
    watch_interval: int = 'watch_interval'


class fallbacks:
    restart_wait_seconds = 30
    restart_timeout = 120
    restart_online_interval = 2

    threshold_low_gap = 2
    low_gap_minutes = 120
    high_gap_minutes = 60
    snap_minutes = [0, 30]
    watch_interval = 300


class rules:
    restart_wait_seconds = 'required'
    restart_timeout = 'required'
    restart_online_interval = 'required'

    threshold_low_gap = 'recommended'
    low_gap_minutes = 'recommended'
    high_gap_minutes = 'recommended'
    snap_minutes = 'recommended'
    watch_interval = 'recommended'
