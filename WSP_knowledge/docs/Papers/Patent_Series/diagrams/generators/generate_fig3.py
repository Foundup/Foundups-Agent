import numpy as np
import matplotlib.pyplot as plt

# --- 1. Setup the data and figure ---
x = np.linspace(-5, 5, 1000)

# English Version
fig_en, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(12, 4))
fig_en.suptitle('FIG. 3: Probability Distribution States', fontsize=16, color='black')

# --- 2. Plot 1: Baseline Distribution (A simple Gaussian curve) ---
# This represents the normal, classical output (Slit A)
baseline_y = np.exp(-x**2 / 2)
ax1.plot(x, baseline_y, color='black', linewidth=2)
ax1.set_title('Baseline Distribution\n(Slit A)', fontsize=12, color='black')

# --- 3. Plot 2: Entangled-Modulated Distribution (Interference) ---
# This represents the wave-like interference pattern (Slit B)
# We achieve this by multiplying the baseline by a sine-wave-like interference term
interference_term = 1 + 0.8 * np.sin(x * 4)**2
modulated_y = baseline_y * interference_term
ax2.plot(x, modulated_y, color='black', linewidth=2)
ax2.set_title('Entangled-Modulated Distribution\n(Slit B)', fontsize=12, color='black')

# --- 4. Plot 3: Collapsed Distribution (A sharp spike) ---
# This represents the final, observed output
# We use a Gaussian with a very small standard deviation to create a spike
collapsed_y = np.exp(-x**2 / (2 * 0.01))
ax3.plot(x, collapsed_y, color='black', linewidth=2)
ax3.set_title('Collapsed Distribution\n(Observation)', fontsize=12, color='black')

# --- 5. Clean up the plots for English version ---
for ax in [ax1, ax2, ax3]:
    ax.set_yticks([])  # Remove y-axis numbers
    ax.set_xticks([])  # Remove x-axis numbers
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_color('black')
    ax.set_xlabel('Possible Outcomes', fontsize=12, color='black')

plt.tight_layout(rect=[0, 0, 1, 0.96])
fig_en.savefig("../FIG3_Probability_Distributions_EN.png", dpi=300, bbox_inches='tight', facecolor='white')
print("FIG. 3 (English) saved to ../FIG3_Probability_Distributions_EN.png")

# Japanese Version
fig_jp, (ax1_jp, ax2_jp, ax3_jp) = plt.subplots(1, 3, figsize=(12, 4))
fig_jp.suptitle('図３: 確率分布状態', fontsize=16, color='black')

# --- Japanese plots (same data) ---
ax1_jp.plot(x, baseline_y, color='black', linewidth=2)
ax1_jp.set_title('ベースライン分布\n(スリットA)', fontsize=12, color='black')

ax2_jp.plot(x, modulated_y, color='black', linewidth=2)
ax2_jp.set_title('もつれ変調分布\n(スリットB)', fontsize=12, color='black')

ax3_jp.plot(x, collapsed_y, color='black', linewidth=2)
ax3_jp.set_title('収束分布\n(観測)', fontsize=12, color='black')

# --- Clean up the plots for Japanese version ---
for ax in [ax1_jp, ax2_jp, ax3_jp]:
    ax.set_yticks([])  # Remove y-axis numbers
    ax.set_xticks([])  # Remove x-axis numbers
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_color('black')
    ax.set_xlabel('可能な結果', fontsize=12, color='black')

plt.tight_layout(rect=[0, 0, 1, 0.96])
fig_jp.savefig("../FIG3_Probability_Distributions_JP.png", dpi=300, bbox_inches='tight', facecolor='white')
print("FIG. 3 (Japanese) saved to ../FIG3_Probability_Distributions_JP.png")

plt.show() 