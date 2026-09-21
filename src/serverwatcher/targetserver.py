from hungerlib import Panel, MinecraftServer, BridgeClient
from hungerlib import utils
from hungerlib.utils import methods as m

from .configmanager import config_manager
from .exceptions import UnsupportedOperationError

class TargetServer:
    def __init__(self, bridge_start_handler=None, bridge_restart_handler=None, bridge_kill_handler=None):
        self.config_manager = config_manager
        self.env = self.config_manager.env
        self.config = self.config_manager.config

        self.ptero_enabled = self.env.ptero_enabled

        self.bridge = BridgeClient(
            url = self.env.bridge_url,
            token_id = self.env.bridge_token_id,
            token_secret = self.env.bridge_token_secret,
            static_delay = 0.5
        )

        self.panel = Panel('Panel', self.env.ptero_url, self.env.ptero_api_key)
        self.mc_server = MinecraftServer(
            'Minecraft Server',
            self.panel,
            self.env.ptero_server_id,
            self.config.server_domain,
            self.config.server_port,
            self.bridge
        )

        self.bridge_start_handler = bridge_start_handler
        self.bridge_restart_handler = bridge_restart_handler
        self.bridge_kill_handler = bridge_kill_handler

        m.proxy(self, self.bridge.getTokenInfo)

        m.proxy(self, self.bridge.getPlatform)
        m.proxy(self, self.bridge.getMinecraftVersion)
        m.proxy(self, self.bridge.getBridgeVersion)
        m.proxy(self, self.bridge.getBridgePort)

        m.proxy(self, self.bridge.getPlayers)
        m.proxy(self, self.bridge.getMaxPlayers)

        m.proxy(self, self.bridge.getTPS)
        m.proxy(self, self.bridge.getMSPT)

        m.proxy(self, self.bridge.getLoadedChunks)
        m.proxy(self, self.bridge.getLoadedEntities)

        m.proxy(self, self.bridge.getGCStats)
        m.proxy(self, self.bridge.getThreadStats)
        m.proxy(self, self.bridge.getNetworkStats)

        m.proxy(self, self.bridge.log)
        m.proxy(self, self.bridge.runCommand)

        self.stream = self.bridge.stream

    def checkPtero(self):
        '''Check if the panel is reachable and the API key is valid.'''
        return utils.validateAll(self.panel, self.mc_server)

    def checkBridge(self):
        '''Check if the bridge is reachable and the token is valid.'''
        return self.bridge.isOk()

    def isOnline(self):
        '''Returns True if online, False if offline'''
        return self.mc_server.isOnline()

    def isOffline(self):
        '''Returns True if offline, False if online'''
        return self.mc_server.isOffline()

    def refreshResources(self):
        '''Refreshes the server's resources (ptero only)'''
        if self.ptero_enabled:
            self.mc_server.refresh()
        else:
            raise UnsupportedOperationError('Bridge-only mode: refreshing is not necessary and not supported')

    def getRAM(self):
        '''Returns current RAM usage'''
        if self.ptero_enabled:
            return self.mc_server.getRAM(rounding=0, gb=False)
        else:
            return self.bridge.getMemoryStats()['process_used']

    def getDisk(self):
        '''Returns current disk usage'''
        if self.ptero_enabled:
            return self.mc_server.getDisk(rounding=0, gb=False)
        else:
            raise UnsupportedOperationError('Bridge-only mode: getting disk usage is not supported')

    def getCPULoad(self):
        '''Returns current CPU usage'''
        if self.ptero_enabled:
            return self.mc_server.getCPU(rounding=0)
        else:
            return self.bridge.getCPUStats()['load']

    def getProcessorCount(self):
        '''Returns the number of processors'''
        return self.bridge.getCPUStats()['processors']

    def getUptime(self):
        '''Returns the uptime'''
        if self.ptero_enabled:
            return self.mc_server.getUptime()
        else:
            return self.bridge.getUptime()

    def startServer(self):
        '''Starts the server (ptero-only)'''
        if self.ptero_enabled:
            return self.mc_server.start()
        elif self.bridge_start_handler is not None:
            self.bridge_start_handler()
        else:
            raise UnsupportedOperationError('Bridge-only mode: starting the server is not supported unless a bridge start handler is provided.')
    
    def restartServer(self):
        '''Restarts the server (ptero-only)'''
        if self.ptero_enabled:
            return self.mc_server.restart()
        elif self.bridge_restart_handler is not None:
            self.bridge_restart_handler()
        else:
            raise UnsupportedOperationError('Bridge-only mode: restarting the server is not supported unless a bridge restart handler is provided.')

    def stopServer(self):
        '''Stops the server (ptero and bridge)'''
        if self.ptero_enabled:
            return self.mc_server.stop()
        else:
            self.bridge.stopServer()

    def killServer(self):
        '''Kills the server (ptero-only)'''
        if self.ptero_enabled:
            return self.mc_server.kill()
        elif self.bridge_kill_handler is not None:
            self.bridge_kill_handler()
        else:
            raise UnsupportedOperationError('Bridge-only mode: killing the server is not supported unless a bridge kill handler is provided.')
