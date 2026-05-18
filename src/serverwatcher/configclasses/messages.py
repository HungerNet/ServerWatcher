from hungerlib import datamap, datamap_api

@datamap(syntax=datamap_api.braces, mode="config")
class MessagesConfig:
    __user_config_path__ = "/defaultconfigs/messages.yaml"
    __default_config_path__ = "config/messages.yaml"

    prefix: str = "prefix"
    bullet: str = "bullet"

    broadcast_restart_at: str = "broadcast_restart_at"

    minute_120: str = "broadcast_minutes.120"
    minute_60: str = "broadcast_minutes.60"
    minute_45: str = "broadcast_minutes.45"
    minute_30: str = "broadcast_minutes.30"
    minute_15: str = "broadcast_minutes.15"
    minute_5:  str = "broadcast_minutes.5"
    minute_1:  str = "broadcast_minutes.1"

    second_10: str = "broadcast_seconds.10"
    second_9:  str = "broadcast_seconds.9"
    second_8:  str = "broadcast_seconds.8"
    second_7:  str = "broadcast_seconds.7"
    second_6:  str = "broadcast_seconds.6"
    second_5:  str = "broadcast_seconds.5"
    second_4:  str = "broadcast_seconds.4"
    second_3:  str = "broadcast_seconds.3"
    second_2:  str = "broadcast_seconds.2"
    second_1:  str = "broadcast_seconds.1"

    startup: str = "logging.startup"
    status_check: str = "logging.status_check"
    validation_fail: str = "logging.validation_fail"
    validation_ok: str = "logging.validation_ok"
    shutdown: str = "logging.shutdown"
    immediate_restart: str = "logging.immediate_restart"
    no_restart: str = "logging.no_restart"
    scheduled: str = "logging.scheduled"
    gap_low: str = "logging.gap_low"
    gap_high: str = "logging.gap_high"

    pro_restart_splash: str = "reasons.pro_splash"
    anti_restart_splash: str = "reasons.anti_splash"

    reason_restart_soon: str = "reasons.restart_soon"
    reason_ram: str = "reasons.ram"
    reason_cpu: str = "reasons.cpu"
    reason_uptime: str = "reasons.uptime"
    reason_tps: str = "reasons.tps"
    reason_low_uptime: str = "reasons.low_uptime"
    reason_players: str = "reasons.players"

    pro_restart_number: str = "reasons.pro_restart_number"
    anti_restart_number: str = "reasons.anti_restart_number"

    restart_action_sent: str = "restarts.restart_action_sent"
    server_back_online: str = "restarts.back_online"
    server_back_online_broadcast: str = "restarts.back_online_broadcast"
    server_failed_restart: str = "restarts.failed_restart"
