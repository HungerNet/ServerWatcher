from dataclasses import dataclass, field

@dataclass
class MessagesConfig:
    prefix: str
    broadcast_restart_at: str
    broadcast_minute: dict = field(default_factory=dict)
    broadcast_second: dict = field(default_factory=dict)

    log_start: str = ""
    log_validation_fail: str = ""
    log_validation_ok: str = ""
    log_immediate_restart: str = ""
    log_no_restart: str = ""
    log_scheduled: str = ""
    log_gap_low: str = ""
    log_gap_high: str = ""

    reason_restart_soon: str = ""
    reason_ram: str = ""
    reason_cpu: str = ""
    reason_uptime: str = ""
    reason_tps: str = ""
    reason_low_uptime: str = ""
    reason_players: str = ""

    restart_action_sent: str = ""
    server_back_online: str = ""
    server_back_online_broadcast: str = ""
    server_failed_restart: str = ""