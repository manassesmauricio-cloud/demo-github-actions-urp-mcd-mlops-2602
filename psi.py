"""PSI (Population Stability Index) entre una muestra de referencia y una actual."""
import numpy as np


def psi(referencia, actual, cortes=10):
    bordes = np.percentile(referencia, np.linspace(0, 100, cortes + 1))
    bordes[0], bordes[-1] = -np.inf, np.inf
    ref = np.histogram(referencia, bordes)[0] / len(referencia)
    act = np.histogram(actual, bordes)[0] / len(actual)
    ref, act = np.clip(ref, 1e-6, None), np.clip(act, 1e-6, None)
    return float(np.sum((act - ref) * np.log(act / ref)))


def semaforo(valor):
    if valor < 0.10:
        return "OK"
    if valor < 0.25:
        return "WARN"
    return "ALARM"
