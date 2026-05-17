import os
import time
from zoneinfo import ZoneInfo

from hungerlib import servers, MessageRouter, loadConfig, utils, datamap_api, mapit

from serverwatcher.configclasses.config import GlobalConfig
from serverwatcher.configclasses.messages import MessagesConfig
from serverwatcher.configclasses.watcher import WatcherConfig



class ServerWatcher:
    def __init__(self):
        self.config = loadConfig(
            "config/config.yaml",
            "/defaultconfigs/config.yaml",
            GlobalConfig
        )

        self.messages = loadConfig(
            "config/messages.yaml",
            "/defaultconfigs/messages.yaml",
            MessagesConfig
        )

        self.watcherconfig = loadConfig(
            "config/watcher.yaml",
            "/defaultconfigs/watcher.yaml",
            WatcherConfig
        )

        datamap_api.set_default_maps(
            utils.ASCII_COLOR_MAP,
            self.config,
            self.messages,
            self.watcherconfig
        )

        self.panel = servers.Panel(
            name=self.config.panel_name,
            url=self.config.panel_url,
            api_key=self.config.panel_api_key,
        )

        self.origin = servers.Generic(
            name="Origin",
            panel=self.panel,
            server_id=self.config.origin_server_id
        )

        self.server = servers.Minecraft(
            name=self.config.server_name,
            panel=self.panel,
            server_id=self.config.server_id,
            server_domain=self.config.server_domain,
            server_port=self.config.server_port,
            bridge_url=self.config.bridge_url.rstrip("/") + ":" + str(self.config.bridge_port),
            bridge_token=self.config.bridge_token,
            tpsCommand=self.config.tps_command,
        )

        logger_name = mapit(self.config.logger_name, server_name=self.config.server_name)
        
        self.router = MessageRouter(
            name=logger_name,
            Servers=[self.server],
            log_path=self.config.log_path,
        )

        self.tz = ZoneInfo(self.config.timezone)

    def shutdown(self):
        self.router.info(self.messages.shutdown)
        raise SystemExit

    def restart_and_wait(self):
        if self.watcherconfig.schedule_control:
            self.origin.disableSchedule(self.watcherconfig.restart_soon_id)

        self.server.restart()
        self.router.info(self.messages.restart_action_sent)
        time.sleep(self.watcherconfig.restart_wait_seconds)

        self.router.warn(self.messages.status_check)
        alive = utils.waitForOnline(
            self.server,
            timeout=self.watcherconfig.restart_timeout,
            interval=self.watcherconfig.restart_online_interval,
        )

        if alive:
            self.router.info(self.messages.server_back_online)
            self.router.broadcast(
                mapit(
                    self.messages.server_back_online_broadcast,
                    enable=[utils.MC_COLOR_MAP],
                    disable=[utils.ASCII_COLOR_MAP]
                )
            )
        else:
            self.router.error(self.messages.server_failed_restart)

    def schedule_restart(self, minutes):
        info = utils.snapSchedule(minimumMinutes=minutes)
        scheduled = info["scheduled"]

        local_time = scheduled.astimezone(self.tz)
        time_str = local_time.strftime("%I:%M %p")

        self.router.broadcast(
            mapit(
                self.messages.broadcast_restart_at,
                time=time_str,
                enable=[utils.MC_COLOR_MAP],
                disable=[utils.ASCII_COLOR_MAP]
            )
        )

        minute_callbacks = {
            int(k.split("_")[1]): (
                lambda msg=mapit(getattr(self.messages, k), enable=[utils.MC_COLOR_MAP], disable=[utils.ASCII_COLOR_MAP]):
                    self.router.broadcast(msg)
            )
            for k in vars(self.messages)
            if k.startswith("minute_")
        }

        second_callbacks = {
            int(k.split("_")[1]): (
                lambda msg=mapit(getattr(self.messages, k), enable=[utils.MC_COLOR_MAP], disable=[utils.ASCII_COLOR_MAP]):
                    self.router.broadcast(msg)
            )
            for k in vars(self.messages)
            if k.startswith("second_")
        }

        utils.runCountdownEvents(
            target_time=scheduled,
            minute_callbacks=minute_callbacks,
            second_callbacks=second_callbacks,
        )

    def evaluate(self):
        self.router.info("ServerWatcher is running!")

        if not utils.validateAll(self.panel, self.server):
            self.router.error(self.messages.validation_fail)
            self.shutdown()

        self.server.refresh()
        snap = utils.Snapshot(self.server, 2, True)

        pro = 0
        anti = 0
        restart_reasons = []
        no_restart_reasons = []

        if self.watcherconfig.schedule_control and self.server.getSchedule(self.watcherconfig.restart_soon_id)["is_active"]:
            restart_reasons.append(self.messages.reason_restart_soon)
            pro += self.watcherconfig.weight_restart_soon

        if snap.ram >= self.watcherconfig.threshold_ram:
            restart_reasons.append(mapit(self.messages.reason_ram, ram=snap.ram, threshold=self.watcherconfig.threshold_ram))
            pro += int(round(snap.ram, 0) - (self.watcherconfig.threshold_ram - 1))

        if snap.cpu >= self.watcherconfig.threshold_cpu:
            restart_reasons.append(mapit(self.messages.reason_cpu, cpu=snap.cpu, threshold=self.watcherconfig.threshold_cpu))
            pro += self.watcherconfig.weight_cpu

        if snap.uptime // 3600 >= self.watcherconfig.threshold_uptime:
            restart_reasons.append(
                mapit(self.messages.reason_uptime, uptime=snap.uptime_formatted, threshold=self.watcherconfig.threshold_uptime)
            )
            pro += self.watcherconfig.weight_uptime

        if (snap.tps if snap.tps is not None else 20) <= self.watcherconfig.threshold_tps:
            restart_reasons.append(mapit(self.messages.reason_tps, tps=snap.tps, threshold=self.watcherconfig.threshold_tps))
            pro += self.watcherconfig.weight_tps

        if snap.uptime // 60 < 30:
            no_restart_reasons.append(mapit(self.messages.reason_low_uptime, uptime=snap.uptime_formatted))
            anti += self.watcherconfig.weight_low_uptime

        if snap.players > 0:
            verb = "are" if snap.players != 1 else "is"
            plural = "players" if snap.players != 1 else "player"
            no_restart_reasons.append(mapit(self.messages.reason_players, verb=verb, count=snap.players, plural=plural))
            anti += snap.players * self.watcherconfig.weight_per_player

        if restart_reasons:
            self.router.warn(self.messages.pro_restart_splash)
            for r in restart_reasons:
                self.router.warn(f"{self.messages.bullet} {r}")

        if no_restart_reasons:
            self.router.warn(self.messages.anti_restart_splash)
            for r in no_restart_reasons:
                self.router.warn(f"{self.messages.bullet} {r}")

        self.router.warn(f"{self.messages.pro_restart_number} {pro}")
        self.router.warn(f"{self.messages.anti_restart_number} {anti}")

        gap = abs(pro - anti)

        if pro == 0:
            self.router.info(self.messages.no_restart)
            return

        if pro > anti and snap.players == 0:
            self.router.info(self.messages.immediate_restart)
            self.restart_and_wait()
            return

        self.router.info(self.messages.scheduled)

        if gap <= 2:
            self.router.warn(self.messages.gap_low, gap=gap)
            self.schedule_restart(self.watcherconfig.low_gap_minutes)
        else:
            self.router.warn(self.messages.gap_high, gap=gap)
            self.schedule_restart(self.watcherconfig.high_gap_minutes)

        self.restart_and_wait()

    def run(self):
        if self.config.clear_terminal:
            utils.clearTerminal()
        while True:
            if self.config.clear_terminal:
                utils.clearTerminal()
            self.evaluate()
            time.sleep(self.watcherconfig.watch_interval)
