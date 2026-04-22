# Names are in "from-to" format. Example: mb_gb() means megabyte to gigabyte.

def mb_gb(mb, floor=False):
    return mb / 1000 if not floor else mb // 1000

def gb_mb(gb):
    return gb * 1000

def mib_gib(mib, floor=False):
    return mib / 1024 if not floor else mib // 1024

def gib_mib(gib):
    return gib * 1024