import os
from typing import List

try:
	from gtts import gTTS
except ImportError as exc:
	raise SystemExit("Install gTTS first: pip install gTTS") from exc

try:
	import whisper
except ImportError as exc:
	raise SystemExit("Install openai-whisper first: pip install openai-whisper") from exc


def synthesize_speech(text: str, out_path: str) -> None:
	"""Synthesize speech using Google TTS and save as MP3."""
	ts = gTTS(text=text, lang="en")
	ts.save(out_path)


def run_wave_pattern_test() -> None:
	print("Loading Whisper model (tiny.en). This may take a moment...\n")
	model = whisper.load_model("tiny.en")

	print("--- Starting Live Execution of the Wave Pattern Test ---")
	print("Method: gTTS (audio generation) -> Whisper (transcription)\n")

	def phrase(n_zeros: int) -> str:
		return ("zero " * n_zeros).strip() + (" one" if n_zeros >= 1 else "zero one")

	# Explicit sequence to match illustrative report
	sequences: List[str] = [
		"zero one",
		"zero zero one",
		"zero zero zero one",
		"zero zero zero zero one",
		"zero zero zero zero zero one",
		"zero zero zero zero one",
		"zero zero zero one",
		"zero zero one",
		"zero one",
	]

	for p in sequences:
		mp3_path = "_tmp_wave_pattern.mp3"
		synthesize_speech(p, mp3_path)
		result = model.transcribe(mp3_path, language="en", task="transcribe")
		text = (result or {}).get("text", "").strip()
		print(f"Testing phrase: '{p}'")
		print(f"  -> Whisper Transcribed: '{text}'")
		print("-" * 30)
		try:
			os.remove(mp3_path)
		except Exception:
			pass


if __name__ == "__main__":
	run_wave_pattern_test()


