from dataclasses import dataclass, field

def yaml_key(name: str):
    return field(metadata={"yaml_key": name})

@dataclass
class WatcherConfig:
    schedule_control: bool = yaml_key("schedule_control")
    restart_soon_id: int = yaml_key("restart_soon_id")

    ram_threshold: int = yaml_key("ram_threshold")
    cpu_threshold: int = yaml_key("cpu_threshold")
    uptime_hours_threshold: int = yaml_key("uptime_hours_threshold")
    tps_threshold: float = yaml_key("tps_threshold")

    weight_restart_soon: int = yaml_key("weight_restart_soon")
    weight_ram: int = yaml_key("weight_ram")
    weight_cpu: int = yaml_key("weight_cpu")
    weight_uptime: int = yaml_key("weight_uptime")
    weight_tps: int = yaml_key("weight_tps")

    weight_low_uptime: int = yaml_key("weight_low_uptime")
    weight_per_player: int = yaml_key("weight_per_player")

    low_gap_minutes: int = yaml_key("low_gap_minutes")
    high_gap_minutes: int = yaml_key("high_gap_minutes")

    restart_wait_seconds: int = yaml_key("restart_wait_seconds")
    restart_online_timeout: int = yaml_key("restart_online_timeout")
    restart_online_interval: int = yaml_key("restart_online_interval")
