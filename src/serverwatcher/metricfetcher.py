import time
from statistics import mean
from .targetserver import TargetServer


class MetricFetcher:
    def __init__(self, server: TargetServer):
        self.server = server

    def snapshot(
        self,
        duration: float = 0.0,
        interval: float = 0.5,
        drop_outliers: int = 0,
    ):
        '''
        Takes a snapshot of server metrics.

        Only RAM + CPU are smoothed.
        All other metrics are instant snapshots.

        duration: total seconds to sample (0 = no smoothing)
        interval: delay between samples
        drop_outliers: number of highest and lowest samples to drop (for RAM/CPU only)
        '''

        # smoothing mode (ram + cpu)
        if duration > 0:
            ram_samples = []
            cpu_samples = []

            end = time.time() + duration
            while time.time() < end:
                ram_samples.append(self.server.getRAM())
                cpu_samples.append(self.server.getCPULoad())
                time.sleep(interval)

            def smooth(values):
                if not values:
                    return None
                values = sorted(values)
                if drop_outliers > 0:
                    values = values[drop_outliers:len(values) - drop_outliers]
                return mean(values) if values else None

            ram = smooth(ram_samples)
            cpu = smooth(cpu_samples)

        # instant mode
        else:
            ram = self.server.getRAM()
            cpu = self.server.getCPULoad()

        # instant metrics (never smoothed)
        uptime = self.server.getUptime()

        players = self.server.getPlayers('count')
        max_players = self.server.getMaxPlayers()

        tps = self.server.getTPS()
        tps_1m = self.server.getTPS('1m')
        tps_5m = self.server.getTPS('5m')
        tps_15m = self.server.getTPS('15m')
        mspt = self.server.getMSPT()

        loaded_chunks = self.server.getLoadedChunks()
        loaded_entities = self.server.getLoadedEntities()

        gc_stats = self.server.getGCStats()
        thread_stats = self.server.getThreadStats()

        # final metric dict
        return {
            'ram': ram,
            'cpu': cpu,
            'uptime': uptime,

            'players': players,
            'max_players': max_players,

            'tps': tps,
            'tps_1m': tps_1m,
            'tps_5m': tps_5m,
            'tps_15m': tps_15m,
            'mspt': mspt,

            'loaded_chunks': loaded_chunks,
            'loaded_entities': loaded_entities,

            'gc_stats': gc_stats,
            'thread_stats': thread_stats
        }
