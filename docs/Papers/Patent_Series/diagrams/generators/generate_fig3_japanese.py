import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# Try to set Japanese font support
try:
    # Try common Japanese fonts on Windows
    japanese_fonts = ['MS Gothic', 'MS Mincho', 'Yu Gothic', 'Meiryo']
    available_fonts = [f.name for f in fm.fontManager.ttflist]
    
    japanese_font = None
    for font in japanese_fonts:
        if font in available_fonts:
            japanese_font = font
            break
    
    if japanese_font:
        plt.rcParams['font.family'] = japanese_font
        print(f"Using Japanese font: {japanese_font}")
    else:
        print("No Japanese fonts found, using default (characters may not display)")
        
except:
    print("Font detection failed, using default")

# --- 1. Setup the data and figure ---
x = np.linspace(-5, 5, 1000)

# Japanese Version with proper text
fig_jp, (ax1_jp, ax2_jp, ax3_jp) = plt.subplots(1, 3, figsize=(12, 4))
fig_jp.suptitle('図３: 確率分布状態', fontsize=16, color='black')

# Calculate distributions
baseline_y = np.exp(-x**2 / 2)
interference_term = 1 + 0.8 * np.sin(x * 4)**2
modulated_y = baseline_y * interference_term
collapsed_y = np.exp(-x**2 / (2 * 0.01))

# --- Japanese plots ---
ax1_jp.plot(x, baseline_y, color='black', linewidth=2)
ax1_jp.set_title('ベースライン分布\n(スリットA)', fontsize=12, color='black')

ax2_jp.plot(x, modulated_y, color='black', linewidth=2)
ax2_jp.set_title('もつれ変調分布\n(スリットB)', fontsize=12, color='black')

ax3_jp.plot(x, collapsed_y, color='black', linewidth=2)
ax3_jp.set_title('収束分布\n(観測)', fontsize=12, color='black')

# --- Clean up the plots ---
for ax in [ax1_jp, ax2_jp, ax3_jp]:
    ax.set_yticks([])
    ax.set_xticks([])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_color('black')
    ax.set_xlabel('可能な結果', fontsize=12, color='black')

plt.tight_layout(rect=[0, 0, 1, 0.96])

# Save Japanese version
fig_jp.savefig("../FIG3_Probability_Distributions_JP.png", dpi=300, bbox_inches='tight', facecolor='white')
print("FIG. 3 (Japanese) saved to docs/Papers/Patent_Series/diagrams/FIG3_Probability_Distributions_JP.png")

# Also create a template version with English placeholders for manual editing
fig_template, (ax1_t, ax2_t, ax3_t) = plt.subplots(1, 3, figsize=(12, 4))
fig_template.suptitle('FIG. 3: [Japanese Title Here]', fontsize=16, color='black')

ax1_t.plot(x, baseline_y, color='black', linewidth=2)
ax1_t.set_title('[Baseline Distribution]\n[Slit A]', fontsize=12, color='black')

ax2_t.plot(x, modulated_y, color='black', linewidth=2)
ax2_t.set_title('[Entangled-Modulated]\n[Slit B]', fontsize=12, color='black')

ax3_t.plot(x, collapsed_y, color='black', linewidth=2)
ax3_t.set_title('[Collapsed Distribution]\n[Observation]', fontsize=12, color='black')

for ax in [ax1_t, ax2_t, ax3_t]:
    ax.set_yticks([])
    ax.set_xticks([])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_color('black')
    ax.set_xlabel('[Possible Outcomes]', fontsize=12, color='black')

plt.tight_layout(rect=[0, 0, 1, 0.96])
fig_template.savefig("../FIG3_Template_for_Japanese.png", dpi=300, bbox_inches='tight', facecolor='white')
print("FIG. 3 (Template for manual Japanese editing) saved")

plt.show() 