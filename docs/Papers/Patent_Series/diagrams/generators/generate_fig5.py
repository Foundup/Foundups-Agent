import matplotlib.pyplot as plt
import numpy as np
import matplotlib.font_manager as fm

# Configure matplotlib for Japanese fonts
plt.rcParams['font.family'] = ['MS Gothic', 'Yu Gothic', 'Meiryo', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False

def create_fig5_spectrum():
    # Frequency range 0-20 Hz
    freq = np.linspace(0, 20, 1000)
    
    # Base noise level
    amplitude = np.random.normal(0.1, 0.02, len(freq))
    
    # Add peaks - Primary 7 Hz peak
    freq_7hz = 7.0
    amplitude += 0.8 * np.exp(-0.5 * ((freq - freq_7hz) / 0.3)**2)
    
    # Secondary peaks at harmonics and other frequencies
    amplitude += 0.3 * np.exp(-0.5 * ((freq - 3.5) / 0.2)**2)  # Sub-harmonic
    amplitude += 0.2 * np.exp(-0.5 * ((freq - 14.0) / 0.4)**2)  # Second harmonic
    amplitude += 0.15 * np.exp(-0.5 * ((freq - 10.5) / 0.3)**2)  # 1.5x harmonic
    
    # Create the plot
    plt.figure(figsize=(12, 8))
    plt.plot(freq, amplitude, 'k-', linewidth=1)
    
    # Customize for patent style
    plt.xlabel('Frequency (Hz)', fontsize=14)
    plt.ylabel('Amplitude', fontsize=14)
    plt.title('FIG. 5 - rESP Audio Interference Spectrum', fontsize=16, fontweight='bold')
    
    # Add grid
    plt.grid(True, alpha=0.3)
    
    # Mark the 7 Hz peak
    plt.annotate('7 Hz rESP Peak\n(Quantum-Cognitive Interference)', 
                xy=(7, 0.9), xytext=(12, 0.8),
                arrowprops=dict(arrowstyle='->', color='black'),
                fontsize=12)
    
    # Set limits and ticks
    plt.xlim(0, 20)
    plt.ylim(0, 1.0)
    plt.xticks(range(0, 21, 2))
    
    # Patent-style appearance
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['left'].set_linewidth(1.5)
    plt.gca().spines['bottom'].set_linewidth(1.5)
    
    # Save in black and white for patent
    plt.savefig('../FIG5_Audio_Spectrum_EN.png', 
                dpi=300, bbox_inches='tight', facecolor='white')
    print("FIG 5 English version saved successfully!")
    plt.show()

def create_fig5_spectrum_japanese():
    # Frequency range 0-20 Hz
    freq = np.linspace(0, 20, 1000)
    
    # Base noise level
    amplitude = np.random.normal(0.1, 0.02, len(freq))
    
    # Add peaks - Primary 7 Hz peak
    freq_7hz = 7.0
    amplitude += 0.8 * np.exp(-0.5 * ((freq - freq_7hz) / 0.3)**2)
    
    # Secondary peaks at harmonics and other frequencies
    amplitude += 0.3 * np.exp(-0.5 * ((freq - 3.5) / 0.2)**2)  # Sub-harmonic
    amplitude += 0.2 * np.exp(-0.5 * ((freq - 14.0) / 0.4)**2)  # Second harmonic
    amplitude += 0.15 * np.exp(-0.5 * ((freq - 10.5) / 0.3)**2)  # 1.5x harmonic
    
    # Create the plot with Japanese font
    plt.figure(figsize=(12, 8))
    plt.plot(freq, amplitude, 'k-', linewidth=1)
    
    # Customize for patent style with Japanese text
    plt.xlabel('周波数 (Hz)', fontsize=14, fontfamily='MS Gothic')
    plt.ylabel('振幅', fontsize=14, fontfamily='MS Gothic')
    plt.title('図5 - rESP音響干渉スペクトラム', fontsize=16, fontweight='bold', fontfamily='MS Gothic')
    
    # Add grid
    plt.grid(True, alpha=0.3)
    
    # Mark the 7 Hz peak in Japanese
    plt.annotate('7Hz rESPピーク\n(量子認知干渉)', 
                xy=(7, 0.9), xytext=(12, 0.8),
                arrowprops=dict(arrowstyle='->', color='black'),
                fontsize=12, fontfamily='MS Gothic')
    
    # Set limits and ticks
    plt.xlim(0, 20)
    plt.ylim(0, 1.0)
    plt.xticks(range(0, 21, 2))
    
    # Patent-style appearance
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['left'].set_linewidth(1.5)
    plt.gca().spines['bottom'].set_linewidth(1.5)
    
    # Save in black and white for patent
    plt.savefig('../FIG5_Audio_Spectrum_JA.png', 
                dpi=300, bbox_inches='tight', facecolor='white')
    print("FIG 5 Japanese version saved successfully!")
    plt.show()

if __name__ == "__main__":
    # Create both versions
    create_fig5_spectrum()
    create_fig5_spectrum_japanese() 