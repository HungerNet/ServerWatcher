from hungerlib import datamap, datamap_api

@datamap(syntax=datamap_api.braces, mode="config")
class WatcherConfig:
    __user_config_path__ = "config/watcher.yaml"
    __default_config_path__ = "/defaultconfigs/watcher.yaml"

    watch_interval: int = "watch_interval"
    schedule_control: bool = "schedule_control.enabled"
    restart_soon_id: int = "schedule_control.restart_soon_id"

    threshold_ram: int = "thresholds.ram"
    threshold_cpu: int = "thresholds.cpu"
    threshold_uptime: int = "thresholds.uptime"
    threshold_tps: float = "thresholds.tps"

    weight_restart_soon: int = "weights.restart_soon"
    weight_ram: int = "weights.ram"
    weight_cpu: int = "weights.cpu"
    weight_uptime: int = "weights.uptime"
    weight_tps: int = "weights.tps"

    weight_low_uptime: int = "weights.low_uptime"
    weight_per_player: int = "weights.per_player"

    low_gap_minutes: int = "gaps.low_gap_minutes"
    high_gap_minutes: int = "gaps.high_gap_minutes"

    restart_wait_seconds: int = "restart.wait_seconds"
    restart_timeout: int = "restart.online_timeout"
    restart_online_interval: int = "restart.online_interval"