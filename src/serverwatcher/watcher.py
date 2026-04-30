import os
import time
import re
from zoneinfo import ZoneInfo

from hungerlib import Panel, MessageRouter
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

from serverwatcher.configclasses.config import GlobalConfig
from serverwatcher.configclasses.messages import MessagesConfig
from serverwatcher.configclasses.watcher import WatcherConfig

from serverwatcher.validator import validate_all

validate_all()

_T_EXPR = re.compile(r"{([^{}]+)}")

def t_eval(template: str, /, **ctx):
    # evaluate inline expressions inside message templates
    def repl(match):
        expr = match.group(1).strip()
        try:
            return str(eval(expr, {}, ctx))
        except Exception as e:
            return f"<err:{e}>"
    return _T_EXPR.sub(repl, template)

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

        self.panel = Panel(
            name=self.config.panel_name,
            url=self.config.panel_url,
            api_key=self.config.panel_api_key,
        )

        self.origin = GenericServer(
            name="Origin",
            panel=self.panel,
            server_id=self.config.origin_server_id
        )

        self.server = MinecraftServer(
            name=self.config.server_name,
            panel=self.panel,
            server_id=self.config.server_id,
            server_domain=self.config.server_domain,
            server_port=self.config.server_port,
            rcon_port=self.config.rcon_port,
            rcon_password=self.config.rcon_password,
            tpsCommand=self.config.tps_command,
        )

        # formatted logger name
        logger_name = self.config.logger_name.format(
            server_name=self.config.server_name
        )

        # initialize message router
        self.router = MessageRouter(
            name=logger_name,
            server=self.server,
            log_path=self.config.log_path,
            formatter=self.fmt,
            console_backspaces=self.config.console_backspaces,
        )

        # timezone for scheduling
        self.tz = ZoneInfo(self.config.timezone)

    def fmt(self, template: str, **fmt):
        # apply t-eval formatting to templates
        return t_eval(template, self=self, **fmt)
    
    def say(self, template, level="info", **fmt):
        if not template:
            return
        self.router.say(
            template,
            level=level,
            log=self.config.enable_logging,
            **fmt
        )



    def shutdown(self):
        self.say(self.messages.shutdown)
        raise SystemExit

    def restart_and_wait(self):
        # disable schedule if configured
        if self.watcherconfig.schedule_control:
            self.origin.disableSchedule(self.watcherconfig.restart_soon_id)

        # send restart command
        self.server.restart()
        self.say(self.messages.restart_action_sent)
        time.sleep(self.watcherconfig.restart_wait_seconds)

        # check server status
        self.say(self.messages.status_check, level="warn")
        alive = waitForOnline(
            self.server,
            timeout=self.watcherconfig.restart_timeout,
            interval=self.watcherconfig.restart_online_interval,
        )

        # handle restart result
        if alive:
            self.say(self.messages.server_back_online)
            self.say(self.messages.server_back_online_broadcast, broadcast=True)
        else:
            self.say(self.messages.server_failed_restart, level="error")

    def schedule_restart(self, minutes):
        # compute scheduled restart time
        info = snapSchedule(minimumMinutes=minutes)
        scheduled = info["scheduled"]

        # format local time
        local_time = scheduled.astimezone(self.tz)
        time_str = local_time.strftime("%I:%M %p")

        # broadcast restart time
        self.router.broadcast(self.fmt(self.messages.broadcast_restart_at, time=time_str))

        # build minute callbacks
        minute_callbacks = {
            int(k.split("_")[1]): (
                lambda msg=self.fmt(getattr(self.messages, k)):
                    self.router.broadcast(msg)
            )
            for k in vars(self.messages)
            if k.startswith("minute_")
        }

        # build second callbacks
        second_callbacks = {
            int(k.split("_")[1]): (
                lambda msg=self.fmt(getattr(self.messages, k)):
                    self.router.broadcast(msg)
            )
            for k in vars(self.messages)
            if k.startswith("second_")
        }

        # run countdown events
        runCountdownEvents(
            target_time=scheduled,
            minute_callbacks=minute_callbacks,
            second_callbacks=second_callbacks,
        )

    def evaluate(self):
        # announce evaluation start
        self.say(self.messages.startup)

        # validate panel and server
        if not validateAll(self.panel, self.server):
            self.say(self.messages.validation_fail, level="error")
            self.shutdown()

        # refresh server state
        self.server.refresh()
        snap = Snapshot(self.server, 2, True)

        # scoring variables
        pro = 0
        anti = 0
        restart_reasons = []
        no_restart_reasons = []

        # check schedule flag
        if self.watcherconfig.schedule_control and self.server.getSchedule(self.watcherconfig.restart_soon_id)["is_active"]:
            restart_reasons.append(self.messages.reason_restart_soon)
            pro += self.watcherconfig.weight_restart_soon

        # check RAM threshold
        if snap.ram >= self.watcherconfig.threshold_ram:
            restart_reasons.append(self.fmt(self.messages.reason_ram, ram=snap.ram, threshold=self.watcherconfig.threshold_ram))
            pro += int(round(snap.ram, 0) - (self.watcherconfig.threshold_ram - 1))

        # check CPU threshold
        if snap.cpu >= self.watcherconfig.threshold_cpu:
            restart_reasons.append(self.fmt(self.messages.reason_cpu, cpu=snap.cpu, threshold=self.watcherconfig.threshold_cpu))
            pro += self.watcherconfig.weight_cpu

        # check uptime threshold
        if snap.uptime // 3600 >= self.watcherconfig.threshold_uptime:
            restart_reasons.append(
                self.fmt(self.messages.reason_uptime, uptime=snap.uptime_formatted,
                         threshold=self.watcherconfig.threshold_uptime)
            )
            pro += self.watcherconfig.weight_uptime

        # check TPS threshold
        if (snap.tps if snap.tps is not None else 20) <= self.watcherconfig.threshold_tps:
            restart_reasons.append(self.fmt(self.messages.reason_tps, tps=snap.tps, threshold=self.watcherconfig.threshold_tps))
            pro += self.watcherconfig.weight_tps

        # check low uptime penalty
        if snap.uptime // 60 < 30:
            no_restart_reasons.append(self.fmt(self.messages.reason_low_uptime, uptime=snap.uptime_formatted))
            anti += self.watcherconfig.weight_low_uptime

        # check player count penalty
        if snap.players > 0:
            verb = "are" if snap.players != 1 else "is"
            plural = "players" if snap.players != 1 else "player"
            no_restart_reasons.append(self.fmt(self.messages.reason_players, verb=verb, count=snap.players, plural=plural))
            anti += snap.players * self.watcherconfig.weight_per_player

        # output pro-restart reasons
        if restart_reasons:
            self.say(self.messages.pro_restart_splash, level="warn")
            for r in restart_reasons:
                self.say(f"{self.messages.bullet} {r}", level="warn")

        # output anti-restart reasons
        if no_restart_reasons:
            self.say(self.messages.anti_restart_splash, level="warn")
            for r in no_restart_reasons:
                self.say(f"{self.messages.bullet} {r}", level="warn")

        # output scores
        self.say(f"{self.messages.pro_restart_number} {pro}", level="warn")
        self.say(f"{self.messages.anti_restart_number} {anti}", level="warn")

        # compute gap
        gap = abs(pro - anti)

        # no restart case
        if pro == 0:
            self.say(self.messages.no_restart)
            return

        # immediate restart case
        if pro > anti and snap.players == 0:
            self.say(self.messages.immediate_restart)
            self.restart_and_wait()
            return

        # scheduled restart case
        self.say(self.messages.scheduled)

        # choose schedule window
        if gap <= 2:
            self.say(self.messages.gap_low, level="warn", gap=gap)
            self.schedule_restart(self.watcherconfig.low_gap_minutes)
        else:
            self.say(self.messages.gap_high, level="warn", gap=gap)
            self.schedule_restart(self.watcherconfig.high_gap_minutes)

        # perform restart
        self.restart_and_wait()


    # main loop
    def run(self):
        if self.config.clear_terminal:
            clearTerminal()
        while True:
            if self.config.clear_terminal:
                clearTerminal()
            self.evaluate()
            time.sleep(self.config.watch_interval)
