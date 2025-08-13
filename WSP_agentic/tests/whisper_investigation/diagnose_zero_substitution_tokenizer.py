"""
Diagnostic: Investigate 0→o substitution by probing Whisper tokenizer behavior directly.

Notes:
- Tokenizer maps between token IDs and text; it does not process acoustics.
- We isolate decode/encode paths to see if textual repetitions around '0' vs 'o'
  can produce unexpected merges due to byte-level BPE.
- We also simulate sequences reminiscent of model outputs to check post-processing
  (e.g., special token trimming) for corner cases.

Primary tests:
- Sequences: "01", "0001", "00001", plus controls like "o1", "oooo1".
- Round-trip: encode → decode → encode to detect unstable mappings.

Requires: openai-whisper
"""

import json
from typing import List, Tuple

try:
	import whisper
except ImportError as exc:
	raise SystemExit("Install openai-whisper to run this diagnostic: pip install openai-whisper") from exc


def get_tokenizer() -> "whisper.tokenizer.Tokenizer":
	# Use English multilingual tokenizer directly to avoid model download
	return whisper.tokenizer.get_tokenizer(multilingual=True, language="en", task="transcribe")


def round_trip(tokenizer, text: str) -> Tuple[List[int], str, List[int]]:
	ids = tokenizer.encode(text)
	decoded = tokenizer.decode(ids)
	ids_rt = tokenizer.encode(decoded)
	return ids, decoded, ids_rt


def run_cases() -> None:
	tokenizer = get_tokenizer()
	cases = [
		"01",
		"0001",
		"00001",
		"o1",
		"oooo1",
		"0 1",
		"0\n1",
		"zero 1",
		"0o01",
		"0o0o1",
	]

	print("Whisper tokenizer diagnostic (0 vs o)\n")
	for text in cases:
		ids, decoded, ids_rt = round_trip(tokenizer, text)
		stable = ids == ids_rt
		print(json.dumps({
			"text": text,
			"ids": ids,
			"decoded": decoded,
			"ids_roundtrip": ids_rt,
			"stable_roundtrip": stable,
		}, ensure_ascii=False))

	# Probe repeated zeros of varying lengths only
	print("\nSweep: repeated zeros length 1..8 followed by '1'\n")
	for n in range(1, 9):
		text = ("0" * n) + "1"
		ids, decoded, ids_rt = round_trip(tokenizer, text)
		print(json.dumps({
			"pattern": f"{'0'*n}1",
			"ids": ids,
			"decoded": decoded,
			"ids_roundtrip": ids_rt,
			"stable_roundtrip": ids == ids_rt,
		}, ensure_ascii=False))


if __name__ == "__main__":
	run_cases()


