# Logging system

import os
os.environ['TZ'] = 'America/Chicago'
import time
time.tzset()

import logging
from pathlib import Path
from datetime import datetime
from hungerlib.addons import ASCII_COLOR_MAP, MC_COLOR_MAP


class HungerLogger:
    def __init__(
        self,
        name,
        server,
        log_path,
        log_destination_method='rcon',

        # backspaces
        console_backspaces=0,

        # color mapping
        file_color_map=None,
        origin_color_map=ASCII_COLOR_MAP.as_dict(),
        destination_color_map=ASCII_COLOR_MAP.as_dict(),
        mc_color_map=MC_COLOR_MAP,

        # prefixes
        info_prefix='<white>[INFO]: ',
        warn_prefix='<yellow>[WARN]: ',
        error_prefix='<red>[ERROR]: '
    ):

        self.name = name
        self.server = server
        self.log_path = Path(f'{log_path}')
        self.log_destination_method = log_destination_method

        self.console_backspaces = '\b' * console_backspaces

        self.file_color_map = file_color_map
        self.origin_color_map = origin_color_map
        self.destination_color_map = destination_color_map
        self.mc_color_map = mc_color_map

        self.info_prefix = info_prefix
        self.warn_prefix = warn_prefix
        self.error_prefix = error_prefix

        self.prefixes = {
            "INFO": self.info_prefix,
            "WARN": self.warn_prefix,
            "ERROR": self.error_prefix
        }
        
        self.log_path.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        self._initializeLogger()

    def _initializeLogger(self):
        logFile = self.log_path / f"{self.name}_{datetime.now().strftime('%Y-%m-%d')}.log"

        if not self.logger.handlers:
            handler = logging.FileHandler(str(logFile))
            formatter = logging.Formatter(
                "[%(asctime)s] [%(levelname)s] %(message)s",
                datefmt="%H:%M:%S"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

        self.logger.info("Logger initialized.")

    def _apply_colors(self, msg, cmap):
        if not cmap:
            return msg
        for tag, code in cmap.items():
            msg = msg.replace(tag, code)
        return msg

    def _strip_colors(self, msg):
        if not self.file_color_map:
            return msg
        for tag in self.file_color_map.keys():
            msg = msg.replace(tag, "")
        return msg

    def _destinationLog(self, msg):
        if not self.server:
            return
        if not hasattr(self.server, "_rcon_send"):
            return
        colored = self._apply_colors(msg, self.destination_color_map)
        if self.log_destination_method == 'rcon':
            self.server._rcon_send(f'logtellraw targetless \"{self.console_backspaces}{colored}\"')
        if self.log_destination_method == 'api':
            self.server.sendConsoleCommand(f'logtellraw targetless \"{self.console_backspaces}{colored}\"')
            

    def _log(self, level, msg, destination, origin, logs):
        prefix = self.prefixes[level] + f"[{self.name}] "
        full = prefix + msg

        if destination:
            self._destinationLog(full)

        if origin:
            colored = self._apply_colors(full + "<reset>", self.origin_color_map)
            print(colored)

        if logs:
            clean = self._strip_colors(full)
            {
                "INFO": self.logger.info,
                "WARN": self.logger.warning,
                "ERROR": self.logger.error
            }[level](clean)

    def info(self, msg, destination=False, origin=True, logs=True):
        '''Log to the INFO channel'''
        self._log("INFO", msg, destination, origin, logs)

    def warn(self, msg, destination=False, origin=True, logs=True):
        '''Log to the WARN channel'''
        self._log("WARN", msg, destination, origin, logs)

    def error(self, msg, destination=False, origin=True, logs=True):
        '''Log to the ERROR channel'''
        self._log("ERROR", msg, destination, origin, logs)
