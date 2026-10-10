import numpy as np
import pytest

from dcs import (SCHEMES, bits_to_text, demodulate, modulate, simulate_ber,
                 text_to_bits, theoretical_ber, awgn)
from dcs.modulation import ideal_constellation


def test_text_roundtrip():
    msg = "HELLO ECE 123!"
    assert bits_to_text(text_to_bits(msg)) == msg


@pytest.mark.parametrize("scheme", SCHEMES)
def test_noiseless_roundtrip(scheme):
    bits = np.random.default_rng(0).integers(0, 2, 4000, dtype=np.uint8)
    rx = demodulate(modulate(bits, scheme), scheme)
    assert np.array_equal(bits, rx[: len(bits)])


@pytest.mark.parametrize("scheme", SCHEMES)
def test_unit_average_energy(scheme):
    pts = ideal_constellation(scheme)
    assert np.isclose(np.mean(np.abs(pts) ** 2), 1.0)


@pytest.mark.parametrize("scheme", SCHEMES)
def test_high_snr_no_errors(scheme):
    msg = text_to_bits("The quick brown fox")
    rx = demodulate(awgn(modulate(msg, scheme), 25, scheme, 1), scheme)[: len(msg)]
    assert np.array_equal(msg, rx)


@pytest.mark.parametrize("scheme", SCHEMES)
def test_simulated_matches_theory_awgn(scheme):
    snr = 6
    sim = simulate_ber(scheme, [snr], "AWGN", n_bits=400_000, seed=3)[0]
    th = float(theoretical_ber(snr, scheme, "AWGN"))
    assert sim == pytest.approx(th, rel=0.15)


def test_rayleigh_matches_theory_bpsk():
    sim = simulate_ber("BPSK", [10], "Rayleigh + AWGN", n_bits=400_000, seed=4)[0]
    th = float(theoretical_ber(10, "BPSK", "Rayleigh + AWGN"))
    assert sim == pytest.approx(th, rel=0.15)
