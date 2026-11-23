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
