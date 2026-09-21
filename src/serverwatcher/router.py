from zoneinfo import ZoneInfo

from hungerlib import servers, MessageRouter
from mapres import MapResolver, maps

from .configmanager import config_manager
from .targetserver import TargetServer

class Router:
    def __init__(self, server: TargetServer):
        self.config_manager = config_manager
        self.config = self.config_manager.config
        self.discordcfg = self.config_manager.discordcfg
        self.env = self.config_manager.env
        self.watchercfg = self.config_manager.watchercfg

        # resolver for internal mapping
        self.resolver = MapResolver()
        self.res = self.resolver.res

        # logger name
        logger_name = self.config.logger_name if self.config.logger_name else 'ServerWatcher'

        # router using mapres
        self.router = MessageRouter(
            name=logger_name,
            Servers=[server],
            log_path=self.config.log_path,

            origin_maps=[
                maps.ascii_colors,
                maps.time(self.config.timezone),
                self.config,
                self.discordcfg,
                self.env,
                self.watchercfg,
            ],

            destination_maps=[
                maps.ascii_colors,
                maps.time(self.config.timezone),
                self.config,
                self.discordcfg,
                self.env,
                self.watchercfg,
            ],

            broadcast_maps=[
                maps.mc_colors,
                maps.time(self.config.timezone),
                self.config,
                self.discordcfg,
                self.env,
                self.watchercfg,
            ],

            file_maps=[
                maps.strip_colors,
                maps.time(self.config.timezone),
                self.config,
                self.discordcfg,
                self.env,
                self.watchercfg,
            ],

            prefix_maps=[
                maps.ascii_colors,
                maps.time(self.config.timezone),
            ],

            info_prefix=self.config.info_prefix,
            warn_prefix=self.config.warn_prefix,
            error_prefix=self.config.error_prefix,

            buffer_enabled=True,
            origin_output=True
        )

        self.router.registerLevel(
            name='debug',
            prefix=self.config.debug_prefix,
            file_method='debug',
            routes=['origin']
        )

        self.router.registerLevel(
            name='fatal',
            prefix=self.config.fatal_prefix,
            file_method='fatal',
            routes=['origin']
        )

        self.info = self.router.info
        self.warn = self.router.warn
        self.error = self.router.error
        self.fatal = self.router.fatal
        self.debug = self.router.debug
        self.broadcast = self.router.broadcast
        self.origin = self.router.origin
        self.destination = self.router.destination

        self.tz = ZoneInfo(self.config.timezone)
