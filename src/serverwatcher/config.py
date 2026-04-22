from dataclasses import dataclass

@dataclass
class WatcherConfig:
    # schedule IDs
    restart_soon_schedule_id: int = 13
    origin_disable_schedule_id: int = 11

    # thresholds
    ram_threshold: int = 6
    cpu_threshold: int = 150
    uptime_hours_threshold: int = 12
    tps_threshold: float = 19.5

    # weights (pro)
    weight_restart_soon: int = 3
    weight_ram: int = 1
    weight_cpu: int = 1
    weight_uptime: int = 1
    weight_tps: int = 1

    # weights (anti)
    weight_low_uptime: int = 5
    weight_per_player: int = 1

    # scheduling
    low_gap_minutes: int = 120
    high_gap_minutes: int = 60

    # restart timing
    restart_wait_seconds: int = 45
    restart_online_timeout: int = 120
    restart_online_interval: int = 2
