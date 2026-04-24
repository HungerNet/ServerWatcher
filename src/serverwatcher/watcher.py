import os
import time
import yaml
from zoneinfo import ZoneInfo

from hungerlib import Panel, HungerLogger
from hungerlib.addons import clearTerminal, Snapshot, snapSchedule, waitForOnline, validateAll, runCountdownEvents
from hungerlib.servers import MinecraftServer, GenericServer

# from serverwatcher import WatcherConfig, WatcherMessages


DEFAULT_CONFIG = {
    "panel": {
        "name": "My Panel",
        "url": "https://example.com",
        "api_key": "CHANGE_ME"
    },

    "origin": {
        "server_id": "CHANGE_ME"
    },

    "server": {
        "name": "My SMP",
        "server_id": "CHANGE_ME",
        "domain": "example.com",
        "port": 25565,
        "rcon_port": 25575,
        "rcon_password": "password",
        "tps_command": "ticks"
    },

    "watcher": {
        "restart_soon_schedule_id": 0,
        "origin_disable_schedule_id": 0,

        "thresholds": {
            "ram": 6,
            "cpu": 150,
            "uptime_hours": 12,
            "tps": 19.5
        },

        "weights": {
            "restart_soon": 3,
            "ram": 1,
            "cpu": 1,
            "uptime": 1,
            "tps": 1,
            "low_uptime": 5,
            "per_player": 1
        },

        "gaps": {
            "low": 120,
            "high": 60
        },

        "restart": {
            "wait_seconds": 45,
            "online_timeout": 120,
            "online_interval": 2
        }
    },

    "messages": {
        "prefix": "<gray>[Watcher]</gray>",

        "log_start": "Evaluating server health...",
        "log_validation_fail": "Validation failed!",
        "log_no_restart": "No restart needed.",
        "log_immediate_restart": "Restarting immediately...",
        "log_scheduled": "Scheduling restart...",
        "log_gap_low": "Gap is low ({gap}), using low-gap schedule.",
        "log_gap_high": "Gap is high ({gap}), using high-gap schedule.",

        "reason_restart_soon": "Restart soon schedule is active.",
        "reason_ram": "RAM {ram}GB >= threshold {threshold}GB",
        "reason_cpu": "CPU {cpu}% >= threshold {threshold}%",
        "reason_uptime": "Uptime {uptime} >= {threshold} hours",
        "reason_tps": "TPS {tps} <= threshold {threshold}",
        "reason_low_uptime": "Uptime too low ({uptime})",
        "reason_players": "There {verb} {count} {plural} online.",

        "broadcast_restart_at": "<yellow>Server restart scheduled at {time}",

        "broadcast_minute": {
            10: "<red>Restart in 10 minutes!",
            5: "<red>Restart in 5 minutes!",
            1: "<red>Restart in 1 minute!"
        },

        "broadcast_second": {
            10: "<red>Restart in 10 seconds!",
            5: "<red>Restart in 5 seconds!",
            1: "<red>Restarting now!"
        }
    }
}


def load_or_create_config(path="config.yaml"):
    if not os.path.exists(path):
        with open(path, "w") as f:
            yaml.dump(DEFAULT_CONFIG, f, sort_keys=False)
        print("Generated default config.yaml — please edit it.")
        time.sleep(2)
    with open(path, "r") as f:
        return yaml.safe_load(f)


class ServerWatcher:
    def __init__(self, server, origin, panel, logger, config, messages):
        self.server = server
        self.origin = origin
        self.panel = panel
        self.log = logger
        self.cfg = config
        self.msg = messages

    def fmt(self, template: str, **kwargs):
        return template.format(prefix=self.msg.prefix, **kwargs)

    def shutdown(self):
        self.log.info("Shutting down ServerWatcher.")
        raise SystemExit

    def restart_and_wait(self):
        self.origin.disableSchedule(self.cfg.origin_disable_schedule_id)
        self.server.restart()
        self.log.info("Restart action sent. Waiting...")
        time.sleep(self.cfg.restart_wait_seconds)

        self.log.warn("Checking server status...")
        alive = waitForOnline(
            self.server,
            timeout=self.cfg.restart_online_timeout,
            interval=self.cfg.restart_online_interval
        )

        if alive:
            self.log.info("Server is back online!")
            self.server.sendBroadcast(f'{self.msg.prefix}<green>Restart successful!')
            self.origin.enableSchedule(self.cfg.origin_disable_schedule_id)
        else:
            self.log.error("Server failed to restart!")

    def schedule_restart(self, minutes):
        info = snapSchedule(minimumMinutes=minutes)
        scheduled = info["scheduled"]

        cst = scheduled.astimezone(ZoneInfo("America/Chicago"))
        time_in_cdt = cst.strftime("%I:%M %p")

        self.server.sendBroadcast(
            self.fmt(self.msg.broadcast_restart_at, time=time_in_cdt)
        )

        minute_callbacks = {
            m: (lambda msg=self.fmt(self.msg.broadcast_minute[m]):
                self.server.sendBroadcast(msg))
            for m in self.msg.broadcast_minute
        }

        second_callbacks = {
            s: (lambda msg=self.fmt(self.msg.broadcast_second[s]):
                self.server.sendBroadcast(msg))
            for s in self.msg.broadcast_second
        }

        runCountdownEvents(
            target_time=scheduled,
            minute_callbacks=minute_callbacks,
            second_callbacks=second_callbacks
        )

    def evaluate(self):
        self.log.info(self.msg.log_start)

        if not validateAll(self.panel, self.server):
            self.log.error(self.msg.log_validation_fail)
            self.shutdown()

        self.server.refresh()
        snap = Snapshot(self.server, 2, True)

        pro = 0
        anti = 0
        restart_reasons = []
        no_restart_reasons = []

        # PRO-RESTART
        if self.server.getSchedule(self.cfg.restart_soon_schedule_id)["is_active"]:
            restart_reasons.append(self.msg.reason_restart_soon)
            pro += self.cfg.weight_restart_soon

        if snap.ram >= self.cfg.ram_threshold:
            restart_reasons.append(
                self.fmt(self.msg.reason_ram, ram=snap.ram, threshold=self.cfg.ram_threshold)
            )
            pro += round(snap.ram, 0) - 5

        if snap.cpu >= self.cfg.cpu_threshold:
            restart_reasons.append(
                self.fmt(self.msg.reason_cpu, cpu=snap.cpu, threshold=self.cfg.cpu_threshold)
            )
            pro += self.cfg.weight_cpu

        if snap.uptime // 3600 >= self.cfg.uptime_hours_threshold:
            restart_reasons.append(
                self.fmt(self.msg.reason_uptime, uptime=snap.uptime_formatted, threshold=self.cfg.uptime_hours_threshold)
            )
            pro += self.cfg.weight_uptime

        if snap.tps <= self.cfg.tps_threshold:
            restart_reasons.append(
                self.fmt(self.msg.reason_tps, tps=snap.tps, threshold=self.cfg.tps_threshold)
            )
            pro += self.cfg.weight_tps

        # ANTI-RESTART
        if snap.uptime // 60 < 30:
            no_restart_reasons.append(
                self.fmt(self.msg.reason_low_uptime, uptime=snap.uptime_formatted)
            )
            anti += self.cfg.weight_low_uptime

        if snap.players > 0:
            verb = "are" if snap.players != 1 else "is"
            plural = "players" if snap.players != 1 else "player"
            no_restart_reasons.append(
                self.fmt(self.msg.reason_players, verb=verb, count=snap.players, plural=plural)
            )
            anti += snap.players * self.cfg.weight_per_player

        # LOGGING
        for r in restart_reasons:
            self.log.warn(f"- {r}")
        for r in no_restart_reasons:
            self.log.warn(f"- {r}")

        self.log.warn(f"Pro-restart:  {pro}")
        self.log.warn(f"Anti-restart: {anti}")

        gap = abs(pro - anti)

        if pro == 0:
            self.log.info(self.msg.log_no_restart)
            return

        if pro > anti and snap.players == 0:
            self.log.info(self.msg.log_immediate_restart)
            self.restart_and_wait()
            return

        self.log.info(self.msg.log_scheduled)

        if gap <= 2:
            self.log.warn(self.fmt(self.msg.log_gap_low, gap=gap))
            self.schedule_restart(self.cfg.low_gap_minutes)
        else:
            self.log.warn(self.fmt(self.msg.log_gap_high, gap=gap))
            self.schedule_restart(self.cfg.high_gap_minutes)

        self.restart_and_wait()



# -------------------------
# MAIN
# -------------------------

cfg = load_or_create_config()

panel = Panel(**cfg["panel"])

origin = GenericServer(
    name="Origin",
    panel=panel,
    server_id=cfg["origin"]["server_id"]
)

srv = cfg["server"]
server = MinecraftServer(
    name=srv["name"],
    panel=panel,
    server_id=srv["server_id"],
    server_domain=srv["domain"],
    server_port=srv["port"],
    rcon_port=srv["rcon_port"],
    rcon_password=srv["rcon_password"],
    tpsCommand=srv["tps_command"]
)

log = HungerLogger(
    name=f"ServerWatcher-{srv['name']}",
    server=server,
    log_path="/home/container/logs/",
    console_backspaces=8
)

w = cfg["watcher"]
config = WatcherConfig(
    restart_soon_schedule_id=w["restart_soon_schedule_id"],
    origin_disable_schedule_id=w["origin_disable_schedule_id"],

    ram_threshold=w["thresholds"]["ram"],
    cpu_threshold=w["thresholds"]["cpu"],
    uptime_hours_threshold=w["thresholds"]["uptime_hours"],
    tps_threshold=w["thresholds"]["tps"],

    weight_restart_soon=w["weights"]["restart_soon"],
    weight_ram=w["weights"]["ram"],
    weight_cpu=w["weights"]["cpu"],
    weight_uptime=w["weights"]["uptime"],
    weight_tps=w["weights"]["tps"],
    weight_low_uptime=w["weights"]["low_uptime"],
    weight_per_player=w["weights"]["per_player"],

    low_gap_minutes=w["gaps"]["low"],
    high_gap_minutes=w["gaps"]["high"],

    restart_wait_seconds=w["restart"]["wait_seconds"],
    restart_online_timeout=w["restart"]["online_timeout"],
    restart_online_interval=w["restart"]["online_interval"],
)

messages = WatcherMessages(**cfg["messages"])

clearTerminal()

Watcher = ServerWatcher(server, origin, panel, log, config, messages)

while True:
    Watcher.evaluate()
    time.sleep(60)
