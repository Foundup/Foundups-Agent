# Whisper Tokenizer Artifact Diagnostics (WSP_agentic/tests/whisper_investigation)

## Purpose
Research diagnostics to probe the reported 0->o substitution artifact in Whisper outputs. These scripts decouple acoustic preprocessing from token decoding to identify whether the substitution arises in the tokenizer or upstream model decoding.

## Scripts
- demo_whisper_preprocessing.py
  - Demonstrates Whisper-compatible Log-Mel front-end (16 kHz, n_fft=400, hop=160, n_mels=80) with visualization.
- diagnose_zero_substitution_tokenizer.py
  - Calls Whisper tokenizer directly to test textual sequences: "01", "0001", "00001", and controls like "o1". Performs encode -> decode -> encode round-trips and prints token IDs and stability.

## Hypothesis
- The tokenizer performs byte-level BPE and does not convert the digit '0' (U+0030) into the letter 'o' (U+006F).
- The observed 0->o artifact is likely produced by the decoder’s language modeling bias under repetition, not by tokenizer mapping. Certain repeat lengths (e.g., "0001") align with learned numeric patterns, while others ("01", "00001") tip the decoder toward letter bigrams/merges (e.g., "oo...").

## How to Run
Prereqs installed:
```
python -m pip install -r WSP_agentic/requirements.txt
```
Run demos:
```
python WSP_agentic/tests/whisper_investigation/demo_whisper_preprocessing.py
python WSP_agentic/tests/whisper_investigation/diagnose_zero_substitution_tokenizer.py
```

## Expected Output (Tokenizer Diagnostic)
- JSON lines reporting input text, token ids, decoded text, and round-trip stability.
- Repetition sweep results for "0"×N + "1" for N=1..8, useful for spotting thresholds where decoding diverges.

## WSP Compliance
- WSP 22: Documented purpose and run steps
- WSP 34: This README serves as test documentation for research diagnostics
- WSP 50: Pre-action verification by isolating tokenizer from acoustic front-end

