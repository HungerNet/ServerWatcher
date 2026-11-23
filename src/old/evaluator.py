class Evaluator:
    def __init__(self, config):
        self.cfg = config

    def evaluate(self, m: dict):
        score = 0
        flags = []
        reasons = []

        def check(metric_name, value, threshold, weight, compare='>'):
            nonlocal score, flags, reasons
            if value is None:
                return
            if compare == '>' and value > threshold:
                score += weight
                flags.append(metric_name)
                reasons.append(f"{metric_name}: {value} > {threshold}")
            elif compare == '<' and value < threshold:
                score += weight
                flags.append(metric_name)
                reasons.append(f"{metric_name}: {value} < {threshold}")

        # RAM / CPU
        check('ram', m['ram'], self.cfg.threshold_ram, self.cfg.weight_ram, '>')
        check('cpu', m['cpu'], self.cfg.threshold_cpu, self.cfg.weight_cpu, '>')

        # Uptime (low uptime is bad)
        check('uptime', m['uptime'], self.cfg.threshold_uptime, self.cfg.weight_uptime, '<')

        # Players
        check('players', m['players'], self.cfg.threshold_players, self.cfg.weight_players, '>')

        # TPS
        check('tps', m['tps'], self.cfg.threshold_tps, self.cfg.weight_tps, '<')
        check('tps_1m', m['tps_1m'], self.cfg.threshold_tps_1m, self.cfg.weight_tps_1m, '<')
        check('tps_5m', m['tps_5m'], self.cfg.threshold_tps_5m, self.cfg.weight_tps_5m, '<')
        check('tps_15m', m['tps_15m'], self.cfg.threshold_tps_15m, self.cfg.weight_tps_15m, '<')

        # MSPT
        check('mspt', m['mspt'], self.cfg.threshold_mspt, self.cfg.weight_mspt, '>')

        # Loaded chunks/entities
        check('loaded_chunks', m['loaded_chunks']['total'], self.cfg.threshold_loaded_chunks, self.cfg.weight_loaded_chunks, '>')
        check('loaded_entities', m['loaded_entities']['total'], self.cfg.threshold_loaded_entities, self.cfg.weight_loaded_entities, '>')

        # GC stats
        gc = m['gc_stats']
        if gc:
            check('gc_pause_ms', gc['last_gc_pause_ms'], self.cfg.threshold_gc_pause_ms, self.cfg.weight_gc_pause_ms, '>')

        # Thread stats
        threads = m['thread_stats']
        if threads:
            check('thread_peak', threads['peak'], self.cfg.threshold_thread_peak, self.cfg.weight_thread_peak, '>')

        return {
            'score': score,
            'flags': flags,
            'reasons': reasons
        }
