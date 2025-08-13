import re
from typing import List, Tuple


try:
	import whisper
except ImportError as exc:
	raise SystemExit("Install openai-whisper to run this probe: pip install openai-whisper") from exc


def get_encoding():
	"""Return (tokenizer, encoding) where encoding is a tiktoken.Encoding if available."""
	tok = whisper.tokenizer.get_tokenizer(multilingual=True, language="en", task="transcribe")
	enc = getattr(tok, "tokenizer", None)
	return tok, enc


def show(enc, tok, s: str) -> None:
	ids = tok.encode(s)
	if enc is not None:
		pieces: List[str] = []
		for tid in ids:
			try:
				pieces.append(enc.decode_single_token_bytes(tid).decode("utf-8", "replace"))
			except Exception:
				pieces.append("<UNK>")
	else:
		pieces = ["<NA>"] * len(ids)
	print(f"{s!r:>10} -> {ids}  {pieces} (len={len(ids)})")


def find(enc, pattern: str, limit: int = 25) -> List[Tuple[int, str]]:
	if enc is None:
		return []
	rx = re.compile(pattern)
	hits: List[Tuple[int, str]] = []
	for tid in range(enc.n_vocab):
		try:
			text = enc.decode_single_token_bytes(tid).decode("utf-8", "ignore")
		except Exception:
			continue
		if rx.fullmatch(text):
			hits.append((tid, text))
			if len(hits) >= limit:
				break
	return hits


def main() -> None:
	tok, enc = get_encoding()

	print("Whisper BPE probe (token splits via Whisper tokenizer)\n")
	tests = [
		"0",
		"00",
		"000",
		"0001",
		"00001",
		"01",
		"10",
		"o",
		"oo",
		"oooo",
		"o1",
		"oooo1",
	]
	for t in tests:
		show(enc, tok, t)

	print("\nCandidate merges present in vocab:")
	for pat in [r"0{3}1", r"0+", r"o+", r"[0o]+1", r"01", r"o1"]:
		print(pat, find(enc, pat))


if __name__ == "__main__":
	main()


