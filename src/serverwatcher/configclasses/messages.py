from dataclasses import dataclass, field

def yaml_key(name: str):
    return field(metadata={"yaml_key": name})

@dataclass
class MessagesConfig:
    prefix: str = yaml_key("prefix")

    broadcast_restart_at: str = yaml_key("broadcast_restart_at")
    bullet: str = yaml_key("bullet")

    # minute messages
    minute_120: str = yaml_key("minute_120")
    minute_60: str = yaml_key("minute_60")
    minute_45: str = yaml_key("minute_45")
    minute_30: str = yaml_key("minute_30")
    minute_15: str = yaml_key("minute_15")
    minute_5: str = yaml_key("minute_5")
    minute_1: str = yaml_key("minute_1")

    # second messages
    second_10: str = yaml_key("second_10")
    second_9: str = yaml_key("second_9")
    second_8: str = yaml_key("second_8")
    second_7: str = yaml_key("second_7")
    second_6: str = yaml_key("second_6")
    second_5: str = yaml_key("second_5")
    second_4: str = yaml_key("second_4")
    second_3: str = yaml_key("second_3")
    second_2: str = yaml_key("second_2")
    second_1: str = yaml_key("second_1")

    # logging
    log_start: str = yaml_key("log_start")
    log_status_check: str = yaml_key("log_status_check")
    log_validation_fail: str = yaml_key("log_validation_fail")
    log_validation_ok: str = yaml_key("log_validation_ok")
    log_shutdown: str = yaml_key("log_shutdown")
    log_immediate_restart: str = yaml_key("log_immediate_restart")
    log_no_restart: str = yaml_key("log_no_restart")
    log_scheduled: str = yaml_key("log_scheduled")
    log_gap_low: str = yaml_key("log_gap_low")
    log_gap_high: str = yaml_key("log_gap_high")

    # reasons
    pro_restart_splash: str = yaml_key("pro_restart_splash")
    anti_restart_splash: str = yaml_key("anti_restart_splash")

    reason_restart_soon: str = yaml_key("reason_restart_soon")
    reason_ram: str = yaml_key("reason_ram")
    reason_cpu: str = yaml_key("reason_cpu")
    reason_uptime: str = yaml_key("reason_uptime")
    reason_tps: str = yaml_key("reason_tps")
    reason_low_uptime: str = yaml_key("reason_low_uptime")
    reason_players: str = yaml_key("reason_players")

    pro_restart_number: str = yaml_key("pro_restart_number")
    anti_restart_number: str = yaml_key("anti_restart_number")

    # restarts
    restart_action_sent: str = yaml_key("restart_action_sent")
    server_back_online: str = yaml_key("server_back_online")
    server_back_online_broadcast: str = yaml_key("server_back_online_broadcast")
    server_failed_restart: str = yaml_key("server_failed_restart")
