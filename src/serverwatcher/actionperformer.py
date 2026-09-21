import time
from zoneinfo import ZoneInfo
from hungerlib import utils


class ActionPerformer:
    '''
    Executes actions chosen by ServerWatcher:
    - restart_now
    - schedule_restart
    - none
    '''

    def __init__(self, server, router, webhook, config):
        self.server = server
        self.router = router
        self.webhook = webhook
        self.cfg = config
        self.tz = ZoneInfo(getattr(self.cfg, 'timezone', 'UTC'))

    # public entry point
    def perform(self, action: str, **ctx):
        if action == 'restart_now':
            return self._restart_now()

        if action == 'schedule_restart':
            minutes = ctx.get('minutes')
            return self._schedule_restart(minutes)

        if action == 'none':
            return self._no_action()

        raise ValueError(f'Unknown action: {action}')

    # immediate restart
    def _restart_now(self):
        self.router.info('Performing immediate restart...')
        self.webhook.send(event='restart_now')

        # send restart command
        self.server.restartServer()
        self.router.info('Restart action sent. Waiting...')
        self.webhook.send(event='restart_action_sent')

        # wait before checking status
        time.sleep(self.cfg.restart_wait_seconds)

        self.router.warn('Checking server status...')

        alive = utils.waitForOnline(
            self.server,
            timeout=self.cfg.restart_timeout,
            interval=self.cfg.restart_online_interval,
        )

        if alive:
            self.router.info('Server is back online!')
            self.router.destination('ServerWatcher successfully restarted the server.')
            self.webhook.send(event='server_back_online')
        else:
            self.router.error('Server failed to restart!')
            self.webhook.send(event='server_failed_restart')

        return alive

    # scheduled restart (with snapping)
    def _schedule_restart(self, minutes):
        self.router.info('Scheduling restart...')

        info = utils.snapSchedule(
            minimumMinutes=minutes,
            snapMinutes=tuple(sorted(self.cfg.snap_minutes))
        )
        scheduled = info['scheduled']

        local_time = scheduled.astimezone(self.tz)
        time_str = local_time.strftime('%I:%M %p')

        # broadcast restart time
        self.router.broadcast(f'[Server Watcher] The server will restart at {time_str} CDT.')
        self.webhook.send(event='restart_scheduled', time=time_str)

        # build minute + second callbacks
        minute_callbacks = self._build_minute_callbacks()
        second_callbacks = self._build_second_callbacks()

        # run countdown
        utils.runCountdownEvents(
            target_time=scheduled,
            minute_callbacks=minute_callbacks,
            second_callbacks=second_callbacks
        )

        # After countdown, perform restart
        return self._restart_now()

    # no action
    def _no_action(self):
        self.router.info('No restart required.')
        self.webhook.send(event='no_action')
        return True

    # helpers for countdown events
    def _build_minute_callbacks(self):
        '''
        Creates callbacks for minute announcements.
        Example: 'Restart in 30 minutes', 'Restart in 1 minute'
        '''
        def plural(n):
            return '' if n == 1 else 's'

        def minute_msg(n):
            return f'[Server Watcher] Restart in {n} minute{plural(n)}!'

        callbacks = {
            n: (lambda n=n: (
                self.router.broadcast(minute_msg(n + 1)),
                self.router.origin(minute_msg(n + 1))
            ))
            for n in self.cfg.snap_minutes
        }

        return callbacks

    def _build_second_callbacks(self):
        '''
        Creates callbacks for final 10-second countdown.
        '''
        def plural(n):
            return '' if n == 1 else 's'

        def second_msg(n):
            return f'[Server Watcher] Restarting in {n} second{plural(n)}!'

        callbacks = {
            n: (lambda n=n: (
                self.router.broadcast(second_msg(n)),
                self.router.origin(second_msg(n))
            ))
            for n in range(1, 11)
        }

        return callbacks
