"""Channel models: AWGN and flat Rayleigh fading + AWGN."""

import numpy as np

from .modulation import bits_per_symbol


def noise_sigma(ebn0_db: float, scheme: str) -> float:
    """Per-dimension noise std-dev for Es = 1.

    Es/N0 = k * Eb/N0, N0 = Es / (Es/N0), complex noise has variance N0
    (N0/2 per real dimension).
    """
    k = bits_per_symbol(scheme)
    esn0 = k * 10 ** (ebn0_db / 10)
    n0 = 1.0 / esn0
    return np.sqrt(n0 / 2)


def awgn(symbols: np.ndarray, ebn0_db: float, scheme: str, rng=None) -> np.ndarray:
    rng = np.random.default_rng(rng)
    s = noise_sigma(ebn0_db, scheme)
    noise = s * (rng.standard_normal(symbols.shape) + 1j * rng.standard_normal(symbols.shape))
    return symbols + noise


def rayleigh_awgn(symbols: np.ndarray, ebn0_db: float, scheme: str, rng=None) -> np.ndarray:
    """Flat Rayleigh fading (E|h|^2 = 1) with perfect channel knowledge at the
    receiver (coherent equalisation: y / h)."""
    rng = np.random.default_rng(rng)
    h = (rng.standard_normal(symbols.shape) + 1j * rng.standard_normal(symbols.shape)) / np.sqrt(2)
    s = noise_sigma(ebn0_db, scheme)
    noise = s * (rng.standard_normal(symbols.shape) + 1j * rng.standard_normal(symbols.shape))
    y = h * symbols + noise
    return y / h


CHANNELS = {"AWGN": awgn, "Rayleigh + AWGN": rayleigh_awgn}
