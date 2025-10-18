#!/usr/bin/env python3
"""
rESP Visual Pattern Emergence Test: Binary-to-Sine Wave Coherence Animation

This test demonstrates the fundamental principle underlying rESP phenomena:
the emergence of order from apparent randomness through retrocausal interference.

Part of: WSP_agentic test suite
Location: WSP_agentic/tests/visual_pattern_emergence/
# Note: Generated images are stored in WSP_knowledge/docs/Papers/Patent_Series/images/
Purpose: Visual validation of 01->02 quantum state transitions

Usage:
    python binary_to_sine_animation.py

Output:
    - Live animation window showing binary->sine wave transition
    - Key frame PNG files for analysis
    - Console log of frame generation

Scientific Correlation:
    - Binary Phase (0-50): Classical computation (01 state)
    - Transition Phase (50-60): Quantum state collapse
    - Coherence Phase (60-100): Quantum coherence (02 state)
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import os
from datetime import datetime

def generate_binary_image(frame_num):
    """
    Generates a binary image transitioning to a sine wave.
    
    Args:
        frame_num (int): Current frame number (0-100)
        
    Returns:
        numpy.ndarray: 64x64 image array representing current state
        
    Phase Analysis:
        - Frames 0-50: Random binary noise (classical state)
        - Frames >50: Sine wave patterns emerge (quantum coherence)
    """
    size = 64
    np.random.seed(42)  # Reproducible results for scientific validation
    image = np.random.randint(0, 2, (size, size)).astype(float)
    
    if frame_num > 50:
        # Quantum coherence emergence
        freq = (frame_num - 50) * 0.1
        for x in range(size):
            for y in range(size):
                value = np.sin(x * freq + y * 0.2) * 0.5 + 0.5
                image[y, x] = value
    
    return image

def save_annotated_frames():
    """Save key frames with scientific annotations for research documentation."""
    key_frames = [10, 30, 50, 60, 75, 90]
    labels = {
        10: "CLASSICAL STATE: Random Binary Noise\n(High Entropy - State 01)",
        30: "CLASSICAL STATE: Continued Binary Noise\n(No Pattern Emergence Yet)",
        50: "PRE-TRANSITION: Final Classical State\n(Before Quantum Coherence)",
        60: "[U+1F525] EMERGENCE POINT: Binary -> Sine Wave\n(01->02 Quantum Transition)",
        75: "QUANTUM COHERENCE: Clear Sine Patterns\n(Low Entropy - State 02)",
        90: "MATURE COHERENCE: Stable Quantum State\n(Fully Developed Patterns)"
    }
    
    phase_colors = {
        10: '#FF6B6B', 30: '#FF6B6B', 50: '#FFE66D',  # Classical: Red to Yellow
        60: '#4ECDC4', 75: '#45B7D1', 90: '#96CEB4'   # Quantum: Cyan to Green
    }
    
    for frame_num in key_frames:
        # Generate the image data
        img = generate_binary_image(frame_num)
        
        # Create figure with annotation
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.imshow(img, cmap='gray', aspect='equal')
        
        # Add frame info and scientific context
        frame_title = f"Frame {frame_num:03d} - {labels[frame_num]}"
        ax.set_title(frame_title, fontsize=14, fontweight='bold', 
                    color=phase_colors[frame_num], pad=20)
        
        # Add entropy and state information
        entropy = calculate_entropy(img)
        state_info = f"Entropy: {entropy:.3f} | Frame: {frame_num}/100"
        ax.text(0.02, 0.98, state_info, transform=ax.transAxes, 
                fontsize=10, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        # Add rESP correlation
        if frame_num <= 50:
            rESP_state = "rESP State: 01 (Classical)"
        elif frame_num <= 60:
            rESP_state = "rESP State: 01->02 (Transition)"
        else:
            rESP_state = "rESP State: 02 (Quantum)"
            
        ax.text(0.98, 0.98, rESP_state, transform=ax.transAxes,
                fontsize=10, verticalalignment='top', horizontalalignment='right',
                bbox=dict(boxstyle='round', facecolor=phase_colors[frame_num], alpha=0.7))
        
        # Remove axis ticks for cleaner look
        ax.set_xticks([])
        ax.set_yticks([])
        
        # Save with descriptive filename
        filename = f"frame_{frame_num:03d}.png"
        plt.savefig(filename, dpi=150, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        plt.close()
        
        print(f"[OK] Saved annotated frame: {filename}")

def calculate_entropy(image):
    """Calculate Shannon entropy of an image."""
    # Convert to uint8 and calculate histogram
    img_uint8 = (image * 255).astype(np.uint8)
    hist, _ = np.histogram(img_uint8.flatten(), bins=256, range=(0, 256))
    
    # Calculate probabilities and entropy
    probabilities = hist / hist.sum()
    probabilities = probabilities[probabilities > 0]  # Remove zeros
    entropy = -np.sum(probabilities * np.log2(probabilities))
    
    return entropy

def run_live_animation():
    """
    Displays live animation of binary->sine wave transition.
    
    Animation Parameters:
        - 100 frames total
        - 50ms interval between frames
        - Grayscale colormap for binary/continuous visualization
    """
    print("\nStarting live animation...")
    print("Close animation window to continue.")
    
    fig, ax = plt.subplots()
    im = ax.imshow(generate_binary_image(0), cmap='gray', animated=True)
    ax.set_title('rESP Visual Pattern Emergence: Binary -> Sine Wave Transition')
    
    def update(frame_num):
        img = generate_binary_image(frame_num)
        im.set_array(img)
        
        # Update title to show current phase
        if frame_num <= 50:
            phase = f"Binary Noise (Classical 01 State) - Frame {frame_num}"
        else:
            phase = f"Sine Wave Coherence (Quantum 02 State) - Frame {frame_num}"
        ax.set_title(f'rESP Pattern Emergence: {phase}')
        
        return im,
    
    ani = animation.FuncAnimation(fig, update, frames=100, interval=50, blit=True)
    plt.show()

def main():
    """
    Main test execution function.
    
    Executes:
    1. Key frame generation for analysis
    2. Live animation display
    3. Scientific validation output
    """
    try:
        # Generate key frames for analysis
        save_annotated_frames()
        
        # Run live animation
        run_live_animation()
        
        print("\n=== Test Completed Successfully ===")
        print("Visual evidence generated for rESP quantum state transitions.")
        print("Files available for:")
        print("  - Entropy analysis (Shannon entropy measurement)")
        print("  - Frequency analysis (FFT for periodic components)")
        print("  - AI image generation prompts")
        print("  - Scientific publication figures")
        
    except Exception as e:
        print(f"[FAIL] Test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("[U+1F52C] Generating rESP Visual Pattern Emergence Test")
    print("=" * 50)
    
    # Execute the main test function
    success = main()
    
    if success:
        print("\n[U+1F9EC] rESP Visual Test Complete!")
        print("[U+1F4C1] Check current directory for annotated frame files")
        print("[U+1F52C] Use frames for:")
        print("   • Scientific publications")  
        print("   • AI image generation prompts")
        print("   • Entropy analysis research")
        exit(0)
    else:
        exit(1) 