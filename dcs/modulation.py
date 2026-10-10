"""Digital modulation: BPSK, QPSK and 16-QAM (Gray mapped, unit average symbol energy).

All constellations are normalised so that Es = 1 (average symbol energy).
Eb = Es / bits_per_symbol.
"""

import numpy as np

SCHEMES = ("BPSK", "QPSK", "16-QAM")

_BPS = {"BPSK": 1, "QPSK": 2, "16-QAM": 4}

# Gray mapping for one 16-QAM axis (2 bits -> amplitude level)
_GRAY_PAM4 = {(0, 0): -3, (0, 1): -1, (1, 1): 1, (1, 0): 3}
_GRAY_PAM4_INV = {v: k for k, v in _GRAY_PAM4.items()}


def bits_per_symbol(scheme: str) -> int:
    return _BPS[scheme]


def _pad(bits: np.ndarray, k: int) -> np.ndarray:
    r = len(bits) % k
    if r:
        bits = np.concatenate([bits, np.zeros(k - r, dtype=np.uint8)])
    return bits


def modulate(bits: np.ndarray, scheme: str) -> np.ndarray:
    """Map bits to complex baseband symbols (Es = 1)."""
    bits = np.asarray(bits, dtype=np.uint8)
    k = bits_per_symbol(scheme)
    bits = _pad(bits, k)

    if scheme == "BPSK":
        return (1 - 2.0 * bits).astype(complex)  # 0 -> +1, 1 -> -1

    if scheme == "QPSK":
        b = bits.reshape(-1, 2)
        i = 1 - 2.0 * b[:, 0]
        q = 1 - 2.0 * b[:, 1]
        return (i + 1j * q) / np.sqrt(2)

    if scheme == "16-QAM":
        b = bits.reshape(-1, 4)
        i = np.array([_GRAY_PAM4[(x, y)] for x, y in b[:, :2]], dtype=float)
        q = np.array([_GRAY_PAM4[(x, y)] for x, y in b[:, 2:]], dtype=float)
        return (i + 1j * q) / np.sqrt(10)

    raise ValueError(f"Unknown scheme: {scheme}")


def _nearest_pam4(x: np.ndarray) -> np.ndarray:
    """Hard decision on a PAM-4 axis, returns levels in {-3,-1,1,3}."""
    levels = np.array([-3, -1, 1, 3])
    return levels[np.argmin(np.abs(x[:, None] - levels[None, :]), axis=1)]


def demodulate(symbols: np.ndarray, scheme: str) -> np.ndarray:
    """Hard-decision (minimum distance) demodulation back to bits."""
    symbols = np.asarray(symbols, dtype=complex)

    if scheme == "BPSK":
        return (symbols.real < 0).astype(np.uint8)

    if scheme == "QPSK":
        out = np.empty(2 * len(symbols), dtype=np.uint8)
        out[0::2] = symbols.real < 0
        out[1::2] = symbols.imag < 0
        return out

    if scheme == "16-QAM":
        i = _nearest_pam4(symbols.real * np.sqrt(10))
        q = _nearest_pam4(symbols.imag * np.sqrt(10))
        out = np.empty(4 * len(symbols), dtype=np.uint8)
        ib = np.array([_GRAY_PAM4_INV[int(v)] for v in i], dtype=np.uint8)
        qb = np.array([_GRAY_PAM4_INV[int(v)] for v in q], dtype=np.uint8)
        out[0::4], out[1::4] = ib[:, 0], ib[:, 1]
        out[2::4], out[3::4] = qb[:, 0], qb[:, 1]
        return out

    raise ValueError(f"Unknown scheme: {scheme}")


def ideal_constellation(scheme: str) -> np.ndarray:
    """All ideal constellation points (for plotting)."""
    k = bits_per_symbol(scheme)
    all_bits = ((np.arange(2 ** k)[:, None] >> np.arange(k - 1, -1, -1)) & 1).astype(np.uint8)
    return modulate(all_bits.reshape(-1), scheme)
