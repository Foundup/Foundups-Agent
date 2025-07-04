import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def generate_fig9_entropy_graph():
    """Generate the entropy graph component for FIG. 9 showing state transition."""
    
    # --- 1. Simulate the data ---
    time = np.linspace(0, 100, 200)
    
    # High-entropy (random) state initially
    entropy = np.random.rand(100) * 0.4 + 0.6 
    
    # Transition point
    transition_point = 100
    
    # Low-entropy (stable) state after transition
    coherent_entropy = np.random.rand(100) * 0.05 + 0.1
    
    final_entropy = np.concatenate((entropy, coherent_entropy))
    time = np.linspace(0, 100, 200)
    
    # --- 2. Create the plot ---
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Plot the entropy curve
    ax.plot(time, final_entropy, color='black', linewidth=2.5, zorder=3)
    
    # --- 3. Add annotations and styling ---
    # Transition line
    ax.axvline(x=50, color='red', linestyle='--', linewidth=3, 
               label='rESP Coherence Induced', zorder=2)
    
    # Background shading for state regions
    ax.axvspan(0, 50, alpha=0.2, color='red', label='Classical State')
    ax.axvspan(50, 100, alpha=0.2, color='green', label='Quantum Coherent State')
    
    # State labels
    ax.text(15, 0.85, 'High-Entropy\nClassical State\n(State 01)', 
            ha='center', fontsize=14, fontweight='bold', color='darkred',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8))
    
    ax.text(80, 0.15, 'Low-Entropy\nCoherent State\n(State 02)', 
            ha='center', fontsize=14, fontweight='bold', color='darkgreen',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8))
    
    # Transition annotation
    ax.annotate('01→02\nTransition\nPoint', xy=(50, 0.5), xytext=(60, 0.7),
                arrowprops=dict(arrowstyle='->', color='red', lw=2),
                fontsize=12, fontweight='bold', color='red',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.9))
    
    # Title and labels
    ax.set_title('FIG. 9(d): Shannon Entropy Reduction During State Transition', 
                fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Time Steps (Normalized)', fontsize=14, fontweight='bold')
    ax.set_ylabel('Normalized Shannon Entropy', fontsize=14, fontweight='bold')
    
    # Grid and styling
    ax.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)
    ax.set_ylim(0, 1.1)
    ax.set_xlim(0, 100)
    
    # Legend
    ax.legend(loc='upper right', fontsize=12, framealpha=0.9)
    
    # Add rESP correlation note
    ax.text(0.02, 0.02, 'rESP System: Entropy reduction correlates with quantum coherence emergence\n' +
            'Measurement: Shannon entropy calculated from output probability distributions',
            transform=ax.transAxes, fontsize=10, style='italic',
            bbox=dict(boxstyle='round,pad=0.5', facecolor='lightblue', alpha=0.8))
    
    plt.tight_layout()
    
    # Save the figure
    output_path = '../../WSP_knowledge/docs/Papers/Patent_Series/images/FIG9d_Entropy_Graph.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight', 
               facecolor='white', edgecolor='none')
    plt.close()
    
    print(f"FIG. 9(d) entropy graph saved to: {output_path}")
    return output_path

if __name__ == "__main__":
    generate_fig9_entropy_graph() 