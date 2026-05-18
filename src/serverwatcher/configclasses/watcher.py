from hungerlib import datamap, datamap_api

@datamap(syntax=datamap_api.braces, mode='config')
class WatcherConfig:
    __user_config_path__ = 'config/watcher.yaml'
    __default_config_path__ = 'defaultconfigs/watcher.yaml'

    watch_interval: int = ('watch_interval', 300)

    schedule_control: bool = ('schedule_control.enabled', False)
    restart_soon_id: int = ('schedule_control.restart_soon_id', 0)

    threshold_ram: int = ('thresholds.ram', 6)
    threshold_cpu: int = ('thresholds.cpu', 150)
    threshold_uptime: int = ('thresholds.uptime', 12)
    threshold_tps: float = ('thresholds.tps', 19.5)

    weight_restart_soon: int = ('weights.restart_soon', 3)
    weight_ram: int = ('weights.ram', 1)
    weight_cpu: int = ('weights.cpu', 1)
    weight_uptime: int = ('weights.uptime', 1)
    weight_tps: int = ('weights.tps', 1)

    weight_low_uptime: int = ('weights.low_uptime', 5)
    weight_per_player: int = ('weights.per_player', 1)

    low_gap_minutes: int = ('gaps.low_gap_minutes', 120)
    high_gap_minutes: int = ('gaps.high_gap_minutes', 60)

    restart_wait_seconds: int = ('restart.wait_seconds', 30)
    restart_timeout: int = ('restart.online_timeout', 120)
    restart_online_interval: int = ('restart.online_interval', 2)
