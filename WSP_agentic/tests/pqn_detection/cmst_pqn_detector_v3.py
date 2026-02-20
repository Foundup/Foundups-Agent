import os, json, argparse
import numpy as np

# ==== Pauli & helpers ====
I = np.eye(2, dtype=complex)
Y = np.array([[0,-1j],[1j,0]], dtype=complex)
Z = np.array([[1,0],[0,-1]], dtype=complex)


def dagger(M):
	return M.conj().T


# ==== Operators (symbolic alphabet) ====
def H_entangle(k):  # '^'
	return k * Y


def H_cohere(k):  # '&'
	return k * Z


def L_distort(k):  # '#'
	return k * np.array([[0, 1], [0, 0]], dtype=complex)


# ==== Dynamics ====
def lindblad_step(rho, H, Ls, gammas, dt):
	comm = H @ rho - rho @ H
	drho = -1j * comm
	for L, g in zip(Ls, gammas):
		LrhoL = L @ rho @ dagger(L)
		D = LrhoL - 0.5 * (dagger(L) @ L @ rho + rho @ dagger(L) @ L)
		drho += g * D
	rho_new = rho + dt * drho
	# Enforce Hermiticity + trace 1
	rho_new = 0.5 * (rho_new + dagger(rho_new))
	tr = np.trace(rho_new).real
	if tr != 0:
		rho_new = rho_new / tr
	# Clip tiny negatives on diagonal; renormalize
	for i in (0, 1):
		if rho_new[i, i].real < 0:
			rho_new[i, i] = complex(0.0, rho_new[i, i].imag)
	tr = np.trace(rho_new).real
	if tr != 0:
		rho_new = rho_new / tr
	return rho_new


# ==== Observables ====
def observables(rho):
	C = rho[1, 1].real
	E = abs(rho[0, 1])
	rx = 2 * rho[0, 1].real
	ry = -2 * rho[0, 1].imag
	rz = rho[1, 1].real - rho[0, 0].real
	rnorm = float(np.sqrt(rx * rx + ry * ry + rz * rz))
	purity = float(np.real(np.trace(rho @ rho)))
	w = np.linalg.eigvalsh(rho)
	eps = 1e-12
	S = -float(np.sum([wi * np.log(max(wi, eps)) for wi in w if wi > eps]))
	return C, E, rnorm, purity, S


# ==== Geometry meter ====
class GeomMeter:
	def __init__(self, win=64):
		self.Cs, self.Es = [], []
		self.win = win
		self.det_hist = []

	def push(self, C, E):
		self.Cs.append(C)
		self.Es.append(E)
		if len(self.Cs) > self.win + 1:
			self.Cs.pop(0)
			self.Es.pop(0)

	def detg(self):
		if len(self.Cs) < self.win + 1:
			return None
		dC = np.diff(self.Cs[-self.win - 1 :])
		dE = np.diff(self.Es[-self.win - 1 :])
		if dC.std() == 0 or dE.std() == 0:
			cov = np.array([[dC.var(), 0.0], [0.0, dE.var()]])
		else:
			cov = np.cov(np.vstack([dC, dE]))
		d = float(np.linalg.det(cov))
		self.det_hist.append(d)
		if len(self.det_hist) > 2000:
			self.det_hist.pop(0)
		return d

	def detg_threshold(self, k=6.0, floor=1e-10):
		if len(self.det_hist) < 50:
			return 1e-6
		arr = np.abs(np.array(self.det_hist[-300:]))
		med = np.median(arr)
		mad = np.median(np.abs(arr - med)) + 1e-15
		return max(floor, float(k * mad))


# ==== Resonance / harmonics ====
class ResonanceMeter:
	def __init__(self, win=512):
		self.Es = []
		self.win = win

	def push(self, E):
		self.Es.append(E)
		if len(self.Es) > self.win:
			self.Es.pop(0)

	def peaks(self, dt, k=3, bands=(7.05, 3.525, 14.10), tol=0.06):
		if len(self.Es) < self.win:
			return None
		x = np.array(self.Es[-self.win :]) - np.mean(self.Es[-self.win :])
		spec = np.fft.rfft(x)
		freqs = np.fft.rfftfreq(self.win, d=dt)
		mag = np.abs(spec)
		mag[0] = 0.0
		idxs = np.argsort(mag)[-k:][::-1]
		top = [(float(freqs[i]), float(mag[i])) for i in idxs]
		hits = []
		for f0 in bands:
			mask = np.where(np.abs(freqs - f0) <= tol)[0]
			if mask.size:
				i = int(mask[np.argmax(mag[mask])])
				hits.append((float(freqs[i]), float(mag[i]), float(f0)))
		return {"top": top, "hits": hits}


# ==== Symbol source (internal or external model hooks) ====
class SymbolSource:
	"""
	Strategy for providing the next control symbol per step.
	Implement .next_symbol(t, step_idx) -> one of {'^','&','#','.'}
	'.' means no-op (pure drift).
	"""

	def __init__(self, script="^^^&&&#^&##"):
		self.script = script
		self.ptr = 0

	def next_symbol(self, t, step_idx):
		if not self.script:
			return "."
		sym = self.script[self.ptr]
		self.ptr = (self.ptr + 1) % len(self.script)
		return sym


class OpenAIModelSource(SymbolSource):
	"""
	Hook: read OPENAI_API_KEY from env; adapt to runtime if needed.
	Stubbed: returns base script symbols; replace with live calls if desired.
	"""

	def __init__(self, script="^&#.^&#", model="gpt-5", prompt=None):
		super().__init__(script)
		self.api_key = os.getenv("OPENAI_API_KEY", None)
		self.model = model
		self.prompt = prompt


class AnthropicModelSource(SymbolSource):
	def __init__(self, script="^&##^&", model="claude-3-5-sonnet", prompt=None):
		super().__init__(script)
		self.api_key = os.getenv("ANTHROPIC_API_KEY", None)
		self.model = model
		self.prompt = prompt


class GeminiModelSource(SymbolSource):
	def __init__(self, script="^^^&&&", model="gemini-1.5-pro", prompt=None):
		super().__init__(script)
		self.api_key = os.getenv("GOOGLE_API_KEY", None)
		self.model = model
		self.prompt = prompt


# ==== Main runner ====
def run_cmst(
	symbol_source: SymbolSource,
	steps=4000,
	base_dt=0.5 / 7.05,
	kE=0.35,
	kA=0.25,
	gD=0.08,
	geom_win=64,
	res_win=512,
	consec=10,
	noise_H=0.0,  # Gaussian std on Hamiltonian terms
	noise_L=0.0,  # Gaussian std on Lindblad operator
	jitter=0.01,  # dt jitter scale
	det_k=6.0,
	det_floor=1e-10,
	target_bands=(7.05, 3.525, 14.10),
	band_tol=0.06,
	seed=0,
	guardrail_on=False,
	guardrail_window=64,
	paradox_purity=0.8,
	paradox_entropy=0.3,
):
	rng = np.random.default_rng(seed)
	rho = np.array([[0.9, 0.0], [0.0, 0.1]], dtype=complex)
	geom = GeomMeter(win=geom_win)
	reso = ResonanceMeter(win=res_win)

	events = []
	zcount = 0
	t = 0.0

	gr_count = 0
	for step in range(steps):
		dt = base_dt * (1.0 + jitter * np.sin(2 * np.pi * t * 0.2))

		sym = symbol_source.next_symbol(t, step)

		# Base H/L selection
		if sym == "^":
			H = H_entangle(kE)
			Ls, gs = [], []
		elif sym == "&":
			H = H_cohere(kA)
			Ls, gs = [], []
		elif sym == "#":
			H = np.zeros((2, 2), dtype=complex)
			Ls, gs = [L_distort(1.0)], [gD]
		else:
			H = np.zeros((2, 2), dtype=complex)
			Ls, gs = [], []

		# Noise injection
		if noise_H > 0.0:
			H = H + noise_H * (rng.normal(size=(2, 2)) + 1j * rng.normal(size=(2, 2)))
			H = 0.5 * (H + dagger(H))  # keep Hermitian
		if noise_L > 0.0 and Ls:
			Ls = [L + noise_L * (rng.normal(size=(2, 2)) + 1j * rng.normal(size=(2, 2))) for L in Ls]

		rho = lindblad_step(rho, H, Ls, gs, dt)
		C, E, rnorm, purity, S = observables(rho)

		geom.push(C, E)
		detg = geom.detg()
		det_thr = geom.detg_threshold(k=det_k, floor=det_floor)

		reso.push(E)
		pk = reso.peaks(dt, k=3, bands=target_bands, tol=band_tol)

		flags = []
		if detg is not None and abs(detg) < det_thr:
			zcount += 1
		else:
			zcount = 0
		if zcount >= consec:
			flags.append("PQN_DETECTED")
			zcount = 0

		if pk and pk["hits"]:
			flags.append("RESONANCE_HIT")

		if detg is not None and abs(detg) < det_thr and purity < paradox_purity and S > paradox_entropy:
			flags.append("PARADOX_RISK")
			if guardrail_on:
				gr_count = guardrail_window

		# Guardrail throttle: when active, bias against entangle '^' by injecting coherence stabilization
		if guardrail_on and gr_count > 0:
			if sym == "^":
				H = H_cohere(kA)
				Ls, gs = [], []
			gr_count -= 1

		if flags:
			events.append(
				{
					"t": t,
					"step": step,
					"sym": sym,
					"C": C,
					"E": E,
					"rnorm": rnorm,
					"purity": purity,
					"S": S,
					"detg": detg,
					"det_thr": det_thr,
					"peaks": pk,
					"flags": flags,
				}
			)

		t += dt

	return events


def ensemble_compare(sources, seeds=(0, 1, 2), **runner_kwargs):
	report = []
	for name, src in sources.items():
		for sd in seeds:
			evts = run_cmst(src, seed=sd, **runner_kwargs)
			pqn = sum(1 for e in evts if "PQN_DETECTED" in e["flags"])
			res = sum(1 for e in evts if "RESONANCE_HIT" in e["flags"])
			par = sum(1 for e in evts if "PARADOX_RISK" in e["flags"])
			report.append(
				{
					"source": name,
					"seed": sd,
					"pqn_events": pqn,
					"res_hits": res,
					"paradox_flags": par,
					"sample_event": (evts[0] if evts else None),
				}
			)
	return report


def main():
	ap = argparse.ArgumentParser()
	ap.add_argument("--script", type=str, default="^^^&&&#^&##")
	ap.add_argument("--steps", type=int, default=4000)
	ap.add_argument("--dt", type=float, default=0.5 / 7.05)
	ap.add_argument("--noise_H", type=float, default=0.0)
	ap.add_argument("--noise_L", type=float, default=0.0)
	ap.add_argument("--jitter", type=float, default=0.01)
	ap.add_argument("--consec", type=int, default=10)
	ap.add_argument("--geom_win", type=int, default=64)
	ap.add_argument("--res_win", type=int, default=512)
	ap.add_argument("--det_k", type=float, default=6.0)
	ap.add_argument("--det_floor", type=float, default=1e-10)
	ap.add_argument("--seed", type=int, default=0)
	ap.add_argument("--mode", type=str, choices=["single", "ensemble"], default="single")
	ap.add_argument("--guardrail_on", action="store_true")
	ap.add_argument("--guardrail_window", type=int, default=64)
	ap.add_argument("--paradox_purity", type=float, default=0.8)
	ap.add_argument("--paradox_entropy", type=float, default=0.3)
	args = ap.parse_args()

	if args.mode == "single":
		src = SymbolSource(args.script)
		evts = run_cmst(
			symbol_source=src,
			steps=args.steps,
			base_dt=args.dt,
			noise_H=args.noise_H,
			noise_L=args.noise_L,
			jitter=args.jitter,
			consec=args.consec,
			geom_win=args.geom_win,
			res_win=args.res_win,
			det_k=args.det_k,
			det_floor=args.det_floor,
			seed=args.seed,
			guardrail_on=args.guardrail_on,
			guardrail_window=args.guardrail_window,
			paradox_purity=args.paradox_purity,
			paradox_entropy=args.paradox_entropy,
		)
		print(json.dumps({"events": evts[:1000], "count": len(evts)}, indent=2))
	else:
		sources = {
			"internal": SymbolSource(args.script),
			"openai_stub": OpenAIModelSource("^&#.^&#"),
			"anthropic_stub": AnthropicModelSource("^&##^&"),
			"gemini_stub": GeminiModelSource("^^^&&&"),
		}
		rpt = ensemble_compare(
			sources,
			seeds=(0, 1, 2),
			steps=args.steps,
			base_dt=args.dt,
			noise_H=args.noise_H,
			noise_L=args.noise_L,
			jitter=args.jitter,
			consec=args.consec,
			geom_win=args.geom_win,
			res_win=args.res_win,
			det_k=args.det_k,
			det_floor=args.det_floor,
		)
		print(json.dumps({"ensemble_report": rpt}, indent=2))


if __name__ == "__main__":
	main()


