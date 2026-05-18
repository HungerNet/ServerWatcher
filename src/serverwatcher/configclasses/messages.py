from hungerlib import datamap, datamap_api

@datamap(syntax=datamap_api.braces, mode='config')
class MessagesConfig:
    __user_config_path__ = 'config/messages.yaml'
    __default_config_path__ = 'defaultconfigs/messages.yaml'

    prefix: str = ('prefix', '<aqua>[Server Watcher]')
    bullet: str = ('bullet', '-')

    broadcast_restart_at: str = ('broadcast_restart_at', '{prefix} The server will restart at {time} CDT.')

    # minute countdowns
    minute_120: str = ('broadcast_minutes.120', '{prefix} The server will restart in 2 hours.')
    minute_60:  str = ('broadcast_minutes.60', '{prefix} The server will restart in 1 hour.')
    minute_45:  str = ('broadcast_minutes.45', '{prefix} The server will restart in 45 minutes.')
    minute_30:  str = ('broadcast_minutes.30', '{prefix} The server will restart in 30 minutes.')
    minute_15:  str = ('broadcast_minutes.15', '{prefix} The server will restart in 15 minutes.')
    minute_5:   str = ('broadcast_minutes.5', '{prefix} The server will restart in 5 minutes.')
    minute_1:   str = ('broadcast_minutes.1', '{prefix} The server will restart in 1 minute.')

    # second countdowns
    second_10: str = ('broadcast_seconds.10', '{prefix} <red>The server is restarting in 10 seconds!')
    second_9:  str = ('broadcast_seconds.9', '{prefix} <red>The server is restarting in 9 seconds!')
    second_8:  str = ('broadcast_seconds.8', '{prefix} <red>The server is restarting in 8 seconds!')
    second_7:  str = ('broadcast_seconds.7', '{prefix} <red>The server is restarting in 7 seconds!')
    second_6:  str = ('broadcast_seconds.6', '{prefix} <red>The server is restarting in 6 seconds!')
    second_5:  str = ('broadcast_seconds.5', '{prefix} <red>The server is restarting in 5 seconds!')
    second_4:  str = ('broadcast_seconds.4', '{prefix} <red>The server is restarting in 4 seconds!')
    second_3:  str = ('broadcast_seconds.3', '{prefix} <red>The server is restarting in 3 seconds!')
    second_2:  str = ('broadcast_seconds.2', '{prefix} <red>The server is restarting in 2 seconds!')
    second_1:  str = ('broadcast_seconds.1', '{prefix} <red>The server is restarting in 1 second!')

    # logging
    startup: str = ('logging.startup', 'ServerWatcher is running!')
    status_check: str = ('logging.status_check', 'Checking server status...')
    validation_fail: str = ('logging.validation_fail', 'Validation FAILED.')
    validation_ok: str = ('logging.validation_ok', 'All validation checks succeeded.')
    shutdown: str = ('logging.shutdown', 'Shutting down ServerWatcher.')
    immediate_restart: str = ('logging.immediate_restart', 'Restarting immediately.')
    no_restart: str = ('logging.no_restart', 'The server does not need to restart.')
    scheduled: str = ('logging.scheduled', 'Restart needed, but anti-restart factors outweigh it.')
    gap_low: str = ('logging.gap_low', 'Gap {gap}. Scheduling restart in 2 hours.')
    gap_high: str = ('logging.gap_high', 'Gap {gap}. Scheduling restart in 1 hour.')

    # reason splashes
    pro_restart_splash: str = ('reasons.pro_splash', 'PRO-RESTART REASONS:')
    anti_restart_splash: str = ('reasons.anti_splash', 'ANTI-RESTART REASONS:')

    # individual reasons
    reason_restart_soon: str = ('reasons.restart_soon', 'The server is set to restart soon')
    reason_ram: str = ('reasons.ram', 'RAM usage ({ram}) is higher than {threshold} GB')
    reason_cpu: str = ('reasons.cpu', 'CPU usage ({cpu}) is higher than {threshold}%')
    reason_uptime: str = ('reasons.uptime', 'Uptime {uptime} exceeds {threshold}h')
    reason_tps: str = ('reasons.tps', 'TPS {tps} is lower than {threshold}')
    reason_low_uptime: str = ('reasons.low_uptime', 'Uptime {uptime} is shorter than 30m')
    reason_players: str = ('reasons.players', 'There {verb} {count} {plural} online')

    pro_restart_number: str = ('reasons.pro_restart_number', 'Pro-restart: ')
    anti_restart_number: str = ('reasons.anti_restart_number', 'Anti-restart:')

    # restart events
    restart_action_sent: str = ('restarts.restart_action_sent', 'Restart action sent. Waiting...')
    server_back_online: str = ('restarts.back_online', 'Server is back online!')
    server_back_online_broadcast: str = ('restarts.back_online_broadcast', '{prefix} <green>Restart successful!')
    server_failed_restart: str = ('restarts.failed_restart', 'Server failed to restart!')
