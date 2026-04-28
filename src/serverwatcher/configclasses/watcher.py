from dataclasses import dataclass, field

def yaml_key(path: str):
    return field(metadata={"yaml_key": path})

@dataclass
class WatcherConfig:
    schedule_control: bool = yaml_key("schedule_control.enabled")
    restart_soon_id: int = yaml_key("schedule_control.restart_soon_id")

    thresholds.ram: int = yaml_key("thresholds.ram")
    thresholds.cpu: int = yaml_key("thresholds.cpu")
    thresholds.uptime_hours: int = yaml_key("thresholds.uptime")
    thresholds.tps: float = yaml_key("thresholds.tps")

    weights.restart_soon: int = yaml_key("weights.restart_soon")
    weights.ram: int = yaml_key("weights.ram")
    weights.cpu: int = yaml_key("weights.cpu")
    weights.uptime: int = yaml_key("weights.uptime")
    weights.tps: int = yaml_key("weights.tps")

    weights.low_uptime: int = yaml_key("weights.low_uptime")
    weights.per_player: int = yaml_key("weights.per_player")

    low_gap_minutes: int = yaml_key("gaps.low_gap_minutes")
    high_gap_minutes: int = yaml_key("gaps.high_gap_minutes")

    restart.wait_seconds: int = yaml_key("restart.wait_seconds")
    restart.timeout: int = yaml_key("restart.online_timeout")
    restart.online_interval: int = yaml_key("restart.online_interval")
