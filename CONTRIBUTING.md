# Contributing

Thanks for your interest in improving the Digital Communication System Simulator!

## Getting set up

```bash
git clone https://github.com/YOUR_USERNAME/digital-comm-simulator.git
cd digital-comm-simulator
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pytest -q
streamlit run app.py
```

## Guidelines

- Keep simulation logic in `dcs/` (no Streamlit imports there) so it stays testable.
- Add or update tests in `tests/` for any new modulation scheme, channel or BER formula. New BER formulas should be checked against Monte-Carlo simulation.
- Make sure `pytest -q` passes before opening a pull request.
- Keep pull requests focused; describe what changed and why.

## Ideas that would be welcome

- Convolutional coding + Viterbi decoding (hard and soft decision)
- OFDM with cyclic prefix
- Rician / multipath channels
- Adaptive modulation
- More modulation schemes (8-PSK, 64-QAM)

## Reporting bugs

Open an issue with the steps to reproduce, the modulation / channel / Eb/N0 settings used, and the full error message if there is one.
