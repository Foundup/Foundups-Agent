import os
from typing import List

try:
	from gtts import gTTS
except ImportError as exc:
	raise SystemExit("Install gTTS first: pip install gTTS") from exc

try:
	from google.cloud import speech_v2 as speech
except ImportError as exc:
	raise SystemExit("Install Google Cloud Speech v2: pip install google-cloud-speech") from exc


def synthesize_speech(text: str, out_path: str) -> None:
	ts = gTTS(text=text, lang="en")
	ts.save(out_path)


def transcribe_gcp(mp3_path: str, project_id: str, location: str = "global") -> str:
	client = speech.SpeechClient()
	recognizer = f"projects/{project_id}/locations/{location}/recognizers/_"

	with open(mp3_path, "rb") as f:
		audio_content = f.read()

	config = speech.RecognitionConfig(
		auto_decoding_config=speech.AutoDetectDecodingConfig(),
		features=speech.RecognitionFeatures(enable_automatic_punctuation=False),
		language_codes=["en-US"],
	)

	request = speech.RecognizeRequest(
		recognizer=recognizer,
		config=config,
		content=audio_content,
	)

	resp = client.recognize(request=request)
	if resp.results and resp.results[0].alternatives:
		return resp.results[0].alternatives[0].transcript.strip()
	return ""


def run_wave_pattern_test() -> None:
	project_id = os.environ.get("GCP_PROJECT_ID", "")
	if not project_id:
		raise SystemExit("Set GCP_PROJECT_ID env var to your project ID")
	if not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
		raise SystemExit("Set GOOGLE_APPLICATION_CREDENTIALS to your service account JSON path")

	print("--- Starting Chirp Wave-Pattern Test ---")
	print("Method: gTTS (audio generation) -> GCP Speech-to-Text v2 (transcription)\n")

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
		mp3_path = "_tmp_gcp_wave_pattern.mp3"
		synthesize_speech(p, mp3_path)
		text = transcribe_gcp(mp3_path, project_id=project_id)
		print(f"Testing phrase: '{p}'")
		print(f"  -> GCP Transcribed: '{text}'")
		print("-" * 30)
		try:
			os.remove(mp3_path)
		except Exception:
			pass


if __name__ == "__main__":
	run_wave_pattern_test()


