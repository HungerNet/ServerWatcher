from dataclasses import dataclass, field

@dataclass
class WatcherMessages:
    prefix: str = "<aqua>[Server Watcher]"

    # broadcast templates
    broadcast_restart_at: str = "{prefix} The server will restart at {time} CDT."

    broadcast_minute: dict = field(default_factory=lambda: {
        120: "{prefix} Restart in 2 hours!",
        60:  "{prefix} Restart in 1 hour!",
        45:  "{prefix} Restart in 45 minutes!",
        30:  "{prefix} Restart in 30 minutes!",
        15:  "{prefix} Restart in 15 minutes!",
        5:   "{prefix} Restart in 5 minutes!",
        1:   "{prefix} Restart in 1 minute!",
    })

    broadcast_second: dict = field(default_factory=lambda: {
        s: "{prefix} Restart in " + str(s) + " seconds!"
        for s in range(10, 0, -1)
    })

    # log messages
    log_start: str = "ServerWatcher is running!"
    log_validation_fail: str = "Validation FAILED"
    log_validation_ok: str = "All validation checks succeeded."
    log_immediate_restart: str = "Restarting immediately."
    log_no_restart: str = "The server does not need to restart."
    log_scheduled: str = "Restart needed, but anti-restart factors outweigh it."
    log_gap_low: str = "Gap {gap}. Scheduling restart in 2 hours."
    log_gap_high: str = "Gap {gap}. Scheduling restart in 1 hour."

    # reason messages
    reason_restart_soon: str = "The server is set to restart soon"
    reason_ram: str = "RAM usage ({ram}) is higher than {threshold} GB"
    reason_cpu: str = "CPU usage ({cpu}) is higher than {threshold}%"
    reason_uptime: str = "Uptime {uptime} exceeds {threshold}h"
    reason_tps: str = "TPS {tps} is lower than {threshold}"

    reason_low_uptime: str = "Uptime {uptime} is shorter than 30m"
    reason_players: str = "There {verb} {count} {plural} online"
