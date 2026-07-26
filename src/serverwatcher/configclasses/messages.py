from mapres import datamap, syntax

@datamap(syntax=syntax.double_braces, mode='config')
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


class fallbacks:
    prefix = '<aqua>[Server Watcher]'
    bullet = '-'

    broadcast_restart_at = '{prefix} The server will restart at {time} CDT.'

    minute_template = '{prefix} Restart in {n} minute{s}!'
    second_template = '{prefix} <red>Restarting in {n} second{s}!'

    startup = 'ServerWatcher is running!'
    status_check = 'Checking server status...'
    validation_fail = 'Validation FAILED.'
    validation_ok = 'All validation checks succeeded.'
    sampling_start = 'Starting sampling process. This should take about {duration} seconds...'
    shutdown = 'Shutting down ServerWatcher.'
    immediate_restart = 'Restarting immediately.'
    no_restart = 'The server does not need to restart.'
    scheduled = 'Restart needed, but anti-restart factors outweigh it.'
    gap_low = 'Gap {gap}. Scheduling restart in 2 hours.'
    gap_high = 'Gap {gap}. Scheduling restart in 1 hour.'

    pro_restart_splash = 'PRO-RESTART REASONS:'
    anti_restart_splash = 'ANTI-RESTART REASONS:'

    reason_restart_soon = 'The server is set to restart soon'
    reason_ram = 'RAM usage ({ram}) is higher than {threshold} GB'
    reason_cpu = 'CPU usage ({cpu}) is higher than {threshold}%'
    reason_uptime = 'Uptime {uptime} exceeds {threshold}h'
    reason_tps = 'TPS {tps} is lower than {threshold}'
    reason_low_uptime = 'Uptime {uptime} is shorter than 30m'
    reason_players = 'There {verb} {count} {plural} online'

    pro_restart_number = 'Pro-restart: '
    anti_restart_number = 'Anti-restart:'

    restart_action_sent = 'Restart action sent. Waiting...'
    server_back_online = 'Server is back online!'
    server_back_online_log = 'ServerWatcher successfully restarted the server.'
    server_failed_restart = 'Server failed to restart!'

class rules:
    pass
