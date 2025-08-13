import numpy as np
import librosa
import librosa.display
import matplotlib.pyplot as plt
from scipy.io.wavfile import write


def demonstrate_whisper_preprocessing():
	"""
	Demonstrate the audio preprocessing pipeline consistent with OpenAI Whisper:
	- 16 kHz mono load
	- STFT with n_fft=400 (25 ms) and hop_length=160 (10 ms)
	- 80-bin Mel filterbank
	- Log-Mel conversion
	"""
	# 1) Generate dummy audio: 2.5s of 440 Hz then 2.5s of 880 Hz
	SAMPLE_RATE = 16000
	DURATION_S = 5
	FREQ1 = 440.0
	FREQ2 = 880.0

	t = np.linspace(0.0, DURATION_S, int(SAMPLE_RATE * DURATION_S), endpoint=False)
	amplitude = np.iinfo(np.int16).max * 0.5
	data = np.zeros_like(t)
	halfway_point = int(len(t) / 2)
	data[:halfway_point] = amplitude * np.sin(2.0 * np.pi * FREQ1 * t[:halfway_point])
	data[halfway_point:] = amplitude * np.sin(2.0 * np.pi * FREQ2 * t[halfway_point:])

	dummy_audio_file = "test_tone.wav"
	write(dummy_audio_file, SAMPLE_RATE, data.astype(np.int16))
	print(f"Generated a dummy audio file: {dummy_audio_file}")

	# 2) Whisper front-end
	y, sr = librosa.load(dummy_audio_file, sr=SAMPLE_RATE, mono=True)

	N_FFT = 400
	HOP_LENGTH = 160
	N_MELS = 80

	mel_spectrogram = librosa.feature.melspectrogram(
		y=y,
		sr=sr,
		n_fft=N_FFT,
		hop_length=HOP_LENGTH,
		n_mels=N_MELS,
	)
	log_mel_spectrogram = librosa.power_to_db(mel_spectrogram, ref=np.max)

	print("\n--- Whisper Front-End Diagnostics ---")
	print(f"Log-Mel shape: {log_mel_spectrogram.shape} (mels, frames)")
	print(f"Mel bins: {log_mel_spectrogram.shape[0]}")
	print(f"Frames: {log_mel_spectrogram.shape[1]}")

	# 3) Visualize
	fig, ax = plt.subplots(figsize=(12, 5))
	img = librosa.display.specshow(
		log_mel_spectrogram,
		sr=sr,
		hop_length=HOP_LENGTH,
		x_axis="time",
		y_axis="mel",
		ax=ax,
	)
	fig.colorbar(img, ax=ax, format="%+2.0f dB", label="Intensity (dB)")
	ax.set_title("Log-Mel Spectrogram (Whisper-compatible)")
	plt.tight_layout()
	plt.show()


if __name__ == "__main__":
	demonstrate_whisper_preprocessing()


