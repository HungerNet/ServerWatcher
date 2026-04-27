from dataclasses import dataclass, field

@dataclass
@dataclass
class MessagesConfig:
    prefix: str
    broadcast_restart_at: str

    # minute messages
    minute_120: str
    minute_60: str
    minute_45: str
    minute_30: str
    minute_15: str
    minute_5: str
    minute_1: str

    # second messages
    second_10: str
    second_9: str
    second_8: str
    second_7: str
    second_6: str
    second_5: str
    second_4: str
    second_3: str
    second_2: str
    second_1: str

    # logging
    log_start: str
    log_status_check: str
    log_validation_fail: str
    log_validation_ok: str
    log_shutdown: str
    log_immediate_restart: str
    log_no_restart: str
    log_scheduled: str
    log_gap_low: str
    log_gap_high: str

    # reasons
    reason_restart_soon: str
    reason_ram: str
    reason_cpu: str
    reason_uptime: str
    reason_tps: str
    reason_low_uptime: str
    reason_players: str

    # restarts
    restart_action_sent: str
    server_back_online: str
    server_back_online_broadcast: str
    server_failed_restart: str
