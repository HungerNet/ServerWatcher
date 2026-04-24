from dataclasses import dataclass

@dataclass
class WatcherConfig:
    restart_soon_schedule_id: int
    origin_disable_schedule_id: int

    ram_threshold: int
    cpu_threshold: int
    uptime_hours_threshold: int
    tps_threshold: float

    weight_restart_soon: int
    weight_ram: int
    weight_cpu: int
    weight_uptime: int
    weight_tps: int

    weight_low_uptime: int
    weight_per_player: int

    low_gap_minutes: int
    high_gap_minutes: int

    restart_wait_seconds: int
    restart_online_timeout: int
    restart_online_interval: int

    logger_name_template: str
    log_path: str
    console_backspaces: int
    timezone: str
