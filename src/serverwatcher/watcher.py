import os
import time
from zoneinfo import ZoneInfo

from hungerlib import Panel, HungerLogger
from hungerlib.servers import MinecraftServer, GenericServer
from hungerlib.addons import (
    clearTerminal,
    Snapshot,
    snapSchedule,
    waitForOnline,
    validateAll,
    runCountdownEvents,
    loadConfig,
)

from serverwatcher.configclasses.global_config import GlobalConfig
from serverwatcher.configclasses.messages import MessagesConfig
from serverwatcher.configclasses.watcher import WatcherConfig

from serverwatcher.validator import validate_all

validate_all()

class ServerWatcher:
    def __init__(self):

        # load configs
        self.global_cfg = loadConfig(
            "config/global.yaml",
            "/defaultconfigs/global.yaml",
            GlobalConfig
        )

        self.messages = loadConfig(
            "config/messages.yaml",
            "/defaultconfigs/messages.yaml",
            MessagesConfig
        )

        self.cfg = loadConfig(
            "config/watcher.yaml",
            "/defaultconfigs/watcher.yaml",
            WatcherConfig
        )

        # initialize panels and servers
        self.panel = Panel(
            name=self.global_cfg.panel_name,
            url=self.global_cfg.panel_url,
            api_key=self.global_cfg.panel_api_key,
        )

        self.origin = GenericServer(
            name="Origin",
            panel=self.panel,
            server_id=self.global_cfg.origin_server_id
        )

        self.server = MinecraftServer(
            name=self.global_cfg.server_name,
            panel=self.panel,
            server_id=self.global_cfg.server_id,
            server_domain=self.global_cfg.server_domain,
            server_port=self.global_cfg.server_port,
            rcon_port=self.global_cfg.rcon_port,
            rcon_password=self.global_cfg.rcon_password,
            tpsCommand=self.global_cfg.tps_command,
        )

        logger_name = self.global_cfg.logger_name.format(
            server_name=self.global_cfg.server_name
        )

        self.log = HungerLogger(
            name=logger_name,
            server=self.server,
            log_path=self.global_cfg.log_path,
            console_backspaces=self.global_cfg.console_backspaces,
        )

        self.tz = ZoneInfo(self.global_cfg.timezone)

    # utility
    def fmt(self, template: str, **kwargs):
        return template.format(prefix=self.messages.prefix, **kwargs)

    def shutdown(self):
        self.log.info(self.messages.log_shutdown)
        raise SystemExit

    # restart logic
    def restart_and_wait(self):
        if self.cfg.schedule_control:
            self.origin.disableSchedule(self.cfg.restart_soon_id)
        self.server.restart()
        self.log.info(self.messages.restart_action_sent)
        time.sleep(self.cfg.restart_wait_seconds)

        self.log.warn(self.messages.log_status_check)
        alive = waitForOnline(
            self.server,
            timeout=self.cfg.restart_online_timeout,
            interval=self.cfg.restart_online_interval,
        )

        if alive:
            self.log.info(self.messages.server_back_online)
            self.log.info(self.fmt(self.messages.server_back_online_broadcast), destination=True, origin=False, logs=False)
        else:
            self.log.error(self.messages.server_failed_restart)

    # scheduled restart
    def schedule_restart(self, minutes):
        info = snapSchedule(minimumMinutes=minutes)
        scheduled = info["scheduled"]

        local_time = scheduled.astimezone(self.tz)
        time_str = local_time.strftime("%I:%M %p")

        self.server.sendBroadcast(
            self.fmt(self.messages.broadcast_restart_at, time=time_str)
        )

        # minute_* callbacks
        minute_callbacks = {
            int(k.split("_")[1]): (
                lambda msg=self.fmt(getattr(self.messages, k)):
                    self.server.sendBroadcast(msg)
            )
            for k in vars(self.messages)
            if k.startswith("minute_")
        }

        # second_* callbacks
        second_callbacks = {
            int(k.split("_")[1]): (
                lambda msg=self.fmt(getattr(self.messages, k)):
                    self.server.sendBroadcast(msg)
            )
            for k in vars(self.messages)
            if k.startswith("second_")
        }

        runCountdownEvents(
            target_time=scheduled,
            minute_callbacks=minute_callbacks,
            second_callbacks=second_callbacks,
        )

    # evaluation logic
    def evaluate(self):
        self.log.info(self.messages.log_start)

        if not validateAll(self.panel, self.server):
            self.log.error(self.messages.log_validation_fail)
            self.shutdown()

        self.server.refresh()
        snap = Snapshot(self.server, 2, True)

        pro = 0
        anti = 0
        restart_reasons = []
        no_restart_reasons = []

        # pro-restart
        if self.cfg.schedule_control and self.server.getSchedule(self.cfg.restart_soon_id)["is_active"]:
            restart_reasons.append(self.messages.reason_restart_soon)
            pro += self.cfg.weight_restart_soon

        if snap.ram >= self.cfg.ram_threshold:
            restart_reasons.append(
                self.fmt(self.messages.reason_ram, ram=snap.ram, threshold=self.cfg.ram_threshold)
            )
            pro += int(round(snap.ram, 0) - (self.cfg.ram_threshold - 1))

        if snap.cpu >= self.cfg.cpu_threshold:
            restart_reasons.append(
                self.fmt(self.messages.reason_cpu, cpu=snap.cpu, threshold=self.cfg.cpu_threshold)
            )
            pro += self.cfg.weight_cpu

        if snap.uptime // 3600 >= self.cfg.uptime_hours_threshold:
            restart_reasons.append(
                self.fmt(self.messages.reason_uptime, uptime=snap.uptime_formatted,
                         threshold=self.cfg.uptime_hours_threshold)
            )
            pro += self.cfg.weight_uptime

        if (snap.tps if snap.tps is not None else 0) <= self.cfg.tps_threshold:
            restart_reasons.append(
                self.fmt(self.messages.reason_tps, tps=snap.tps, threshold=self.cfg.tps_threshold)
            )
            pro += self.cfg.weight_tps

        # anti-restart
        if snap.uptime // 60 < 30:
            no_restart_reasons.append(
                self.fmt(self.messages.reason_low_uptime, uptime=snap.uptime_formatted)
            )
            anti += self.cfg.weight_low_uptime

        if snap.players > 0:
            verb = "are" if snap.players != 1 else "is"
            plural = "players" if snap.players != 1 else "player"
            no_restart_reasons.append(
                self.fmt(self.messages.reason_players, verb=verb, count=snap.players, plural=plural)
            )
            anti += snap.players * self.cfg.weight_per_player

        # logging
        if restart_reasons:
            self.log.warn(f"{self.messages.pro_restart_splash}")
            for r in restart_reasons:
                self.log.warn(f"- {r}")
            self.log.warn("\n")

        if no_restart_reasons:
            self.log.warn(f"{self.messages.anti_restart_splash}")
            for r in no_restart_reasons:
                self.log.warn(f"- {r}")
            self.log.warn("\n")

        self.log.warn(f"Pro-restart:  {pro}")
        self.log.warn(f"Anti-restart: {anti}")

        gap = abs(pro - anti)

        # decision
        if pro == 0:
            self.log.info(self.messages.log_no_restart)
            return

        if pro > anti and snap.players == 0:
            self.log.info(self.messages.log_immediate_restart)
            self.restart_and_wait()
            return

        self.log.info(self.messages.log_scheduled)

        if gap <= 2:
            self.log.warn(self.fmt(self.messages.log_gap_low, gap=gap))
            self.schedule_restart(self.cfg.low_gap_minutes)
        else:
            self.log.warn(self.fmt(self.messages.log_gap_high, gap=gap))
            self.schedule_restart(self.cfg.high_gap_minutes)

        self.restart_and_wait()

    # main loop
    def run(self):
        if self.global_cfg.clear_terminal:
            clearTerminal()
        while True:
            if self.global_cfg.clear_terminal:
                clearTerminal()
            self.evaluate()
            time.sleep(self.global_cfg.watch_interval)
