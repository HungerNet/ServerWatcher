import os
import time
from zoneinfo import ZoneInfo

from hungerlib import servers, MessageRouter, loadConfig, utils
from mapres import MapResolver, maps

from serverwatcher.configclasses.config import GlobalConfig
from serverwatcher.configclasses.messages import MessagesConfig
from serverwatcher.configclasses.watcher import WatcherConfig


class ServerWatcher:
    def __init__(self):
        self.config = loadConfig(GlobalConfig)
        self.messages = loadConfig(MessagesConfig)
        self.watcherconfig = loadConfig(WatcherConfig)

        # resolver for internal mapping
        self.resolver = MapResolver()
        self.res = self.resolver.res

        # panel + server
        self.panel = servers.Panel(
            name=self.config.panel_name,
            url=self.config.panel_url,
            api_key=self.config.panel_api_key,
        )

        self.server = servers.Minecraft(
            name=self.config.server_name,
            panel=self.panel,
            server_id=self.config.server_id,
            server_domain=self.config.server_domain,
            server_port=self.config.server_port,
            bridge_port=self.config.bridge_port,
            bridge_token=self.config.bridge_token,
        )

        # logger name
        logger_name = self.res(
            self.config.logger_name,
            server_name=self.config.server_name
        )

        # router using mapres
        self.router = MessageRouter(
            name=logger_name,
            Servers=[self.server],
            log_path=self.config.log_path,

            origin_maps=[
                maps.ascii_colors,
                maps.time(self.config.timezone),
                self.config,
                self.messages,
                self.watcherconfig,
            ],

            destination_maps=[
                maps.ascii_colors,
                maps.time(self.config.timezone),
                self.config,
                self.messages,
                self.watcherconfig,
            ],

            broadcast_maps=[
                maps.mc_colors,
                maps.time(self.config.timezone),
                self.config,
                self.messages,
                self.watcherconfig,
            ],

            file_maps=[
                maps.strip_colors,
                maps.time(self.config.timezone),
                self.config,
                self.messages,
                self.watcherconfig,
            ],

            prefix_maps=[
                maps.ascii_colors,
                maps.time(self.config.timezone),
            ],

            info_prefix=self.config.info_prefix,
            warn_prefix=self.config.warn_prefix,
            error_prefix=self.config.error_prefix,
        )

        self.tz = ZoneInfo(self.config.timezone)

    def clearTerminal(self):
        if self.config.clear_terminal:
            utils.clearTerminal()

    def shutdown(self):
        self.router.info(self.messages.shutdown)
        raise SystemExit

    def restart_and_wait(self):
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
            self.router.info(self.messages.server_back_online_log)
            self.router.destination(self.messages.server_back_online)
        else:
            self.router.error(self.messages.server_failed_restart)

    def schedule_restart(self, minutes):
        info = utils.snapSchedule(
            minimumMinutes=minutes,
            snapMinutes=tuple(sorted(self.watcherconfig.snap_minutes))
        )
        scheduled = info["scheduled"]

        local_time = scheduled.astimezone(self.tz)
        time_str = local_time.strftime("%I:%M %p")

        self.router.broadcast(self.messages.broadcast_restart_at, time=time_str)

        def plural(n):
            return '' if n == 1 else 's'

        # minute message generator
        def minute_msg(n):
            raw = self.messages.minute_template
            return self.res(raw, n=n, s=plural(n), prefix=self.messages.prefix)

        # second message generator
        def second_msg(n):
            raw = self.messages.second_template
            return self.res(raw, n=n, s=plural(n), prefix=self.messages.prefix)

        # minute callbacks using template
        minute_callbacks = {
            n: (lambda n=n: (
                self.router.broadcast(minute_msg(n + 1)),
                self.router.origin(minute_msg(n + 1))
            ))
            for n in self.watcherconfig.snap_minutes
        }

        # second callbacks using template
        second_callbacks = {
            n: (lambda n=n: (
                self.router.broadcast(second_msg(n)),
                self.router.origin(second_msg(n))
            ))
            for n in range(1, 11)
        }

        utils.runCountdownEvents(
            target_time=scheduled,
            minute_callbacks=minute_callbacks,
            second_callbacks=second_callbacks
        )

    def evaluate(self):
        self.router.info("ServerWatcher is running!")
        utils.clearTerminal()

        self.router.info(self.messages.startup)

        # retry validation 5 times
        for i in range(5):
            if utils.validateAll(self.panel, self.server):
                break
            time.sleep(2)
        else:
            self.router.error(self.messages.validation_fail)
            return

        sample_duration_formatted = int(self.watcherconfig.sample_duration) if self.watcherconfig.sample_duration.is_integer() else self.watcherconfig.sample_duration
        self.router.info(self.messages.sampling_start, duration=sample_duration_formatted)
        self.server.refresh()
        snap = utils.Snapshot(self.server, duration=self.watcherconfig.sample_duration, interval=self.watcherconfig.sample_interval, drop_outliers=self.watcherconfig.sample_outlier_drop, gb=True)

        pro = 0
        anti = 0
        restart_reasons = []
        no_restart_reasons = []

        if snap.ram >= self.watcherconfig.threshold_ram:
            restart_reasons.append(self.res(self.messages.reason_ram, ram=snap.ram, threshold=self.watcherconfig.threshold_ram))
            pro += int(round(snap.ram, 0) - (self.watcherconfig.threshold_ram - 1))

        if snap.cpu >= self.watcherconfig.threshold_cpu:
            restart_reasons.append(self.res(self.messages.reason_cpu, cpu=snap.cpu, threshold=self.watcherconfig.threshold_cpu))
            pro += self.watcherconfig.weight_cpu

        if snap.uptime // 3600 >= self.watcherconfig.threshold_uptime:
            restart_reasons.append(self.res(self.messages.reason_uptime, uptime=snap.uptime_formatted, threshold=self.watcherconfig.threshold_uptime))
            pro += self.watcherconfig.weight_uptime

        if (snap.tps if snap.tps is not None else 20) <= self.watcherconfig.threshold_tps:
            restart_reasons.append(self.res(self.messages.reason_tps, tps=snap.tps, threshold=self.watcherconfig.threshold_tps))
            pro += self.watcherconfig.weight_tps

        if snap.uptime // 60 < self.watcherconfig.threshold_min_uptime:
            no_restart_reasons.append(self.res(self.messages.reason_low_uptime, uptime=snap.uptime_formatted))
            anti += self.watcherconfig.weight_low_uptime

        if snap.players > 0:
            verb = "are" if snap.players != 1 else "is"
            plural = "players" if snap.players != 1 else "player"
            no_restart_reasons.append(self.res(self.messages.reason_players, verb=verb, count=snap.players, plural=plural))
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
            # will add something here later
            return

        if pro > anti and snap.players == 0:
            self.router.info(self.messages.immediate_restart)
            self.restart_and_wait()
            return

        self.router.info(self.messages.scheduled)

        if gap <= self.watcherconfig.threshold_low_gap:
            self.router.warn(self.messages.gap_low, gap=gap)
            self.schedule_restart(self.watcherconfig.low_gap_minutes)
        else:
            self.router.warn(self.messages.gap_high, gap=gap)
            self.schedule_restart(self.watcherconfig.high_gap_minutes)

        self.restart_and_wait()

    def run(self):
        if self.config.handle_keyboard_interrupt:
            try:
                while True:
                    self.clearTerminal()
                    self.evaluate()
                    time.sleep(self.watcherconfig.watch_interval)
            except KeyboardInterrupt:
                self.shutdown()
        else:
            while True:
                self.clearTerminal()
                self.evaluate()
                time.sleep(self.watcherconfig.watch_interval)
