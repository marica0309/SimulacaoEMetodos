# Gerador Pseudoaleatório (LCG) --> M2
a = 1664525
c = 1013904223
M = 2**32
seed = 1391
_last_random = seed


def NextRandom():
    """Retorna um número pseudoaleatório uniforme em (0,1)."""
    global _last_random
    _last_random = (a * _last_random + c) % M
    return _last_random / M  # normalizado entre 0 e 1
