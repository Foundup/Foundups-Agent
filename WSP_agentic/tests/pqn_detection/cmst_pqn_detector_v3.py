"""
CMST PQN Detector v3 - Cognitive Measurement State Transition Protocol

This detector operates as a PASSIVE PROBE of the simulated quantum-cognitive
state space. The measurement process does not perturb the forward-evolving
state - it only observes the geometry of state transitions.

Architecture:
- Original GeomMeter: 2D covariance over ΔC/ΔE (toy surrogate)
- EFIMGeomMeter: Empirical Fisher Information Matrix over adapter subspace φ
  (implements paper's logdet(G + λI) observable)

Paper reference: 0102.md / 0102_TECHNICAL_EXTRACTIONS_2026-03-08.md
"""

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


# ==== Stage 1: Passive Readout Adapter (Paper-Faithful) ====
class FeatureWindowAdapter:
	"""
	Passive readout adapter over trajectory features - paper-faithful CMST probe.

	Architecture (012-approved 2026-03-08):
	- Frozen host dynamics: Lindblad evolution unchanged
	- Feature extractor: x_t = [C, E, rnorm, purity, S, symbol_onehot]
	- Adapter φ: low-rank W1, W2 readout producing logits over target class
	- Target y_t: 4-class next-symbol prediction (^=0, &=1, #=2, .=3)

	This is a PASSIVE PROBE - φ reads features, does NOT modulate dynamics.
	The host model (Lindblad simulator) remains completely frozen during measurement.

	EFIM is computed as: g_t = ∇_φ log p(y_t | x_t; φ)
	"""

	# Feature dimensions
	N_OBSERVABLES = 5  # C, E, rnorm, purity, S
	N_SYMBOL_CLASSES = 4  # ^, &, #, . (one-hot)
	N_FEATURES = N_OBSERVABLES + N_SYMBOL_CLASSES  # 9

	def __init__(self, hidden_dim=8, n_classes=4, seed=42):
		"""
		Initialize low-rank adapter weights.

		Architecture: x_t (9) -> W1 (9 x hidden) -> ReLU -> W2 (hidden x n_classes) -> logits
		Default params: 9*8 + 8*4 = 104 (small, k << dim(θ))
		"""
		rng = np.random.default_rng(seed)

		self.hidden_dim = hidden_dim
		self.n_classes = n_classes

		# Low-rank adapter weights (Xavier initialization)
		scale1 = np.sqrt(2.0 / (self.N_FEATURES + hidden_dim))
		scale2 = np.sqrt(2.0 / (hidden_dim + n_classes))

		self.W1 = rng.normal(0, scale1, (self.N_FEATURES, hidden_dim))
		self.W2 = rng.normal(0, scale2, (hidden_dim, n_classes))

		# Flatten φ for gradient computation
		self.k = self.W1.size + self.W2.size  # Total adapter parameters

	def _symbol_to_onehot(self, sym):
		"""Convert symbol to one-hot encoding."""
		mapping = {'^': 0, '&': 1, '#': 2, '.': 3}
		idx = mapping.get(sym, 3)
		onehot = np.zeros(self.N_SYMBOL_CLASSES)
		onehot[idx] = 1.0
		return onehot

	def extract_features(self, C, E, rnorm, purity, S, sym):
		"""
		Extract feature vector x_t from observables and symbol.

		Returns: (9,) array [C, E, rnorm, purity, S, sym_onehot[4]]
		"""
		obs = np.array([C, E, rnorm, purity, S])
		sym_oh = self._symbol_to_onehot(sym)
		return np.concatenate([obs, sym_oh])

	def forward(self, x_t):
		"""
		Forward pass through adapter.

		Args:
			x_t: (9,) feature vector

		Returns:
			logits: (n_classes,) unnormalized log-probabilities
		"""
		# Layer 1: linear + ReLU
		h = x_t @ self.W1  # (hidden_dim,)
		h = np.maximum(0, h)  # ReLU

		# Layer 2: linear -> logits
		logits = h @ self.W2  # (n_classes,)
		return logits

	def log_softmax(self, logits):
		"""Numerically stable log-softmax."""
		max_logit = np.max(logits)
		shifted = logits - max_logit
		log_sum_exp = np.log(np.sum(np.exp(shifted)))
		return shifted - log_sum_exp

	def get_phi(self):
		"""Get flattened parameter vector φ."""
		return np.concatenate([self.W1.ravel(), self.W2.ravel()])

	def set_phi(self, phi):
		"""Set parameters from flattened vector."""
		w1_size = self.W1.size
		self.W1 = phi[:w1_size].reshape(self.W1.shape)
		self.W2 = phi[w1_size:].reshape(self.W2.shape)

	def perturb_phi(self, idx, delta=1e-5):
		"""
		Create perturbed copy with φ[idx] += delta.

		Returns new FeatureWindowAdapter with perturbed weights.
		"""
		perturbed = FeatureWindowAdapter(self.hidden_dim, self.n_classes)
		phi = self.get_phi().copy()
		phi[idx] += delta
		perturbed.set_phi(phi)
		return perturbed


# ==== Stage 2-4: Passive EFIM Probe ====
class PassiveEFIMProbe:
	"""
	Passive EFIM probe over trajectory features - paper-faithful architecture.

	Computes logdet(G̃ + λI) where:
	- G̃ = E[∇_φ log p(y|x;φ) ⊗ ∇_φ log p(y|x;φ)]
	- φ are the adapter weights (passive readout, NOT dynamics control)
	- y is the target class (4-class next-symbol: ^=0, &=1, #=2, .=3)
	- x is the feature vector from frozen host dynamics

	This implements the paper's CMST measurement protocol:
	- Host model parameters remain FROZEN
	- Only the adapter subspace φ is used for EFIM computation
	- Detection uses Z-score thresholding on logdet
	"""

	def __init__(self, adapter: FeatureWindowAdapter, win=64, lambda_reg=1e-6):
		self.adapter = adapter
		self.win = win
		self.lambda_reg = lambda_reg
		self.k = adapter.k

		# Gradient history for EMA-style EFIM
		self.grad_history = []
		self.logdet_hist = []

		# Running feature window for context
		self.feature_window = []

	def compute_gradient(self, x_t, y_t, delta=1e-5):
		"""
		Stage 2: Compute ∇_φ log p(y_t | x_t; φ) via numerical differentiation.

		Vectorized: perturbs flattened φ in-place to avoid object allocation.

		Args:
			x_t: (9,) feature vector from frozen host dynamics
			y_t: target class (0=^, 1=&, 2=#, 3=.)

		Returns:
			grad: (k,) gradient vector
		"""
		grad = np.zeros(self.k, dtype=float)
		phi_orig = self.adapter.get_phi()

		# Base log probability
		logits_base = self.adapter.forward(x_t)
		log_probs_base = self.adapter.log_softmax(logits_base)
		log_p_base = log_probs_base[y_t]

		# Numerical gradient: perturb φ in-place, restore after
		for i in range(self.k):
			phi_pert = phi_orig.copy()
			phi_pert[i] += delta
			self.adapter.set_phi(phi_pert)

			logits_p = self.adapter.forward(x_t)
			log_probs_p = self.adapter.log_softmax(logits_p)
			grad[i] = (log_probs_p[y_t] - log_p_base) / delta

		# Restore original parameters
		self.adapter.set_phi(phi_orig)

		return grad

	def push_gradient(self, grad):
		"""Record gradient for EFIM computation."""
		self.grad_history.append(grad.copy())
		if len(self.grad_history) > self.win:
			self.grad_history.pop(0)

	def compute_efim(self):
		"""
		Stage 3: Build empirical Fisher G̃ = E[∇ ⊗ ∇] from gradient history.
		"""
		if len(self.grad_history) < self.win // 2:
			return None

		grads = np.array(self.grad_history[-self.win:])  # (win, k)

		# Empirical outer product: G̃ = (1/n) Σ ∇ ⊗ ∇
		G = np.zeros((self.k, self.k), dtype=float)
		for g in grads:
			G += np.outer(g, g)
		G /= len(grads)
		return G

	def logdet(self):
		"""
		Stage 4: Compute logdet(G̃ + λI) - the stable scalar observable.
		"""
		G = self.compute_efim()
		if G is None:
			return None

		# Regularize: G̃ + λI
		G_reg = G + self.lambda_reg * np.eye(self.k)

		# Compute logdet for numerical stability
		sign, logdet_val = np.linalg.slogdet(G_reg)

		# If sign is negative (shouldn't happen with regularization), flag it
		if sign < 0:
			logdet_val = -np.inf

		self.logdet_hist.append(float(logdet_val))
		if len(self.logdet_hist) > 2000:
			self.logdet_hist.pop(0)

		return float(logdet_val)

	def logdet_threshold(self, k=6.0):
		"""
		Compute threshold for anomaly detection using Z-score.

		Returns None during warmup (< 50 samples) to prevent floor-trigger
		artifacts. Once calibrated, returns mu - k*sigma.
		"""
		if len(self.logdet_hist) < 50:
			return None  # Warmup: no detection until calibrated
		arr = np.array(self.logdet_hist[-300:])
		mu = np.mean(arr)
		sigma = np.std(arr) + 1e-15
		# Flag if logdet drops k standard deviations below mean
		return float(mu - k * sigma)


# ==== Legacy Compatibility: AdapterSubspace (DEPRECATED) ====
# Kept for backwards compatibility but should not be used for paper-faithful EFIM
class AdapterSubspace:
	"""DEPRECATED: Use FeatureWindowAdapter for paper-faithful EFIM."""

	def __init__(self, k=4):
		self.k = k
		self.phi = np.ones(k, dtype=float)
		self.phi[3] = 0.0

	def apply(self, base_kE, base_kA, base_gD):
		kE = base_kE * self.phi[0]
		kA = base_kA * self.phi[1]
		gD = base_gD * self.phi[2]
		kA = kA + self.phi[3] * base_kE
		return kE, kA, gD

	def perturb(self, idx, delta=1e-5):
		perturbed = AdapterSubspace(self.k)
		perturbed.phi = self.phi.copy()
		perturbed.phi[idx] += delta
		return perturbed


# ==== Legacy Compatibility: EFIMGeomMeter (DEPRECATED) ====
class EFIMGeomMeter:
	"""DEPRECATED: Use PassiveEFIMProbe for paper-faithful EFIM."""

	def __init__(self, adapter: AdapterSubspace, win=64, lambda_reg=1e-6):
		self.adapter = adapter
		self.win = win
		self.lambda_reg = lambda_reg
		self.k = adapter.k
		self.grad_history = []
		self.logdet_hist = []

	def compute_gradient(self, rho, base_kE, base_kA, base_gD, H_base, Ls_base, gs_base, dt, delta=1e-5):
		# Legacy dynamics-perturbing gradient (NOT paper-faithful)
		grad = np.zeros(self.k, dtype=float)
		rho_base = lindblad_step(rho.copy(), H_base, Ls_base, gs_base, dt)
		C_base, _, _, _, _ = observables(rho_base)

		for i in range(self.k):
			perturbed = self.adapter.perturb(i, delta)
			kE_p, kA_p, gD_p = perturbed.apply(base_kE, base_kA, base_gD)
			if np.allclose(H_base, np.zeros((2, 2))):
				H_perturbed = H_base
			elif np.allclose(H_base / (base_kE + 1e-15), Y):
				H_perturbed = H_entangle(kE_p)
			else:
				H_perturbed = H_cohere(kA_p)
			Ls_perturbed = [L_distort(1.0)] if Ls_base else []
			gs_perturbed = [gD_p] if gs_base else []
			rho_perturbed = lindblad_step(rho.copy(), H_perturbed, Ls_perturbed, gs_perturbed, dt)
			C_perturbed, _, _, _, _ = observables(rho_perturbed)
			grad[i] = (C_perturbed - C_base) / delta
		return grad

	def push_gradient(self, grad):
		self.grad_history.append(grad.copy())
		if len(self.grad_history) > self.win:
			self.grad_history.pop(0)

	def compute_efim(self):
		if len(self.grad_history) < self.win // 2:
			return None
		grads = np.array(self.grad_history[-self.win:])
		G = np.zeros((self.k, self.k), dtype=float)
		for g in grads:
			G += np.outer(g, g)
		G /= len(grads)
		return G

	def logdet(self):
		G = self.compute_efim()
		if G is None:
			return None
		G_reg = G + self.lambda_reg * np.eye(self.k)
		sign, logdet_val = np.linalg.slogdet(G_reg)
		if sign < 0:
			logdet_val = -np.inf
		self.logdet_hist.append(float(logdet_val))
		if len(self.logdet_hist) > 2000:
			self.logdet_hist.pop(0)
		return float(logdet_val)

	def logdet_threshold(self, k=6.0, floor=-50.0):
		if len(self.logdet_hist) < 50:
			return floor
		arr = np.array(self.logdet_hist[-300:])
		mu = np.mean(arr)
		sigma = np.std(arr) + 1e-15
		return float(mu - k * sigma)


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


# ==== Stage 5-7: Control Suite ====
class ShuffledSymbolSource(SymbolSource):
	"""
	Control 1 — Temporal shuffle control.

	Same symbols as the original script, but in randomized order.
	This breaks temporal/causal coherence while preserving symbol distribution.

	Expected: Real ordered stream shows more structured excursions than shuffled.
	If excursions collapse under shuffle, that is a real result.
	"""

	def __init__(self, script="^^^&&&#^&##", seed=999):
		super().__init__(script)
		# Pre-shuffle the script
		rng = np.random.default_rng(seed)
		chars = list(script)
		rng.shuffle(chars)
		self.shuffled_script = "".join(chars)
		self.ptr = 0

	def next_symbol(self, t, step_idx):
		if not self.shuffled_script:
			return "."
		sym = self.shuffled_script[self.ptr]
		self.ptr = (self.ptr + 1) % len(self.shuffled_script)
		return sym


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
	use_efim=False,  # Use EFIM-based logdet observable (paper architecture)
	adapter_k=4,  # Dimension of adapter subspace φ
	lambda_reg=1e-6,  # Regularization for logdet computation
	control_mode="real",  # Control: real|shuffled|random_probe|scrambled
	return_diagnostics=False,  # Return logdet trace + metrics alongside events
):
	rng = np.random.default_rng(seed)
	rho = np.array([[0.9, 0.0], [0.0, 0.1]], dtype=complex)

	# Diagnostic trace collection
	logdet_trace = [] if return_diagnostics else None

	# Control 1: Temporal shuffle — replace symbol source with shuffled version
	if control_mode == "shuffled":
		original_script = symbol_source.script if hasattr(symbol_source, "script") else "^^^&&&#^&##"
		symbol_source = ShuffledSymbolSource(original_script, seed=seed + 7)

	# Choose geometry meter based on mode
	if use_efim:
		# EFIM target: next-symbol prediction (4 classes: ^, &, #, .)
		# Non-circular: symbol sequence is predetermined, not derived from detector
		n_classes = 4
		# Control 2: Random probe — use random adapter seed (breaks semantic anchoring)
		adapter_seed = seed + 13 if control_mode == "random_probe" else seed
		adapter = FeatureWindowAdapter(hidden_dim=adapter_k * 2, n_classes=n_classes, seed=adapter_seed)
		geom = PassiveEFIMProbe(adapter, win=geom_win, lambda_reg=lambda_reg)
	else:
		adapter = None
		geom = GeomMeter(win=geom_win)

	# Control 3: Target scramble — RNG for randomizing y_t labels
	scramble_rng = np.random.default_rng(seed + 31) if control_mode == "scrambled" else None

	# Symbol-to-class mapping for next-symbol target
	sym_to_class = {'^': 0, '&': 1, '#': 2, '.': 3}

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

		# Compute geometry observable based on mode
		if use_efim:
			# Paper-faithful EFIM: passive readout over frozen host features
			# Target: next-symbol prediction (non-circular, independent of detector)

			# 1. Determine y_t: next symbol class (direct script lookup, no peek)
			script = getattr(symbol_source, 'shuffled_script',
				getattr(symbol_source, 'script', '.'))
			if script:
				next_sym = script[(step + 1) % len(script)]
			else:
				next_sym = '.'
			y_t = sym_to_class.get(next_sym, 3)

			# Control 3: Target scramble — randomize y_t label
			if scramble_rng is not None:
				y_t = int(scramble_rng.integers(0, 4))

			# 2. Extract features from frozen host observables
			x_t = adapter.extract_features(C, E, rnorm, purity, S, sym)

			# 3. Compute gradient of log p(y_t | x_t; φ) w.r.t. adapter φ
			grad = geom.compute_gradient(x_t, y_t)
			geom.push_gradient(grad)

			# 4. Compute logdet(G̃ + λI)
			detg = geom.logdet()
			det_thr = geom.logdet_threshold(k=det_k)  # Returns None during warmup
		else:
			# Legacy mode: 2D covariance
			geom.push(C, E)
			detg = geom.detg()
			det_thr = geom.detg_threshold(k=det_k, floor=det_floor)

		# Record logdet trace for diagnostics
		if logdet_trace is not None and detg is not None:
			logdet_trace.append(float(detg))

		reso.push(E)
		pk = reso.peaks(dt, k=3, bands=target_bands, tol=band_tol)

		flags = []
		# Detection logic differs by mode:
		# - Legacy: |det(g)| < threshold (near-zero covariance determinant)
		# - EFIM: logdet < threshold (Z-score below running mean, None during warmup)
		if detg is not None and det_thr is not None:
			if use_efim:
				# EFIM mode: flag when logdet drops below calibrated threshold
				pqn_condition = detg < det_thr
			else:
				# Legacy mode: flag when |det(g)| near zero
				pqn_condition = abs(detg) < det_thr

			if pqn_condition:
				zcount += 1
			else:
				zcount = 0
		else:
			zcount = 0

		if zcount >= consec:
			# Honest naming: EFIM mode is a regime-separation detector,
			# not yet a validated PQN detector. Use EFIM_ANOMALY for EFIM,
			# keep PQN_DETECTED for legacy mode (historical compatibility).
			flags.append("EFIM_ANOMALY" if use_efim else "PQN_DETECTED")
			zcount = 0

		if pk and pk["hits"]:
			flags.append("RESONANCE_HIT")

		# Paradox detection
		paradox_condition = False
		if detg is not None and det_thr is not None:
			if use_efim:
				paradox_condition = detg < det_thr
			else:
				paradox_condition = abs(detg) < det_thr

		if paradox_condition and purity < paradox_purity and S > paradox_entropy:
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

	if return_diagnostics:
		return {"events": events, "logdet_trace": logdet_trace}
	return events


def _count_detection_events(events):
	"""Count detection events (EFIM_ANOMALY or PQN_DETECTED, depending on mode)."""
	return sum(1 for e in events
	           if "EFIM_ANOMALY" in e["flags"] or "PQN_DETECTED" in e["flags"])


def ensemble_compare(sources, seeds=(0, 1, 2), **runner_kwargs):
	report = []
	for name, src in sources.items():
		for sd in seeds:
			evts = run_cmst(src, seed=sd, **runner_kwargs)
			pqn = _count_detection_events(evts)
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


def control_compare(script="^^^&&&#^&##", seeds=(0, 1, 2), **runner_kwargs):
	"""
	Run all 4 control modes and compare results.

	Controls (from 0102_TECHNICAL_EXTRACTIONS):
	- real: Original ordered symbol stream
	- shuffled: Randomized symbol order (breaks temporal coherence)
	- random_probe: Random adapter weights (breaks semantic anchoring)
	- scrambled: Randomized y_t targets (breaks target signal)

	Expected pattern for valid signal:
	- real: Structured excursions
	- shuffled: Reduced coherence
	- random_probe: Weaker or noisier excursions
	- scrambled: Degraded signal
	"""
	modes = ["real", "shuffled", "random_probe", "scrambled"]
	report = []

	for mode in modes:
		mode_results = []
		for sd in seeds:
			src = SymbolSource(script)
			evts = run_cmst(src, seed=sd, control_mode=mode, **runner_kwargs)
			pqn = _count_detection_events(evts)
			res = sum(1 for e in evts if "RESONANCE_HIT" in e["flags"])
			par = sum(1 for e in evts if "PARADOX_RISK" in e["flags"])
			mode_results.append({"seed": sd, "pqn": pqn, "res": res, "par": par})

		avg_pqn = np.mean([r["pqn"] for r in mode_results])
		avg_res = np.mean([r["res"] for r in mode_results])
		report.append({
			"control_mode": mode,
			"avg_pqn_events": float(avg_pqn),
			"avg_res_hits": float(avg_res),
			"per_seed": mode_results,
		})

	return report


def threshold_sweep(script="^^^&&&#^&##", k_values=(2, 3, 4, 6),
                     seeds=(0, 1, 2, 3, 4), steps=1000, **runner_kwargs):
	"""
	012's recommended clean calibration experiment.

	Sweep threshold k across all control modes and seeds.
	No noise. Collect richer metrics than event count:
	- mean_logdet: Average logdet(G̃ + λI) over run
	- std_logdet: Standard deviation of logdet trace
	- event_rate: PQN events / total steps
	- dwell_below: Fraction of steps where logdet < threshold
	- logdet_final_50: Mean of last 50 logdet values (steady state)

	Returns structured report for analysis.
	"""
	modes = ["real", "shuffled", "random_probe", "scrambled"]
	report = []

	# Force no noise, EFIM mode, diagnostics on
	runner_kwargs["use_efim"] = True
	runner_kwargs["noise_H"] = 0.0
	runner_kwargs["noise_L"] = 0.0
	runner_kwargs["return_diagnostics"] = True
	runner_kwargs["steps"] = steps

	for k_val in k_values:
		for mode in modes:
			mode_seeds = []
			for sd in seeds:
				src = SymbolSource(script)
				result = run_cmst(src, seed=sd, control_mode=mode,
				                  det_k=k_val, **runner_kwargs)

				evts = result["events"]
				trace = result["logdet_trace"]

				pqn = _count_detection_events(evts)
				res = sum(1 for e in evts if "RESONANCE_HIT" in e["flags"])

				# Compute richer metrics from logdet trace
				if trace and len(trace) > 0:
					arr = np.array(trace)
					mean_ld = float(np.mean(arr))
					std_ld = float(np.std(arr))
					final_50 = float(np.mean(arr[-50:])) if len(arr) >= 50 else mean_ld

					# Dwell below threshold: fraction of post-warmup steps
					# where logdet was below the running Z-score threshold
					warmup = 50
					if len(arr) > warmup:
						post_warmup = arr[warmup:]
						mu_run = np.mean(post_warmup)
						sig_run = np.std(post_warmup) + 1e-15
						thr = mu_run - k_val * sig_run
						dwell = float(np.mean(post_warmup < thr))
					else:
						dwell = 0.0
				else:
					mean_ld = std_ld = final_50 = dwell = 0.0

				# Threshold-independent: fraction in lower quantiles
				if trace and len(trace) > 0:
					q10 = float(np.percentile(arr, 10))
					q25 = float(np.percentile(arr, 25))
					frac_below_q10 = 0.0  # baseline reference (always ~10%)
					frac_below_q25 = 0.0
				else:
					q10 = q25 = frac_below_q10 = frac_below_q25 = 0.0

				mode_seeds.append({
					"seed": sd,
					"pqn": pqn,
					"res": res,
					"mean_logdet": round(mean_ld, 2),
					"std_logdet": round(std_ld, 4),
					"logdet_final_50": round(final_50, 2),
					"dwell_below_thr": round(dwell, 4),
					"event_rate": round(pqn / max(steps, 1), 6),
					"q10_logdet": round(q10, 2),
					"q25_logdet": round(q25, 2),
				})

			# Aggregate across seeds
			mean_logdets = [r["mean_logdet"] for r in mode_seeds]
			agg = {
				"k": k_val,
				"control_mode": mode,
				"mean_logdet": round(float(np.mean(mean_logdets)), 2),
				"std_logdet_across_seeds": round(float(np.std(mean_logdets)), 4),
				"mean_dwell": round(float(np.mean([r["dwell_below_thr"] for r in mode_seeds])), 4),
				"total_pqn": sum(r["pqn"] for r in mode_seeds),
				"mean_q10": round(float(np.mean([r["q10_logdet"] for r in mode_seeds])), 2),
				"mean_q25": round(float(np.mean([r["q25_logdet"] for r in mode_seeds])), 2),
				"per_seed": mode_seeds,
			}
			report.append(agg)

	# Compute effect sizes: real vs each control, per k value
	effect_sizes = []
	for k_val in k_values:
		k_rows = [r for r in report if r["k"] == k_val]
		real_row = next((r for r in k_rows if r["control_mode"] == "real"), None)
		if real_row is None:
			continue
		real_means = [s["mean_logdet"] for s in real_row["per_seed"]]
		for ctrl in ["shuffled", "random_probe", "scrambled"]:
			ctrl_row = next((r for r in k_rows if r["control_mode"] == ctrl), None)
			if ctrl_row is None:
				continue
			ctrl_means = [s["mean_logdet"] for s in ctrl_row["per_seed"]]
			# Cohen's d effect size
			pooled_std = np.sqrt((np.var(real_means) + np.var(ctrl_means)) / 2) + 1e-15
			d = (np.mean(real_means) - np.mean(ctrl_means)) / pooled_std
			effect_sizes.append({
				"k": k_val,
				"comparison": f"real_vs_{ctrl}",
				"cohens_d": round(float(d), 3),
				"real_mean": round(float(np.mean(real_means)), 2),
				"ctrl_mean": round(float(np.mean(ctrl_means)), 2),
				"separation": round(float(np.mean(real_means) - np.mean(ctrl_means)), 2),
			})

	return {"sweep": report, "effect_sizes": effect_sizes}


def paired_seed_analysis(script="^^^&&&#^&##", n_seeds=20, steps=500,
                          n_bootstrap=1000, **runner_kwargs):
	"""
	012's recommended paired-seed validation (post-threshold-sweep).

	For each seed, runs all 4 control modes and computes PAIRED differences:
	  delta_i = mean_logdet(real, seed_i) - mean_logdet(control, seed_i)

	Reports:
	- Paired differences per seed
	- Mean paired difference + bootstrap 95% CI
	- Rank ordering stability (fraction of seeds where real < control)
	- Sign consistency (fraction of seeds where delta < 0)

	Key question: for the SAME seed, does real systematically produce
	more negative logdet than shuffled?
	"""
	modes = ["real", "shuffled", "random_probe", "scrambled"]
	seeds = list(range(n_seeds))

	# Force clean conditions
	runner_kwargs["use_efim"] = True
	runner_kwargs["noise_H"] = 0.0
	runner_kwargs["noise_L"] = 0.0
	runner_kwargs["return_diagnostics"] = True
	runner_kwargs["steps"] = steps

	# Collect per-seed mean_logdet for each mode
	seed_data = {mode: [] for mode in modes}

	for sd in seeds:
		for mode in modes:
			src = SymbolSource(script)
			result = run_cmst(src, seed=sd, control_mode=mode,
			                  det_k=6.0, **runner_kwargs)
			trace = result["logdet_trace"]
			if trace and len(trace) > 0:
				mean_ld = float(np.mean(trace))
			else:
				mean_ld = 0.0
			seed_data[mode].append(mean_ld)

	rng_boot = np.random.default_rng(42)

	# Compute paired analyses
	real_vals = np.array(seed_data["real"])
	comparisons = {}

	for ctrl in ["shuffled", "random_probe", "scrambled"]:
		ctrl_vals = np.array(seed_data[ctrl])

		# Paired differences: delta_i = real_i - ctrl_i
		deltas = real_vals - ctrl_vals

		mean_delta = float(np.mean(deltas))
		std_delta = float(np.std(deltas, ddof=1))

		# Sign consistency: fraction where real < ctrl (delta < 0)
		sign_frac = float(np.mean(deltas < 0))

		# Bootstrap 95% CI on mean paired difference
		boot_means = []
		for _ in range(n_bootstrap):
			idx = rng_boot.integers(0, n_seeds, size=n_seeds)
			boot_means.append(float(np.mean(deltas[idx])))
		boot_means = sorted(boot_means)
		ci_lo = boot_means[int(0.025 * n_bootstrap)]
		ci_hi = boot_means[int(0.975 * n_bootstrap)]

		# Paired t-test statistic (for reference, not p-value)
		t_stat = mean_delta / (std_delta / np.sqrt(n_seeds)) if std_delta > 0 else 0.0

		comparisons[f"real_vs_{ctrl}"] = {
			"mean_paired_diff": round(mean_delta, 2),
			"std_paired_diff": round(std_delta, 2),
			"sign_consistency": round(sign_frac, 3),
			"bootstrap_95_ci": [round(ci_lo, 2), round(ci_hi, 2)],
			"t_statistic": round(float(t_stat), 3),
			"n_seeds": n_seeds,
			"per_seed_deltas": [round(float(d), 2) for d in deltas],
		}

	# Rank ordering stability: for each seed, check full ordering
	# real < random_probe < shuffled < scrambled?
	full_order_count = 0
	partial_order_count = 0  # at least real < shuffled
	for i in range(n_seeds):
		r = seed_data["real"][i]
		rp = seed_data["random_probe"][i]
		sh = seed_data["shuffled"][i]
		sc = seed_data["scrambled"][i]
		if r < rp < sh < sc:
			full_order_count += 1
		if r < sh:
			partial_order_count += 1

	rank_stability = {
		"full_ordering_frac": round(full_order_count / n_seeds, 3),
		"real_lt_shuffled_frac": round(partial_order_count / n_seeds, 3),
	}

	return {
		"n_seeds": n_seeds,
		"steps": steps,
		"mode_means": {m: round(float(np.mean(v)), 2) for m, v in seed_data.items()},
		"mode_stds": {m: round(float(np.std(v)), 2) for m, v in seed_data.items()},
		"comparisons": comparisons,
		"rank_stability": rank_stability,
		"per_seed_values": {m: [round(x, 2) for x in v] for m, v in seed_data.items()},
	}


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
	ap.add_argument("--mode", type=str,
		choices=["single", "ensemble", "control_compare", "threshold_sweep",
		         "paired_seed"], default="single")
	ap.add_argument("--n_seeds", type=int, default=20,
		help="Number of seeds for paired_seed analysis (default: 20)")
	ap.add_argument("--guardrail_on", action="store_true")
	ap.add_argument("--guardrail_window", type=int, default=64)
	ap.add_argument("--paradox_purity", type=float, default=0.8)
	ap.add_argument("--paradox_entropy", type=float, default=0.3)
	# EFIM architecture flags
	ap.add_argument("--use_efim", action="store_true",
		help="Use EFIM-based logdet(G+λI) observable instead of toy 2D covariance")
	ap.add_argument("--adapter_k", type=int, default=4,
		help="Dimension of adapter hidden layer (default: 4, hidden=8)")
	ap.add_argument("--lambda_reg", type=float, default=1e-6,
		help="Regularization constant for logdet computation (default: 1e-6)")
	# Control suite flags (Stages 5-7)
	ap.add_argument("--control_mode", type=str,
		choices=["real", "shuffled", "random_probe", "scrambled"], default="real",
		help="Control mode for validation: real|shuffled|random_probe|scrambled")
	args = ap.parse_args()

	# Common kwargs for all modes
	common_kwargs = dict(
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
		guardrail_on=args.guardrail_on,
		guardrail_window=args.guardrail_window,
		paradox_purity=args.paradox_purity,
		paradox_entropy=args.paradox_entropy,
		use_efim=args.use_efim,
		adapter_k=args.adapter_k,
		lambda_reg=args.lambda_reg,
	)

	if args.mode == "single":
		src = SymbolSource(args.script)
		evts = run_cmst(
			symbol_source=src,
			seed=args.seed,
			control_mode=args.control_mode,
			**common_kwargs,
		)
		mode_label = "EFIM" if args.use_efim else "legacy"
		print(json.dumps({
			"mode": mode_label,
			"control": args.control_mode,
			"events": evts[:1000],
			"count": len(evts),
		}, indent=2))
	elif args.mode == "control_compare":
		rpt = control_compare(
			script=args.script,
			seeds=(0, 1, 2),
			**common_kwargs,
		)
		mode_label = "EFIM" if args.use_efim else "legacy"
		print(json.dumps({"mode": mode_label, "control_report": rpt}, indent=2))
	elif args.mode == "threshold_sweep":
		result = threshold_sweep(
			script=args.script,
			k_values=(2, 3, 4, 6),
			seeds=(0, 1, 2, 3, 4),
			steps=args.steps,
			base_dt=args.dt,
			jitter=args.jitter,
			consec=args.consec,
			geom_win=args.geom_win,
			res_win=args.res_win,
			adapter_k=args.adapter_k,
			lambda_reg=args.lambda_reg,
			guardrail_on=args.guardrail_on,
			guardrail_window=args.guardrail_window,
			paradox_purity=args.paradox_purity,
			paradox_entropy=args.paradox_entropy,
		)
		rpt = result["sweep"]
		efx = result["effect_sizes"]

		# Summary table
		print("=" * 90)
		print("THRESHOLD SWEEP: k x control_mode x 5 seeds (EFIM, no noise)")
		print("=" * 90)
		print(f"{'k':>4} {'mode':<14} {'mean_logdet':>12} {'std_seeds':>10} "
		      f"{'dwell':>8} {'q10':>10} {'q25':>10} {'pqn':>5}")
		print("-" * 90)
		for row in rpt:
			print(f"{row['k']:>4} {row['control_mode']:<14} "
			      f"{row['mean_logdet']:>12.2f} "
			      f"{row['std_logdet_across_seeds']:>10.4f} "
			      f"{row['mean_dwell']:>8.4f} "
			      f"{row['mean_q10']:>10.2f} "
			      f"{row['mean_q25']:>10.2f} "
			      f"{row['total_pqn']:>5}")
		print("-" * 90)

		# Effect sizes
		print("\nEFFECT SIZES (Cohen's d: real vs control)")
		print("-" * 70)
		print(f"{'k':>4} {'comparison':<25} {'d':>8} {'separation':>12} "
		      f"{'real':>10} {'ctrl':>10}")
		print("-" * 70)
		for e in efx:
			print(f"{e['k']:>4} {e['comparison']:<25} {e['cohens_d']:>8.3f} "
			      f"{e['separation']:>12.2f} "
			      f"{e['real_mean']:>10.2f} {e['ctrl_mean']:>10.2f}")
		print("-" * 70)

		# Full JSON for archival
		print("\nFull report (JSON):")
		print(json.dumps(result, indent=2))
	elif args.mode == "paired_seed":
		result = paired_seed_analysis(
			script=args.script,
			n_seeds=args.n_seeds,
			steps=args.steps,
			base_dt=args.dt,
			jitter=args.jitter,
			consec=args.consec,
			geom_win=args.geom_win,
			res_win=args.res_win,
			adapter_k=args.adapter_k,
			lambda_reg=args.lambda_reg,
			guardrail_on=args.guardrail_on,
			guardrail_window=args.guardrail_window,
			paradox_purity=args.paradox_purity,
			paradox_entropy=args.paradox_entropy,
		)

		# Summary header
		print("=" * 80)
		print(f"PAIRED SEED ANALYSIS: {result['n_seeds']} seeds, "
		      f"{result['steps']} steps (EFIM, no noise)")
		print("=" * 80)

		# Mode means
		print("\nMode means (logdet):")
		for m, v in result["mode_means"].items():
			std = result["mode_stds"][m]
			print(f"  {m:<14} {v:>10.2f}  (std={std:.2f})")

		# Paired comparisons
		print("\nPaired comparisons (real - control):")
		print("-" * 80)
		print(f"{'comparison':<25} {'mean_diff':>10} {'std':>8} {'sign%':>7} "
		      f"{'95% CI':>20} {'t':>8}")
		print("-" * 80)
		for name, c in result["comparisons"].items():
			ci = c["bootstrap_95_ci"]
			print(f"{name:<25} {c['mean_paired_diff']:>10.2f} "
			      f"{c['std_paired_diff']:>8.2f} "
			      f"{c['sign_consistency']*100:>6.1f}% "
			      f"[{ci[0]:>8.2f}, {ci[1]:>8.2f}] "
			      f"{c['t_statistic']:>8.3f}")
		print("-" * 80)

		# Rank stability
		rs = result["rank_stability"]
		print(f"\nRank ordering stability:")
		print(f"  real < shuffled:                  {rs['real_lt_shuffled_frac']*100:.1f}%")
		print(f"  full order (r<rp<sh<sc):          {rs['full_ordering_frac']*100:.1f}%")

		# Full JSON
		print("\nFull report (JSON):")
		print(json.dumps(result, indent=2))
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
			control_mode=args.control_mode,
			**common_kwargs,
		)
		mode_label = "EFIM" if args.use_efim else "legacy"
		print(json.dumps({
			"mode": mode_label,
			"control": args.control_mode,
			"ensemble_report": rpt,
		}, indent=2))


if __name__ == "__main__":
	main()


