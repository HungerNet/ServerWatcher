import time
from hungerlib import WebhookClient, utils

from .configmanager import config_manager
from .targetserver import TargetServer
from .router import Router
from .metricfetcher import MetricFetcher
from .evaluator import Evaluator
from .actionperformer import ActionPerformer


class ServerWatcher:
    def __init__(self, bridge_start_handler=None, bridge_restart_handler=None, bridge_kill_handler=None):
        self.config_manager = config_manager
        self.config = self.config_manager.config
        self.discordcfg = self.config_manager.discordcfg
        self.env = self.config_manager.env
        self.watchercfg = self.config_manager.watchercfg
        self.evaluatorcfg = self.config_manager.evaluatorcfg

        self.target = TargetServer(
            bridge_start_handler=bridge_start_handler,
            bridge_restart_handler=bridge_restart_handler,
            bridge_kill_handler=bridge_kill_handler
        )

        self.r = Router(self.target)

        self.webhook = None
        if self.discordcfg.discord_enabled:
            self.webhook = WebhookClient(
                url=self.discordcfg.discord_url,
                token=self.discordcfg.discord_token
            )

        self.fetcher = MetricFetcher(self.target)
        self.evaluator = Evaluator(self.evaluatorcfg)
        self.action = ActionPerformer(
            server=self.target,
            router=self.r,
            webhook=self.webhook,
            config=self.watchercfg
        )
    
    def webhookSend(self, event: str, **ctx):
        if self.discordcfg.discord_enabled and self.webhook is not None:
            self.webhook.send(event=event, **ctx)

    def shutdown(self):
        self.r.info('Shutting down ServerWatcher.')
        raise SystemExit

    def startupMessages(self):
        if self.env.ptero_enabled:
            self.r.info('ServerWatcher is running!')
        utils.clearTerminal()
        self.r.info('ServerWatcher is starting...')
        self.r.debug(f"Environment: {'Pterodactyl' if self.env.ptero_enabled else 'Standalone'}")
    
    def configExistenceCheck(self):
        self.r.debug('Checking existence of configuration files...')
        if not self.config_manager.checkAllExistence():
            self.r.error('Some configuration files are missing. Generating default configs...')
            self.config_manager.generateAllConfigs(overwrite=False)
            self.r.info('Default configuration files have been generated.')
            self.r.warn('Please review and edit the configuration files as needed, then restart the application.')
            self.shutdown()
        self.r.debug('Configs exist!')
    
    def configValidation(self):
        self.r.debug('Validating configuration files...')
        self.config_manager.validateAll()

    def checkReachability(self):
        if self.env.ptero_enabled:
            self.r.info('Checking Pterodactyl reachability...')
            for i in range(5):
                if self.target.checkPtero():
                    self.r.info('Pterodactyl reachable!')
                    break
                time.sleep(5)
            else:
                self.r.fatal('Pterodactyl is not reachable or the API key is invalid!')
                self.webhookSend(event='validation_fail', server=self.config.server_name)
                return
        
        self.r.info('Checking HungerBridge reachability...')
        for i in range(5):
            if self.target.checkBridge():
                self.r.info('HungerBridge reachable!')
                break
            time.sleep(5)
        else:
            self.r.fatal('HungerBridge is not reachable or the token secret/id is invalid!')
    
    def decideAction(self, result, metrics):
        score = result['score']
        uptime = metrics['uptime']
        players = metrics['players']

        if score == 0:
            return 'none', None

        if uptime < self.evaluatorcfg.threshold_min_uptime:
            return 'none', None

        if players == 0:
            return 'restart_now', None

        gap = score
        minutes = (
            self.watchercfg.low_gap_minutes
            if gap <= self.watchercfg.threshold_low_gap
            else self.watchercfg.high_gap_minutes
        )

        return 'schedule_restart', minutes

    def run(self):
        self.startupMessages()
        self.configExistenceCheck()
        self.configValidation()
        self.checkReachability()

        while True:
            metrics = self.fetcher.snapshot(
                duration=self.evaluatorcfg.sample_duration,
                interval=self.evaluatorcfg.sample_interval,
                drop_outliers=self.evaluatorcfg.sample_outlier_drop
            )

            # handle sampling failures
            if any(metrics[k] is None for k in ('ram', 'cpu', 'uptime', 'tps', 'players')):
                self.r.error('Sampling failed — core metrics missing.')
                self.webhookSend(event='sampling_fail', server=self.config.server_name)
                time.sleep(5)
                continue

            result = self.evaluator.evaluate(metrics)

            # log reasons (minimal)
            if result['flags']:
                self.r.warn('Evaluation flags:')
                for reason in result['reasons']:
                    self.r.warn(f"- {reason}")

            action, minutes = self.decideAction(result, metrics)
            self.action.perform(action, minutes=minutes)

            # watcher interval (fallback if not defined)
            interval = getattr(self.watchercfg, 'watch_interval', 300)
            time.sleep(interval)
