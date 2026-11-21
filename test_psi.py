import numpy as np

from psi import psi, semaforo

rng = np.random.default_rng(0)


def test_misma_distribucion_da_ok():
    ref, act = rng.normal(0, 1, 10_000), rng.normal(0, 1, 10_000)
    assert semaforo(psi(ref, act)) == "OK"


def test_corrimiento_fuerte_da_alarm():
    ref, act = rng.normal(0, 1, 10_000), rng.normal(1.5, 1, 10_000)
    assert semaforo(psi(ref, act)) == "ALARM"
