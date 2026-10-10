"""Digital Communication System Simulator core package."""

from .text_bits import text_to_bits, bits_to_text
from .modulation import modulate, demodulate, bits_per_symbol, SCHEMES
from .channel import awgn, rayleigh_awgn
from .ber import theoretical_ber, simulate_ber, count_errors

__all__ = [
    "text_to_bits",
    "bits_to_text",
    "modulate",
    "demodulate",
    "bits_per_symbol",
    "SCHEMES",
    "awgn",
    "rayleigh_awgn",
    "theoretical_ber",
    "simulate_ber",
    "count_errors",
]
