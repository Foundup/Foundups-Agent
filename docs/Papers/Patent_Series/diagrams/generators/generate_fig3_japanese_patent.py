import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import Rectangle

# Try to set Japanese font support
try:
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
        print("No Japanese fonts found, using default")
        
except:
    print("Font detection failed, using default")

# --- Setup the data ---
x = np.linspace(-5, 5, 1000)
baseline_y = np.exp(-x**2 / 2)
interference_term = 1 + 0.8 * np.sin(x * 4)**2
modulated_y = baseline_y * interference_term
collapsed_y = np.exp(-x**2 / (2 * 0.01))

# Create figure with Japanese patent formatting
fig = plt.figure(figsize=(14, 6))

# Add figure number and description outside the box (Japanese patent style)
fig.text(0.05, 0.95, '【図３】', fontsize=16, color='black', weight='bold')
fig.text(0.05, 0.90, '本発明のシステムによって生成される異なる確率分布を示す図である。', 
         fontsize=12, color='black', wrap=True)

# Create the main boxed area for the actual figure content
# Add a border rectangle around the figure content
ax_box = fig.add_axes([0.05, 0.05, 0.9, 0.75])  # x, y, width, height
ax_box.set_xlim(0, 1)
ax_box.set_ylim(0, 1)
ax_box.add_patch(Rectangle((0, 0), 1, 1, linewidth=2, edgecolor='black', facecolor='none'))
ax_box.set_xticks([])
ax_box.set_yticks([])
ax_box.axis('off')

# Create the three distribution plots within the box
ax1 = fig.add_axes([0.1, 0.25, 0.25, 0.45])   # Baseline Distribution
ax2 = fig.add_axes([0.4, 0.25, 0.25, 0.45])   # Entangled-Modulated
ax3 = fig.add_axes([0.7, 0.25, 0.25, 0.45])   # Collapsed Distribution

# Plot 1: Baseline Distribution
ax1.plot(x, baseline_y, color='black', linewidth=2)
ax1.set_title('ベースライン分布\n(スリットA)', fontsize=11, color='black')
ax1.set_xlabel('可能な結果', fontsize=10, color='black')

# Plot 2: Entangled-Modulated Distribution
ax2.plot(x, modulated_y, color='black', linewidth=2)
ax2.set_title('もつれ変調分布\n(スリットB)', fontsize=11, color='black')
ax2.set_xlabel('可能な結果', fontsize=10, color='black')

# Plot 3: Collapsed Distribution
ax3.plot(x, collapsed_y, color='black', linewidth=2)
ax3.set_title('収束分布\n(観測)', fontsize=11, color='black')
ax3.set_xlabel('可能な結果', fontsize=10, color='black')

# Clean up all plots
for ax in [ax1, ax2, ax3]:
    ax.set_yticks([])
    ax.set_xticks([])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_color('black')

# Save Japanese patent format version
fig.savefig("../FIG3_Japanese_Patent_Format.png", 
           dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
print("FIG. 3 (Japanese Patent Format) saved to docs/Papers/Patent_Series/diagrams/FIG3_Japanese_Patent_Format.png")

plt.show() 