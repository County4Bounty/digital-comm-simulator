"""Text <-> bit-array conversion (UTF-8, MSB first)."""

import numpy as np


def text_to_bits(text: str) -> np.ndarray:
    """Convert a string to a 1-D array of bits (uint8), 8 bits per byte, MSB first."""
    data = np.frombuffer(text.encode("utf-8"), dtype=np.uint8)
    return np.unpackbits(data)


def bits_to_text(bits: np.ndarray) -> str:
    """Convert bits back to text. Incomplete trailing bytes are dropped and
    undecodable bytes (caused by channel errors) become the replacement char."""
    bits = np.asarray(bits, dtype=np.uint8)
    n = (len(bits) // 8) * 8
    if n == 0:
        return ""
    data = np.packbits(bits[:n]).tobytes()
    return data.decode("utf-8", errors="replace")


def format_bits(bits: np.ndarray, group: int = 8, limit: int = 256) -> str:
    """Pretty-print bits in groups of `group` (e.g. 01001000 01100101 ...)."""
    s = "".join(str(int(b)) for b in bits[:limit])
    out = " ".join(s[i:i + group] for i in range(0, len(s), group))
    return out + (" ..." if len(bits) > limit else "")
