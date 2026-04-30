from dataclasses import dataclass, field

def yaml_key(path: str, default=None):
    return field(default=default, metadata={"yaml_key": path})

@dataclass
class MessagesConfig:
    prefix: str = yaml_key("prefix", default="<aqua>[Server Watcher]")
    bullet: str = yaml_key("bullet")
    
    broadcast_restart_at: str = yaml_key("broadcast_restart_at")

    # minute messages
    minute_120: str = yaml_key("broadcast_minutes.120", default="{prefix} Restart in 2 hours!")
    minute_60: str = yaml_key("broadcast_minutes.60", default="{prefix} Restart in 1 hour!")
    minute_45: str = yaml_key("broadcast_minutes.45", default="{prefix} Restart in 45 minutes!")
    minute_30: str = yaml_key("broadcast_minutes.30", default="{prefix} Restart in 30 minutes!")
    minute_15: str = yaml_key("broadcast_minutes.15", default="{prefix} Restart in 15 minutes!")
    minute_5: str = yaml_key("broadcast_minutes.5", default="{prefix} Restart in 5 minutes!")
    minute_1: str = yaml_key("broadcast_minutes.1", default="{prefix} Restart in 1 minute!")

    # second messages
    second_10: str = yaml_key("broadcast_seconds.10", default="{prefix} Restart in 10 seconds!")
    second_9:  str = yaml_key("broadcast_seconds.9",  default="{prefix} Restart in 9 seconds!")
    second_8:  str = yaml_key("broadcast_seconds.8",  default="{prefix} Restart in 8 seconds!")
    second_7:  str = yaml_key("broadcast_seconds.7",  default="{prefix} Restart in 7 seconds!")
    second_6:  str = yaml_key("broadcast_seconds.6",  default="{prefix} Restart in 6 seconds!")
    second_5:  str = yaml_key("broadcast_seconds.5",  default="{prefix} Restart in 5 seconds!")
    second_4:  str = yaml_key("broadcast_seconds.4",  default="{prefix} Restart in 4 seconds!")
    second_3:  str = yaml_key("broadcast_seconds.3",  default="{prefix} Restart in 3 seconds!")
    second_2:  str = yaml_key("broadcast_seconds.2",  default="{prefix} Restart in 2 seconds!")
    second_1:  str = yaml_key("broadcast_seconds.1",  default="{prefix} Restart in 1 second!")

    # logging
    startup: str = yaml_key("logging.startup")
    status_check: str = yaml_key("logging.status_check")
    validation_fail: str = yaml_key("logging.validation_fail")
    validation_ok: str = yaml_key("logging.validation_ok")
    shutdown: str = yaml_key("logging.shutdown")
    immediate_restart: str = yaml_key("logging.immediate_restart")
    no_restart: str = yaml_key("logging.no_restart")
    scheduled: str = yaml_key("logging.scheduled")
    gap_low: str = yaml_key("logging.gap_low")
    gap_high: str = yaml_key("logging.gap_high")

    # reasons
    pro_restart_splash: str = yaml_key("reasons.pro_splash")
    anti_restart_splash: str = yaml_key("reasons.anti_splash")

    reason_restart_soon: str = yaml_key("reasons.restart_soon")
    reason_ram: str = yaml_key("reasons.ram")
    reason_cpu: str = yaml_key("reasons.cpu")
    reason_uptime: str = yaml_key("reasons.uptime")
    reason_tps: str = yaml_key("reasons.tps")
    reason_low_uptime: str = yaml_key("reasons.low_uptime")
    reason_players: str = yaml_key("reasons.players")

    pro_restart_number: str = yaml_key("reasons.pro_restart_number")
    anti_restart_number: str = yaml_key("reasons.anti_restart_number")

    # restarts
    restart_action_sent: str = yaml_key("restarts.restart_action_sent")
    server_back_online: str = yaml_key("restarts.back_online")
    server_back_online_broadcast: str = yaml_key("restarts.back_online_broadcast")
    server_failed_restart: str = yaml_key("restarts.failed_restart")
