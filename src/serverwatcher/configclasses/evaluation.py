from mapres import datamap

@datamap.braces.config(recursive=True)
class EvaluatorConfig:
    __user_config_path__ = 'config/evaluation.yaml'
    __default_config_path__ = 'defaultconfigs/evaluation.yaml'

    # Sampling
    sample_duration: float | int = 'sampling.duration'
    sample_interval: float | int = 'sampling.interval'
    sample_outlier_drop: int = 'sampling.drop_outliers'

    # Thresholds
    threshold_ram: float = 'thresholds.ram'
    threshold_cpu: float = 'thresholds.cpu'
    threshold_uptime: float = 'thresholds.uptime'
    threshold_min_uptime: float = 'thresholds.min_uptime'

    threshold_players: int = 'thresholds.players'
    threshold_max_players: int = 'thresholds.max_players'

    threshold_tps: float = 'thresholds.tps'
    threshold_tps_1m: float = 'thresholds.tps_1m'
    threshold_tps_5m: float = 'thresholds.tps_5m'
    threshold_tps_15m: float = 'thresholds.tps_15m'

    threshold_mspt: float = 'thresholds.mspt'

    threshold_loaded_chunks: int = 'thresholds.loaded_chunks'
    threshold_loaded_entities: int = 'thresholds.loaded_entities'

    threshold_gc_pause_ms: float = 'thresholds.gc_pause_ms'
    threshold_thread_peak: int = 'thresholds.thread_peak'

    # Weights
    weight_ram: int = 'weights.ram'
    weight_cpu: int = 'weights.cpu'
    weight_uptime: int = 'weights.uptime'

    weight_players: int = 'weights.players'
    weight_max_players: int = 'weights.max_players'

    weight_tps: int = 'weights.tps'
    weight_tps_1m: int = 'weights.tps_1m'
    weight_tps_5m: int = 'weights.tps_5m'
    weight_tps_15m: int = 'weights.tps_15m'

    weight_mspt: int = 'weights.mspt'

    weight_loaded_chunks: int = 'weights.loaded_chunks'
    weight_loaded_entities: int = 'weights.loaded_entities'

    weight_gc_pause_ms: int = 'weights.gc_pause_ms'
    weight_thread_peak: int = 'weights.thread_peak'


class fallbacks:
    sample_duration = 5
    sample_interval = 1
    sample_outlier_drop = 1

    threshold_ram = 6
    threshold_cpu = 150
    threshold_uptime = 12
    threshold_min_uptime = 30

    threshold_players = 0
    threshold_max_players = 0

    threshold_tps = 19.5
    threshold_tps_1m = 19.5
    threshold_tps_5m = 19.5
    threshold_tps_15m = 19.5

    threshold_mspt = 50

    threshold_loaded_chunks = 0
    threshold_loaded_entities = 0

    threshold_gc_pause_ms = 200
    threshold_thread_peak = 500

    weight_ram = 2
    weight_cpu = 2
    weight_uptime = 1

    weight_players = 1
    weight_max_players = 0

    weight_tps = 3
    weight_tps_1m = 1
    weight_tps_5m = 1
    weight_tps_15m = 1

    weight_mspt = 3

    weight_loaded_chunks = 0
    weight_loaded_entities = 0

    weight_gc_pause_ms = 2
    weight_thread_peak = 2


class rules:
    threshold_ram = 'required'
    threshold_cpu = 'required'
    threshold_tps = 'required'
    threshold_mspt = 'required'
    threshold_uptime = 'required'
    threshold_min_uptime = 'required'
