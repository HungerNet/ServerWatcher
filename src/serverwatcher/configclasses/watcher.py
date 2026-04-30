from dataclasses import dataclass, field

def yaml_key(path: str, default=None):
    return field(default=default, metadata={"yaml_key": path})

@dataclass
class WatcherConfig:
    watch_interval: int = yaml_key("watch_interval")
    schedule_control: bool = yaml_key("schedule_control.enabled")
    restart_soon_id: int = yaml_key("schedule_control.restart_soon_id")

    threshold_ram: int = yaml_key("thresholds.ram")
    threshold_cpu: int = yaml_key("thresholds.cpu")
    threshold_uptime: int = yaml_key("thresholds.uptime")
    threshold_tps: float = yaml_key("thresholds.tps")

    weight_restart_soon: int = yaml_key("weights.restart_soon")
    weight_ram: int = yaml_key("weights.ram")
    weight_cpu: int = yaml_key("weights.cpu")
    weight_uptime: int = yaml_key("weights.uptime")
    weight_tps: int = yaml_key("weights.tps")

    weight_low_uptime: int = yaml_key("weights.low_uptime")
    weight_per_player: int = yaml_key("weights.per_player")

    low_gap_minutes: int = yaml_key("gaps.low_gap_minutes")
    high_gap_minutes: int = yaml_key("gaps.high_gap_minutes")

    restart_wait_seconds: int = yaml_key("restart.wait_seconds")
    restart_timeout: int = yaml_key("restart.online_timeout")
    restart_online_interval: int = yaml_key("restart.online_interval")
