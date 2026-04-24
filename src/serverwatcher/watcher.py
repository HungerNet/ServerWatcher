import time
from zoneinfo import ZoneInfo
from hungerlib.addons import (
    Snapshot,
    snapSchedule,
    waitForOnline,
    validateAll,
    runCountdownEvents
)

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
