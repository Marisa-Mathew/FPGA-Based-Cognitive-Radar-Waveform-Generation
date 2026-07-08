import os

import numpy as np
import scipy.signal as signal
import matplotlib.pyplot as plt

# =====================================================================
# 1. PARAMETERS (High Resolution Mode from DRDO Reference Paper)
# =====================================================================
T = 25e-6          # Pulse width (25 us)
B = 12e6           # Swept Bandwidth (12 MHz)
Fs = 25e6          # Sampling Frequency (25 MHz)
k = 0.078          # Sidelobe level control factor (optimized taper)

# Total number of discrete samples inside the pulse
N = int(T * Fs)    # 25 us * 25 MHz = 625 samples

# =====================================================================
# 2. NLFM WAVEFORM GENERATION
# =====================================================================
# Step A: Create a fine non-uniform frequency grid to numerically invert equation
f_grid = np.linspace(-B/2, B/2, 100000)
# Equation (2): Compute time points matching the given frequency grid
t_grid = T * (f_grid / B) + T * (k / 2.0) * np.pi * np.sin(2.0 * np.pi * f_grid / B)

# Step B: Interpolate frequency grid to map to a uniformly spaced time array
t_uniform = np.linspace(-T/2, T/2, N)
f_t = np.interp(t_uniform, t_grid, f_grid)

# Step C: Phase Accumulation using Trapezoidal integration Rule (Eq 3)
phi = np.zeros(N)
dt = 1.0 / Fs
for i in range(1, N):
    phi[i] = phi[i-1] + np.pi * (f_t[i-1] + f_t[i]) * dt

# Complex baseband signal envelope
s_nlfm = np.exp(1j * phi)

# =====================================================================
# 3. FIXED-POINT QUANTIZATION & .MEM FILE GENERATION
# =====================================================================
# Quantize In-phase (I) and Quadrature (Q) components to signed 16-bit integers
I_quant = np.int16(np.round(np.real(s_nlfm) * 32767))
Q_quant = np.int16(np.round(np.imag(s_nlfm) * 32767))

save_dir = r"C:\Users\maris\OneDrive\Desktop\nit\code_j"
mem_filename = "nlfm_wave.mem"
os.makedirs(save_dir, exist_ok=True)
with open(mem_filename, "w") as f:
    for i in range(N):
        # Convert to unsigned 16-bit format boundaries for standard hexadecimal conversion
        val_i = int(I_quant[i]) & 0xFFFF
        val_q = int(Q_quant[i]) & 0xFFFF
        # Combine I (Upper 16 bits) and Q (Lower 16 bits) into a unified 32-bit word
        word = (val_i << 16) | val_q
        f.write(f"{word:08x}\n")

print(f"Success: '{mem_filename}' file generated with {N} entries.")




# =====================================================================
# 4. VERIFICATION PLOTS
# =====================================================================
plt.figure(figsize=(14, 6))

# Plot A: Time-Frequency Spectrogram (Simulating Fig 14 of ARL-TR-9796)
plt.subplot(1, 2, 1)
frequencies, times, spec_density = signal.spectrogram(
    s_nlfm, Fs, nperseg=64, noverlap=60, return_onesided=False
)
# Shift the zero-frequency components to the center of the spectrum
frequencies = np.fft.fftshift(frequencies)
spec_density = np.fft.fftshift(spec_density, axes=0)

plt.pcolormesh(times * 1e6, frequencies / 1e6, 10 * np.log10(spec_density + 1e-12), shading='gouraud', cmap='jet')
plt.title("Spectrogram / Time-Frequency ")
plt.xlabel("Time ($\mu$s)")
plt.ylabel("Frequency (MHz)")
plt.colorbar(label="Power Spectral Density (dB)")
plt.grid(True)

# Plot B: High-Resolution Mode Frequency Spectrum (Simulating Fig 5 of DRDO Paper)
plt.subplot(1, 2, 2)
fft_size = 2048
windowed_fft = np.fft.fft(s_nlfm, n=fft_size)
fft_shifted = np.fft.fftshift(windowed_fft)
fft_freqs = np.fft.fftshift(np.fft.fftfreq(fft_size, d=1/Fs))
spectrum_db = 20 * np.log10(np.abs(fft_shifted) / np.max(np.abs(fft_shifted)))

plt.plot(fft_freqs / 1e6, spectrum_db, color='b', linewidth=1.5)
plt.title("Frequency Spectrum ")
plt.xlabel("Frequency (MHz)")
plt.ylabel("Normalized Power Amplitude (dB)")
plt.ylim([-50, 5])
plt.grid(True)

plt.tight_layout()
plt.show()


# Compute the matched filter output (Autocorrelation)
mfo = np.convolve(s_nlfm, np.conj(s_nlfm[::-1]))
mfo_db = 20 * np.log10(np.abs(mfo) / np.max(np.abs(mfo)))

# Find the mainlobe peak index
peak_idx = np.argmax(mfo_db)

# Simple check to find the highest peak outside the immediate mainlobe region
# (e.g., ignoring 15 samples around the center peak)
mask = np.ones(len(mfo_db), dtype=bool)
mask[peak_idx-15 : peak_idx+15] = False
psl = np.max(mfo_db[mask])

print(f"Quantified Peak Sidelobe Level (PSL): {psl:.2f} dB")