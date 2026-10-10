"""Digital Communication System Simulator - Streamlit app.

Run with:  streamlit run app.py
"""

import io

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

from dcs.ber import count_errors, simulate_ber, theoretical_ber
from dcs.channel import CHANNELS
from dcs.modulation import SCHEMES, bits_per_symbol, demodulate, ideal_constellation, modulate
from dcs.text_bits import bits_to_text, format_bits, text_to_bits

st.set_page_config(page_title="Digital Communication Simulator", page_icon="📡", layout="wide")
st.title("📡 Digital Communication System Simulator")
st.caption("Text → bits → modulation → noisy channel → demodulation → recovered text, with BER analysis.")

# ---------------------------------------------------------------- sidebar
with st.sidebar:
    st.header("Controls")
    message = st.text_input("Message", "HELLO ECE")
    scheme = st.selectbox("Modulation", SCHEMES, index=1)
    channel = st.selectbox("Channel", list(CHANNELS.keys()))
    ebn0 = st.slider("Eb/N0 (dB)", -2.0, 20.0, 7.0, 0.5)
    seed = st.number_input("Random seed", 0, 10_000, 42)
    st.divider()
    st.subheader("BER curve settings")
    sweep_min, sweep_max = st.slider("Eb/N0 sweep range (dB)", -2, 20, (0, 14))
    n_bits = st.select_slider("Bits per point", [10_000, 50_000, 200_000, 1_000_000], value=200_000)
    compare_all = st.checkbox("Compare all modulation schemes", value=True)

if not message:
    st.warning("Enter a message to transmit.")
    st.stop()

# ----------------------------------------------------------- simulate link
rng = np.random.default_rng(int(seed))
tx_bits = text_to_bits(message)
tx_syms = modulate(tx_bits, scheme)
rx_syms = CHANNELS[channel](tx_syms, ebn0, scheme, rng)
rx_bits = demodulate(rx_syms, scheme)[: len(tx_bits)]
errors = count_errors(tx_bits, rx_bits)
ber = errors / len(tx_bits)
recovered = bits_to_text(rx_bits)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Bits sent", len(tx_bits))
c2.metric("Bit errors", errors)
c3.metric("BER (this message)", f"{ber:.4f}")
c4.metric("Theoretical BER", f"{float(theoretical_ber(ebn0, scheme, channel)):.2e}")

st.subheader("Message")
m1, m2 = st.columns(2)
m1.markdown("**Transmitted**")
m1.code(message, language=None)
m2.markdown("**Recovered**")
m2.code(recovered, language=None)

with st.expander("Show transmitted / received bits"):
    st.markdown("**Transmitted bits**")
    st.code(format_bits(tx_bits), language=None)
    st.markdown("**Received bits**")
    st.code(format_bits(rx_bits), language=None)

# ------------------------------------------------------------------ plots
left, right = st.columns(2)

with left:
    st.subheader("Constellation diagram")
    # use more symbols than the message alone so the cloud is visible
    demo_bits = np.random.default_rng(1).integers(0, 2, 4000 * bits_per_symbol(scheme), dtype=np.uint8)
    demo_rx = CHANNELS[channel](modulate(demo_bits, scheme), ebn0, scheme, np.random.default_rng(2))
    ideal = ideal_constellation(scheme)
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.scatter(demo_rx.real, demo_rx.imag, s=4, alpha=0.35, label="Received")
    ax.scatter(ideal.real, ideal.imag, c="red", marker="x", s=80, label="Ideal")
    lim = 1.8 if channel == "AWGN" else 2.5
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.axhline(0, color="gray", lw=0.5)
    ax.axvline(0, color="gray", lw=0.5)
    ax.set_xlabel("In-phase")
    ax.set_ylabel("Quadrature")
    ax.set_title(f"{scheme} @ Eb/N0 = {ebn0} dB ({channel})")
    ax.legend(loc="upper right")
    ax.grid(alpha=0.3)
    st.pyplot(fig)
    plt.close(fig)

with right:
    st.subheader("Signal waveform (in-phase component)")
    n_show = min(len(tx_syms), 24)
    sps = 20  # samples per symbol for display
    t = np.arange(n_show * sps) / sps
    tx_wave = np.repeat(tx_syms.real[:n_show], sps)
    rx_wave = np.repeat(rx_syms.real[:n_show], sps)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(t, tx_wave, label="Transmitted", lw=2)
    ax.plot(t, rx_wave, label="Received", lw=1, alpha=0.8)
    ax.set_xlabel("Symbol index")
    ax.set_ylabel("Amplitude")
    ax.legend()
    ax.grid(alpha=0.3)
    st.pyplot(fig)
    plt.close(fig)

# --------------------------------------------------------------- BER curve
st.subheader("BER vs Eb/N0")


@st.cache_data(show_spinner="Running Monte-Carlo simulation...")
def run_sweep(schemes, channel, lo, hi, n_bits):
    pts = np.arange(lo, hi + 1, 1.0)
    rows = {"Eb/N0 (dB)": pts}
    for s in schemes:
        rows[f"{s} simulated"] = simulate_ber(s, pts, channel, n_bits)
        rows[f"{s} theoretical"] = theoretical_ber(pts, s, channel)
    return pd.DataFrame(rows)


schemes_to_run = tuple(SCHEMES) if compare_all else (scheme,)
df = run_sweep(schemes_to_run, channel, sweep_min, sweep_max, n_bits)

fig, ax = plt.subplots(figsize=(9, 5))
colors = {"BPSK": "tab:blue", "QPSK": "tab:green", "16-QAM": "tab:red"}
for s in schemes_to_run:
    sim = df[f"{s} simulated"].to_numpy()
    mask = sim > 0
    ax.semilogy(df["Eb/N0 (dB)"][mask], sim[mask], "o", color=colors[s], label=f"{s} simulated")
    ax.semilogy(df["Eb/N0 (dB)"], df[f"{s} theoretical"], "-", color=colors[s], label=f"{s} theoretical")
ax.axvline(ebn0, color="black", ls="--", lw=0.8, label="Current Eb/N0")
ax.set_ylim(1e-6, 1)
ax.set_xlabel("Eb/N0 (dB)")
ax.set_ylabel("Bit Error Rate")
ax.set_title(f"BER performance over {channel}")
ax.grid(True, which="both", alpha=0.3)
ax.legend(ncol=2, fontsize=8)
st.pyplot(fig)
plt.close(fig)

st.caption("Points with zero observed errors are omitted from the log plot (increase bits per point to resolve lower BER).")

with st.expander("Results table"):
    st.dataframe(df, width="stretch")
buf = io.StringIO()
df.to_csv(buf, index=False)
st.download_button("⬇ Download results as CSV", buf.getvalue(), "ber_results.csv", "text/csv")