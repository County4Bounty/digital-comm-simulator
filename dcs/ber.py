"""BER utilities: error counting, theoretical BER and Monte-Carlo simulation."""

import numpy as np
from scipy.special import erfc

from .modulation import modulate, demodulate, bits_per_symbol
from .channel import CHANNELS


def count_errors(tx: np.ndarray, rx: np.ndarray) -> int:
    n = min(len(tx), len(rx))
    return int(np.sum(tx[:n] != rx[:n]))


def _q(x):
    return 0.5 * erfc(x / np.sqrt(2))


def theoretical_ber(ebn0_db, scheme: str, channel: str = "AWGN"):
    """Closed-form BER (Gray coding). 16-QAM uses the standard approximation."""
    ebn0 = 10 ** (np.asarray(ebn0_db, dtype=float) / 10)

    if channel == "AWGN":
        if scheme in ("BPSK", "QPSK"):
            return _q(np.sqrt(2 * ebn0))
        if scheme == "16-QAM":
            return (3 / 8) * erfc(np.sqrt(0.4 * ebn0))
    elif channel == "Rayleigh + AWGN":
        if scheme in ("BPSK", "QPSK"):
            return 0.5 * (1 - np.sqrt(ebn0 / (1 + ebn0)))
        if scheme == "16-QAM":
            # Approximation for Gray-coded 16-QAM in Rayleigh fading
            g = 0.4 * ebn0
            return (3 / 8) * (1 - np.sqrt(g / (1 + g)))
    raise ValueError(f"Unsupported combination: {scheme} / {channel}")


def simulate_ber(scheme: str, ebn0_db_list, channel: str = "AWGN",
                 n_bits: int = 200_000, seed: int = 0):
    """Monte-Carlo BER for each Eb/N0 point. Returns np.ndarray of BER."""
    rng = np.random.default_rng(seed)
    k = bits_per_symbol(scheme)
    n_bits = (n_bits // k) * k
    chan = CHANNELS[channel]
    out = []
    for ebn0 in ebn0_db_list:
        bits = rng.integers(0, 2, n_bits, dtype=np.uint8)
        rx = demodulate(chan(modulate(bits, scheme), ebn0, scheme, rng), scheme)
        out.append(count_errors(bits, rx) / n_bits)
    return np.array(out)
