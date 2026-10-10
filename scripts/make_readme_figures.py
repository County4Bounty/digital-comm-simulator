"""Generate the README figures from the real simulator code.

Run from the project root:  python scripts/make_readme_figures.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from dcs.ber import simulate_ber, theoretical_ber
from dcs.channel import CHANNELS
from dcs.modulation import SCHEMES, bits_per_symbol, ideal_constellation, modulate

OUT = Path(__file__).resolve().parent.parent / "docs" / "images"
OUT.mkdir(parents=True, exist_ok=True)


def constellations():
    fig, axes = plt.subplots(2, 3, figsize=(12, 7.5))
    for row, ebn0 in enumerate((15, 6)):
        for col, scheme in enumerate(SCHEMES):
            ax = axes[row, col]
            bits = np.random.default_rng(1).integers(0, 2, 3000 * bits_per_symbol(scheme), dtype=np.uint8)
            rx = CHANNELS["AWGN"](modulate(bits, scheme), ebn0, scheme, np.random.default_rng(2))
            ideal = ideal_constellation(scheme)
            ax.scatter(rx.real, rx.imag, s=3, alpha=0.35)
            ax.scatter(ideal.real, ideal.imag, c="red", marker="x", s=70)
            ax.set_xlim(-1.8, 1.8)
            ax.set_ylim(-1.8, 1.8)
            ax.set_aspect("equal")
            ax.axhline(0, color="gray", lw=0.5)
            ax.axvline(0, color="gray", lw=0.5)
            ax.set_title(f"{scheme} @ Eb/N0 = {ebn0} dB")
            ax.grid(alpha=0.3)
    fig.suptitle("Constellation diagrams over AWGN (top: high SNR, bottom: low SNR)")
    fig.tight_layout()
    fig.savefig(OUT / "constellations.png", dpi=120)
    plt.close(fig)


def ber_curves():
    colors = {"BPSK": "tab:blue", "QPSK": "tab:green", "16-QAM": "tab:red"}
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    for ax, channel, pts in (
        (axes[0], "AWGN", np.arange(0, 15, 1.0)),
        (axes[1], "Rayleigh + AWGN", np.arange(0, 26, 2.0)),
    ):
        for s in SCHEMES:
            sim = simulate_ber(s, pts, channel, n_bits=1_000_000, seed=0)
            mask = sim > 0
            ax.semilogy(pts[mask], sim[mask], "o", color=colors[s], label=f"{s} simulated")
            ax.semilogy(pts, theoretical_ber(pts, s, channel), "-", color=colors[s], label=f"{s} theoretical")
        ax.set_ylim(1e-6, 1)
        ax.set_xlabel("Eb/N0 (dB)")
        ax.set_ylabel("Bit Error Rate")
        ax.set_title(f"BER over {channel}")
        ax.grid(True, which="both", alpha=0.3)
        ax.legend(ncol=2, fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "ber_curves.png", dpi=120)
    plt.close(fig)


if __name__ == "__main__":
    constellations()
    ber_curves()
    print("Saved figures to", OUT)
