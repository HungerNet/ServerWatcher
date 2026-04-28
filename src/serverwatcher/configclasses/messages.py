from dataclasses import dataclass, field

def yaml_key(path: str):
    return field(metadata={"yaml_key": path})

@dataclass
class MessagesConfig:
    prefix: str = yaml_key("prefix")
    broadcast_restart_at: str = yaml_key("broadcast_restart_at")
    bullet: str = yaml_key("bullet")

    # minute messages
    minute_120: str = yaml_key("broadcast_minutes.120")
    minute_60: str = yaml_key("broadcast_minutes.60")
    minute_45: str = yaml_key("broadcast_minutes.45")
    minute_30: str = yaml_key("broadcast_minutes.30")
    minute_15: str = yaml_key("broadcast_minutes.15")

    # second messages
    second_10: str = yaml_key("broadcast_seconds.10")
    second_9: str = yaml_key("broadcast_seconds.9")
    second_8: str = yaml_key("broadcast_seconds.8")
    second_7: str = yaml_key("broadcast_seconds.7")
    second_6: str = yaml_key("broadcast_seconds.6")
    second_5: str = yaml_key("broadcast_seconds.5")
    second_4: str = yaml_key("broadcast_seconds.4")
    second_3: str = yaml_key("broadcast_seconds.3")
    second_2: str = yaml_key("broadcast_seconds.2")
    second_1: str = yaml_key("broadcast_seconds.1")

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
    pro_restart_splash: str = yaml_key("reasons.pro_restart_splash")
    anti_restart_splash: str = yaml_key("reasons.anti_restart_splash")

    reasons.restart_soon: str = yaml_key("reasons.restart_soon")
    reasons.ram: str = yaml_key("reasons.ram")
    reasons.cpu: str = yaml_key("reasons.cpu")
    reasons.uptime: str = yaml_key("reasons.uptime")
    reasons.tps: str = yaml_key("reasons.tps")
    reasons.low_uptime: str = yaml_key("reasons.low_uptime")
    reasons.players: str = yaml_key("reasons.players")

    pro_restart_number: str = yaml_key("reasons.pro_restart_number")
    anti_restart_number: str = yaml_key("reasons.anti_restart_number")

    # restarts
    restart_action_sent: str = yaml_key("restarts.restart_action_sent")
    server_back_online: str = yaml_key("restarts.back_online")
    server_back_online_broadcast: str = yaml_key("restarts.back_online_broadcast")
    server_failed_restart: str = yaml_key("restarts.failed_restart")
