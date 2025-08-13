# Chirp-STT-Numeric-Artifact

Demonstration of a systematic 0→o substitution artifact in Google Speech-to-Text (Chirp-powered), using programmatically generated audio and reproducible scripts.

## Abstract
We reproduce the repeated-zero “wave pattern” anomaly: certain lengths of repeated "zero" collapse to letter 'o' sequences, while a specific length (e.g., three) collapses to digits (e.g., "0001"). This mirrors the known Whisper behavior and suggests a cross-platform, decoder-side emergent property rather than a tokenizer mapping bug.

## Methodology
- TTS: gTTS (English) to synthesize test phrases as MP3
- Phrases (default):
  - "zero one", "zero zero one", "zero zero zero one", "zero zero zero zero one", "zero zero zero zero zero one", "zero zero zero zero one", "zero zero zero one", "zero zero one", "zero one"
- STT: Google Cloud Speech-to-Text v2 (Chirp-powered)
- Output: table of Input → Transcribed, plus raw JSON in `results/`

## Setup
1) Python deps
```
python -m pip install -r requirements.txt
```
2) Credentials
- Create a GCP service account with Speech-to-Text v2 access
- Set env vars:
```
# PowerShell
$env:GOOGLE_APPLICATION_CREDENTIALS = "C:\path\to\service_account.json"
$env:GCP_PROJECT_ID = "your-project-id"
```

## Run
- Generate audio and transcribe in one go:
```
python scripts/run_suite.py
```
- Or step-by-step:
```
python scripts/generate_audio.py
python scripts/transcribe_chirp.py
```

## Expected Results
- A length-dependent pattern consistent with Whisper:
  - neighbors like ["zero zero one"] may yield vowel merges ("oo one")
  - a specific length like ["zero zero zero one"] may yield numeric collapse ("0001")

## Files
- `scripts/generate_audio.py` — creates MP3s for phrases in `data/test_phrases.txt`
- `scripts/transcribe_chirp.py` — transcribes MP3s via GCP STT v2; writes `results/`
- `scripts/run_suite.py` — orchestrates generation + transcription; prints a table
- `data/test_phrases.txt` — editable list of phrases
- `audio/` — generated MP3s
- `results/` — raw JSON and CSV of transcription results

## License
MIT
