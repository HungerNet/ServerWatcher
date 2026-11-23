from mapres import datamap

@datamap.braces.config(recursive=True)
class MessagesConfig:
    __user_config_path__ = 'config/messages.yaml'
    __default_config_path__ = 'defaultconfigs/messages.yaml'

    prefix: str = 'prefix'
    bullet: str = 'bullet'

    broadcast_restart_at: str = 'broadcast_restart_at'

    minute_template: str = 'broadcast_templates.minutes'
    second_template: str = 'broadcast_templates.seconds'

    startup: str = 'logging.startup'
    status_check: str = 'logging.status_check'
    validation_fail: str = 'logging.validation_fail'
    validation_ok: str = 'logging.validation_ok'
    sampling_start: str = 'logging.sampling_start'
    shutdown: str = 'logging.shutdown'
    immediate_restart: str = 'logging.immediate_restart'
    no_restart: str = 'logging.no_restart'
    scheduled: str = 'logging.scheduled'
    gap_low: str = 'logging.gap_low'
    gap_high: str = 'logging.gap_high'

    pro_restart_splash: str = 'reasons.pro_splash'
    anti_restart_splash: str = 'reasons.anti_splash'

    reason_restart_soon: str = 'reasons.restart_soon'
    reason_ram: str = 'reasons.ram'
    reason_cpu: str = 'reasons.cpu'
    reason_uptime: str = 'reasons.uptime'
    reason_tps: str = 'reasons.tps'
    reason_low_uptime: str = 'reasons.low_uptime'
    reason_players: str = 'reasons.players'

    pro_restart_number: str = 'reasons.pro_restart_number'
    anti_restart_number: str = 'reasons.anti_restart_number'

    restart_action_sent: str = 'restarts.restart_action_sent'
    server_back_online: str = 'restarts.back_online'
    server_back_online_log: str = 'restarts.back_online_log'
    server_failed_restart: str = 'restarts.failed_restart'
