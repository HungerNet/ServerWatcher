from mapres import datamap

@datamap.braces.config(recursive=True)
class WatcherConfig:
    __user_config_path__ = 'config/watcher.yaml'
    __default_config_path__ = 'defaultconfigs/watcher.yaml'

    watch_interval: int = 'watch_interval'

    sample_duration: float | int = 'sampling.duration'
    sample_interval: float | int = 'sampling.interval'
    sample_outlier_drop: int = 'sampling.drop_outliers'

    threshold_ram: int = 'thresholds.ram'
    threshold_cpu: int = 'thresholds.cpu'
    threshold_uptime: int = 'thresholds.uptime'
    threshold_tps: float = 'thresholds.tps'
    threshold_min_uptime: int = 'thresholds.min_uptime'
    threshold_low_gap: int = 'thresholds.low_gap'

    weight_restart_soon: int = 'weights.restart_soon'
    weight_ram: int = 'weights.ram'
    weight_cpu: int = 'weights.cpu'
    weight_uptime: int = 'weights.uptime'
    weight_tps: int = 'weights.tps'

    weight_low_uptime: int = 'weights.low_uptime'
    weight_per_player: int = 'weights.per_player'

    low_gap_minutes: int = 'gaps.low_gap_minutes'
    high_gap_minutes: int = 'gaps.high_gap_minutes'

    snap_minutes: list = 'snap_minutes'

    restart_wait_seconds: int = 'restart.wait_seconds'
    restart_timeout: int = 'restart.online_timeout'
    restart_online_interval: int = 'restart.online_interval'


class fallbacks:
    watch_interval = 300

    sample_duration = 5
    sample_interval = 1
    sample_outlier_drop = 1

    threshold_ram = 6
    threshold_cpu = 150
    threshold_uptime = 12
    threshold_tps = 19.5
    threshold_min_uptime = 30
    threshold_low_gap = 2

    weight_restart_soon = 3
    weight_ram = 1
    weight_cpu = 1
    weight_uptime = 1
    weight_tps = 1

    weight_low_uptime = 5
    weight_per_player = 1

    low_gap_minutes = 120
    high_gap_minutes = 60

    snap_minutes = [0, 30]

    restart_wait_seconds = 30
    restart_timeout = 120
    restart_online_interval = 2


class rules:
    threshold_ram = 'required'
    threshold_cpu = 'required'
    threshold_uptime = 'required'
    threshold_tps = 'required'

    restart_wait_seconds = 'required'
    restart_timeout = 'required'
    restart_online_interval = 'required'

    watch_interval = 'recommended'
    sample_duration = 'recommended'
    sample_interval = 'recommended'
    sample_outlier_drop = 'recommended'
    threshold_min_uptime = 'recommended'
    threshold_low_gap = 'recommended'
    snap_minutes = 'recommended'
    low_gap_minutes = 'recommended'
    high_gap_minutes = 'recommended'

    weight_restart_soon = 'optional'
    weight_ram = 'optional'
    weight_cpu = 'optional'
    weight_uptime = 'optional'
    weight_tps = 'optional'
    weight_low_uptime = 'optional'
    weight_per_player = 'optional'
