import numpy as np
import scipy.signal as signal
import matplotlib.pyplot as plt

# =====================================================================
# 1. GENERATE BASELINE HIGH-RESOLUTION MODE NLFM WAVEFORM
# =====================================================================
T = 25e-6          # Pulse width (25 us)
B = 12e6           # Swept Bandwidth (12 MHz)
Fs = 25e6          # Sampling Frequency (25 MHz)
k = 0.078          # Sidelobe control factor
N = int(T * Fs)

# Numerical inversion to create the NLFM phase grid
f_grid = np.linspace(-B/2, B/2, 100000)
t_grid = T * (f_grid / B) + T * (k / 2.0) * np.pi * np.sin(2.0 * np.pi * f_grid / B)
t_uniform = np.linspace(-T/2, T/2, N)
f_t = np.interp(t_uniform, t_grid, f_grid)

phi = np.zeros(N)
dt = 1.0 / Fs
for i in range(1, N):
    phi[i] = phi[i-1] + np.pi * (f_t[i-1] + f_t[i]) * dt

s_ideal = np.exp(1j * phi)

# =====================================================================
# 2. METRIC 1: SIGNAL-TO-QUANTIZATION-NOISE RATIO (SQNR)
# =====================================================================
# Quantize to 16-bit integers (as performed during .mem generation)
I_quant = np.round(np.real(s_ideal) * 32767)
Q_quant = np.round(np.imag(s_ideal) * 32767)

# Reconstruct normalized floating point vector from quantized values
s_quantized = (I_quant + 1j * Q_quant) / 32767.0

# Calculate quantization noise power
quantization_noise = s_ideal - s_quantized
signal_power = np.sum(np.abs(s_ideal)**2)
noise_power = np.sum(np.abs(quantization_noise)**2)
sqnr_db = 10 * np.log10(signal_power / noise_power)

# =====================================================================
# 3. MATCHED FILTERING / PULSE COMPRESSION (Autocorrelation)
# =====================================================================
# Matched filter is the complex conjugate of the transmitted signal
matched_filter = np.conj(s_ideal[::-1])
compressed_signal = np.convolve(s_ideal, matched_filter, mode='full')

# Normalize the compressed pulse response to its peak power (0 dB)
compressed_mag = np.abs(compressed_signal)
peak_idx = np.argmax(compressed_mag)
compressed_db = 20 * np.log10(compressed_mag / compressed_mag[peak_idx])

# Time axis for the matched filter output sequence
time_axis = (np.arange(len(compressed_db)) - peak_idx) / Fs

# =====================================================================
# 4. METRIC 2: RANGE RESOLUTION (3-dB MAINLOBE WIDTH)
# =====================================================================
# Trace leftward from peak to find the -3 dB crossing point
idx_left = peak_idx
while idx_left > 0 and compressed_db[idx_left] > -3.0:
    idx_left -= 1
# Linear interpolation for sub-sample accuracy
t_left = idx_left + (-3.0 - compressed_db[idx_left]) / (compressed_db[idx_left+1] - compressed_db[idx_left])

# Trace rightward from peak to find the -3 dB crossing point
idx_right = peak_idx
while idx_right < len(compressed_db) and compressed_db[idx_right] > -3.0:
    idx_right += 1
t_right = idx_right - (-3.0 - compressed_db[idx_right]) / (compressed_db[idx_right-1] - compressed_db[idx_right])

mainlobe_3db_width_samples = t_right - t_left
mainlobe_3db_width_seconds = mainlobe_3db_width_samples / Fs

# =====================================================================
# 5. METRICS 3 & 4: PEAK & INTEGRATED SIDELOBE LEVELS (PSL & ISL)
# =====================================================================
# Isolate the mainlobe by searching for the first local nulls surrounding the peak
null_left = peak_idx
while null_left > 0 and compressed_mag[null_left-1] < compressed_mag[null_left]:
    null_left -= 1

null_right = peak_idx
while null_right < len(compressed_mag)-1 and compressed_mag[null_right+1] < compressed_mag[null_right]:
    null_right += 1

# Identify all local peaks across the entire compressed profile
all_peaks, _ = signal.find_peaks(compressed_db, height=-100)

# Filter out the mainlobe peak to isolate the sidelobes
sidelobe_peaks = [p for p in all_peaks if p < null_left or p > null_right]
peak_sidelobe_idx = sidelobe_peaks[np.argmax(compressed_db[sidelobe_peaks])]
psl_db = compressed_db[peak_sidelobe_idx]

# Calculate Integrated Sidelobe Level (ISL) energy metrics
total_energy = np.sum(compressed_mag**2)
mainlobe_energy = np.sum(compressed_mag[null_left:null_right+1]**2)
sidelobe_energy = total_energy - mainlobe_energy
isl_db = 10 * np.log10(sidelobe_energy / mainlobe_energy)

# =====================================================================
# 6. PRINT QUANTIFIED PERFORMANCE REPORT
# =====================================================================
print("="*60)
print("             NLFM WAVEFORM PERFORMANCE REPORT            ")
print("="*60)
print(f"1. Signal-to-Quantization-Noise (16-bit SQNR) : {sqnr_db:.2f} dB")
print(f"2. Peak Sidelobe Level (PSL)                  : {psl_db:.2f} dB")
print(f"3. Integrated Sidelobe Level (ISL)            : {isl_db:.2f} dB")
print(f"4. 3-dB Mainlobe Pulse Width                  : {mainlobe_3db_width_seconds*1e6:.4f} us")
print(f"5. Ideal Radar Range Resolution (c * width / 2): {3e8 * mainlobe_3db_width_seconds / 2.0:.2f} meters")
print("="*60)

# =====================================================================
# 7. PERFORMANCE VISUALIZATION PLOT
# =====================================================================
plt.figure(figsize=(10, 6))
plt.plot(time_axis * 1e6, compressed_db, color='b', label='Compressed Pulse (Autocorrelation)')

# Highlight critical metrics on the plot
plt.axhline(psl_db, color='r', linestyle='--', label=f'Peak Sidelobe Level ({psl_db:.2f} dB)')
plt.axhline(-3.0, color='g', linestyle=':', label='3-dB Threshold')
plt.plot(time_axis[peak_sidelobe_idx]*1e6, psl_db, 'ro', markersize=8, label='Highest Sidelobe Peak')

# Add plot markers for the isolated mainlobe boundaries
plt.axvline(time_axis[null_left]*1e6, color='black', alpha=0.5, linestyle='-.', label='Mainlobe Null Boundaries')
plt.axvline(time_axis[null_right]*1e6, color='black', alpha=0.5, linestyle='-.')

plt.title("Quantified Radar Pulse Compression Profile")
plt.xlabel("Time Delay ($\mu$s)")
plt.ylabel("Normalized Power Amplitude (dB)")
plt.xlim([-5, 5])  # Zoomed into focus area around center peak
plt.ylim([-60, 5])
plt.grid(True)
plt.legend(loc='upper right')
plt.tight_layout()
plt.show()