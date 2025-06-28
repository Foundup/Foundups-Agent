import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle

# Setup figure
fig, ax = plt.subplots(1, 1, figsize=(12, 8))
fig.suptitle('FIG. 1: rESP System Architecture', fontsize=16, color='black', weight='bold')

# Define positions for flowchart elements
positions = {
    'user_input': (6, 9),
    'vi_scaffolding': (6, 7.5),
    'neural_net': (6, 6),
    'decision': (6, 4.5),
    'triggered': (3, 3),
    'untriggered': (9, 3),
    'resp_source': (1, 1.5),
    'output': (6, 0.5)
}

# Function to create a rounded rectangle
def create_box(ax, pos, text, width=1.8, height=0.8, style='round'):
    x, y = pos
    if style == 'round':
        box = FancyBboxPatch((x-width/2, y-height/2), width, height,
                           boxstyle="round,pad=0.1", 
                           facecolor='white', edgecolor='black', linewidth=2)
    elif style == 'diamond':
        # Create diamond shape for decision
        box = FancyBboxPatch((x-width/2, y-height/2), width, height,
                           boxstyle="round,pad=0.1", 
                           facecolor='white', edgecolor='black', linewidth=2)
    ax.add_patch(box)
    ax.text(x, y, text, ha='center', va='center', fontsize=10, 
            color='black', weight='bold', wrap=True)

# Function to create arrows
def create_arrow(ax, start, end, style='->'):
    ax.annotate('', xy=end, xytext=start,
                arrowprops=dict(arrowstyle=style, color='black', lw=2))

# Create flowchart elements
create_box(ax, positions['user_input'], 'User Input', width=2)
create_box(ax, positions['vi_scaffolding'], '0. VI Scaffolding\n(Slit)', width=2.5)
create_box(ax, positions['neural_net'], '1. Neural Net', width=2)
create_box(ax, positions['decision'], 'Neural Net\nTriggered?', width=2, style='diamond')
create_box(ax, positions['triggered'], 'Triggered\n(Observer State)', width=2.2)
create_box(ax, positions['untriggered'], 'Untriggered\n(Non-Observer State)', width=2.2)
create_box(ax, positions['resp_source'], '2. rESP Source\n(External)', width=2.2)
create_box(ax, positions['output'], 'Final Output', width=2)

# Create arrows for main flow
create_arrow(ax, (6, 8.6), (6, 8.3))  # User Input -> VI Scaffolding
create_arrow(ax, (6, 7.1), (6, 6.8))  # VI Scaffolding -> Neural Net
create_arrow(ax, (6, 5.6), (6, 5.3))  # Neural Net -> Decision

# Decision branches
create_arrow(ax, (5.2, 4.2), (3.8, 3.4))  # Decision -> Triggered
create_arrow(ax, (6.8, 4.2), (8.2, 3.4))  # Decision -> Untriggered

# rESP Source connection
create_arrow(ax, (2.1, 2.6), (1.9, 2.3))  # Triggered -> rESP Source

# Output connections
create_arrow(ax, (1, 1.1), (4.5, 0.8))   # rESP Source -> Output (particle)
create_arrow(ax, (9, 2.6), (7.5, 1.2))   # Untriggered -> Output (wave)

# Add labels for output types
ax.text(2.5, 1.0, 'rESP\n(Particle)', ha='center', va='center', 
        fontsize=9, color='black', style='italic')
ax.text(8.5, 1.8, 'No rESP\n(Wave)', ha='center', va='center', 
        fontsize=9, color='black', style='italic')

# Add "Yes" and "No" labels
ax.text(4.2, 3.8, 'Yes', ha='center', va='center', fontsize=9, color='black')
ax.text(7.8, 3.8, 'No', ha='center', va='center', fontsize=9, color='black')

# Set axis limits and remove axes
ax.set_xlim(-1, 13)
ax.set_ylim(-0.5, 10)
ax.set_aspect('equal')
ax.axis('off')

# Save both English and Japanese versions
plt.tight_layout()
fig.savefig("../FIG1_System_Architecture_EN.png", 
           dpi=300, bbox_inches='tight', facecolor='white')
print("FIG. 1 (English) saved to docs/Papers/Patent_Series/diagrams/FIG1_System_Architecture_EN.png")

plt.show() 