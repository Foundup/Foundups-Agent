import os, csv, json, argparse
import numpy as np

# ===== Pauli and helpers =====
I = np.eye(2, dtype=complex)
Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)


def dagger(M):
	return M.conj().T


# ===== Operators (symbolic alphabet) =====
def H_entangle(k):  # '^'
	return k * Y


def H_cohere(k):  # '&'
	return k * Z


def L_distort(k):  # '#'
	return k * np.array([[0, 1], [0, 0]], dtype=complex)


# ===== Dynamics =====
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


# ===== Observables =====
def compute_observables(rho):
	C = rho[1, 1].real
	E = abs(rho[0, 1])
	rx = 2 * rho[0, 1].real
	ry = -2 * rho[0, 1].imag
	rz = rho[1, 1].real - rho[0, 0].real
	rnorm = float(np.sqrt(rx * rx + ry * ry + rz * rz))
	purity = float(np.real(np.trace(rho @ rho)))
	w = np.linalg.eigvalsh(rho)
	_eps = 1e-12
	S = -float(np.sum([wi * np.log(max(wi, _eps)) for wi in w if wi > _eps]))
	return C, E, rnorm, purity, S


# ===== Geometry meter (det(g)) =====
class GeomMeter:
	def __init__(self, win=64, thr_k=6.0, thr_floor=1e-10):
		self.Cs = []
		self.Es = []
		self.win = win
		self.det_hist = []
		self.thr_k = thr_k
		self.thr_floor = thr_floor

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
		if len(self.det_hist) > 5000:
			self.det_hist.pop(0)
		return d

	def threshold(self):
		if len(self.det_hist) < 50:
			return 1e-6
		arr = np.abs(np.array(self.det_hist[-300:]))
		med = np.median(arr)
		mad = np.median(np.abs(arr - med)) + 1e-15
		return max(self.thr_floor, float(self.thr_k * mad))


# ===== Resonance detector (sliding FFT over E(t)) =====
class ResonanceDetector:
	def __init__(self, win=512, target=7.05, tol=0.05):
		self.Es = []
		self.win = win
		self.target = target
		self.tol = tol
		# Per WSP 84: Extend for harmonic detection (S10 in ROADMAP)
		self.harmonic_bands = {
			"subharmonic_f/2": target / 2,
			"fundamental_f": target,
			"harmonic_2f": target * 2,
			"harmonic_3f": target * 3
		}

	def push(self, E):
		self.Es.append(E)
		if len(self.Es) > self.win:
			self.Es.pop(0)

	def detect(self, dt, top_k=3):
		if len(self.Es) < self.win:
			return None
		x = np.array(self.Es[-self.win :])
		x = x - np.mean(x)
		spec = np.fft.rfft(x)
		freqs = np.fft.rfftfreq(self.win, d=dt)
		mag = np.abs(spec)
		mag[0] = 0.0
		idxs = np.argsort(mag)[-top_k:][::-1]
		top = [(float(freqs[i]), float(mag[i])) for i in idxs]
		# Hit near target frequency
		mask = np.where(np.abs(freqs - self.target) <= self.tol)[0]
		hit = None
		if mask.size:
			i = int(mask[np.argmax(mag[mask])])
			hit = (float(freqs[i]), float(mag[i]))
		
		# Harmonic fingerprint detection (S10)
		harmonics = {}
		for band_name, band_freq in self.harmonic_bands.items():
			band_mask = np.where(np.abs(freqs - band_freq) <= self.tol)[0]
			if band_mask.size:
				band_i = int(band_mask[np.argmax(mag[band_mask])])
				harmonics[band_name] = {
					"freq": float(freqs[band_i]),
					"power": float(mag[band_i])
				}
			else:
				harmonics[band_name] = {"freq": band_freq, "power": 0.0}
		
		return {"top": top, "hit": hit, "harmonics": harmonics}


# ===== Symbol source with steps_per_sym =====
class SymbolSource:
	def __init__(self, script, steps_per_sym=100):
		self.script = script or "^&#"
		self.steps_per_sym = max(1, int(steps_per_sym))
		self.ptr = 0
		self.counter = 0

	def next_symbol(self):
		if not self.script:
			return "."
		sym = self.script[self.ptr]
		self.counter += 1
		if self.counter >= self.steps_per_sym:
			self.counter = 0
			self.ptr = (self.ptr + 1) % len(self.script)
		return sym


# ===== Main run =====
def run(
	log_csv_path: str,
	events_path: str,
	script: str,
	steps: int,
	steps_per_sym: int,
	base_dt: float,
	geom_win: int,
	reso_win: int,
	reso_tol: float,
	consec: int,
	kE: float,
	kA: float,
	gD: float,
	seed: int,
):
	rng = np.random.default_rng(seed)
	rho = np.array([[0.9, 0.0], [0.0, 0.1]], dtype=complex)
	source = SymbolSource(script, steps_per_sym)
	geom = GeomMeter(win=geom_win)
	reso = ResonanceDetector(win=reso_win, target=7.05, tol=reso_tol)

	# Prepare logging
	with open(log_csv_path, "w", newline="") as fcsv, open(events_path, "w") as fev:
		writer = csv.writer(fcsv)
		writer.writerow([
			"t",
			"step",
			"sym",
			"C",
			"E",
			"rnorm",
			"purity",
			"S",
			"detg",
			"det_thr",
			"reso_hit_freq",
			"reso_hit_mag",
			"ew_varE",
			"ew_ac1E",
			"ew_dS",
			# Harmonic fingerprint columns (S10)
			"harm_sub_power",
			"harm_fund_power",
			"harm_2f_power",
			"harm_3f_power",
		])

		events_count = 0
		zcount = 0
		t = 0.0

		# Early-warning buffers
		E_win = []
		prev_S = None

		for step in range(steps):
			# time jitter-free for v2 simplicity (resilience handled by windowing)
			dt = base_dt
			sym = source.next_symbol()

			# Select operators
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

			# Evolve
			rho = lindblad_step(rho, H, Ls, gs, dt)
			C, E, rnorm, purity, S = compute_observables(rho)

			# Metrics
			geom.push(C, E)
			detg = geom.detg()
			det_thr = geom.threshold()
			reso.push(E)
			pk = reso.detect(dt, top_k=3)
			reso_freq = pk["hit"][0] if pk and pk["hit"] else ""
			reso_mag = pk["hit"][1] if pk and pk["hit"] else ""

			# Flags
			flags = []
			if detg is not None and abs(detg) < det_thr:
				zcount += 1
			else:
				zcount = 0
			if zcount >= consec:
				flags.append("PQN_DETECTED")
				zcount = 0
			if pk and pk["hit"]:
				flags.append("RESONANCE_HIT")
			if detg is not None and abs(detg) < det_thr and purity < 0.8 and S > 0.3:
				flags.append("PARADOX_RISK")

			# Early-warning metrics
			E_win.append(E)
			if len(E_win) > max(geom_win, 16):
				E_win.pop(0)
			if len(E_win) >= 3:
				arr = np.array(E_win, dtype=float)
				varE = float(np.var(arr))
				# lag-1 autocorr
				arr0 = arr[:-1] - np.mean(arr[:-1])
				arr1 = arr[1:] - np.mean(arr[1:])
				denom = float(np.sqrt(np.sum(arr0*arr0)) * np.sqrt(np.sum(arr1*arr1)))
				ac1 = float(np.sum(arr0*arr1)/denom) if denom > 0 else 0.0
			else:
				varE = 0.0
				ac1 = 0.0
			dS = (S - prev_S) if (prev_S is not None) else 0.0
			prev_S = S

			# Extract harmonic powers (S10)
			harm_powers = {
				"sub": pk["harmonics"]["subharmonic_f/2"]["power"] if pk and "harmonics" in pk else 0.0,
				"fund": pk["harmonics"]["fundamental_f"]["power"] if pk and "harmonics" in pk else 0.0,
				"2f": pk["harmonics"]["harmonic_2f"]["power"] if pk and "harmonics" in pk else 0.0,
				"3f": pk["harmonics"]["harmonic_3f"]["power"] if pk and "harmonics" in pk else 0.0,
			}

			# Log row
			writer.writerow([
				f"{t:.6f}",
				step,
				sym,
				f"{C:.6f}",
				f"{E:.6f}",
				f"{rnorm:.6f}",
				f"{purity:.6f}",
				f"{S:.6f}",
				("" if detg is None else f"{detg:.12e}"),
				("" if detg is None else f"{det_thr:.12e}"),
				("") if reso_freq == "" else f"{reso_freq:.3f}",
				("") if reso_mag == "" else f"{reso_mag:.6f}",
				f"{varE:.6f}",
				f"{ac1:.6f}",
				f"{dS:.6f}",
				# Harmonic fingerprint data
				f"{harm_powers['sub']:.6f}",
				f"{harm_powers['fund']:.6f}",
				f"{harm_powers['2f']:.6f}",
				f"{harm_powers['3f']:.6f}",
			])

			# Log events
			if flags:
				evt = {
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
					"reso_hit": (pk["hit"] if pk else None),
					"flags": flags,
				}
				fev.write(json.dumps(evt) + "\n")
				events_count += 1

			t += dt

	return True


def main():
	ap = argparse.ArgumentParser()
	ap.add_argument("--script", type=str, default="^^^^&&&###^&#")
	ap.add_argument("--steps", type=int, default=3000)
	ap.add_argument("--steps_per_sym", type=int, default=120)
	ap.add_argument("--dt", type=float, default=0.5 / 7.05)
	ap.add_argument("--geom_win", type=int, default=64)
	ap.add_argument("--reso_win", type=int, default=512)
	ap.add_argument("--reso_tol", type=float, default=0.05)
	ap.add_argument("--consec", type=int, default=10)
	ap.add_argument("--kE", type=float, default=0.35)
	ap.add_argument("--kA", type=float, default=0.25)
	ap.add_argument("--gD", type=float, default=0.08)
	ap.add_argument("--seed", type=int, default=0)
	ap.add_argument("--out_dir", type=str, default=os.path.join(os.path.dirname(__file__), "logs"))
	ap.add_argument("--log_csv", type=str, default="cmst_v2_log.csv")
	ap.add_argument("--events", type=str, default="cmst_v2_events.txt")
	args = ap.parse_args()

	# Resolve output paths under out_dir
	out_dir = args.out_dir or "."
	os.makedirs(out_dir, exist_ok=True)
	log_csv_path = args.log_csv if os.path.isabs(args.log_csv) else os.path.join(out_dir, args.log_csv)
	events_path = args.events if os.path.isabs(args.events) else os.path.join(out_dir, args.events)

	run(
		log_csv_path=log_csv_path,
		events_path=events_path,
		script=args.script,
		steps=args.steps,
		steps_per_sym=args.steps_per_sym,
		base_dt=args.dt,
		geom_win=args.geom_win,
		reso_win=args.reso_win,
		reso_tol=args.reso_tol,
		consec=args.consec,
		kE=args.kE,
		kA=args.kA,
		gD=args.gD,
		seed=args.seed,
	)


if __name__ == "__main__":
	main()


