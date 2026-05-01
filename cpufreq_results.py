import matplotlib.pyplot as plt
import csv

govs, freqs, usages = [], [], []
with open('cpufreq_results.csv') as f:
    reader = csv.DictReader(f)
    for row in reader:
        govs.append(row['governor'])
        freqs.append(float(row['avg_freq_kHz']) / 1000000)  # 转为GHz
        usages.append(float(row['avg_cpu_usage_percent']))

fig, ax1 = plt.subplots()
ax2 = ax1.twinx()
ax1.bar(govs, freqs, alpha=0.7, label='Avg Freq (GHz)')
ax2.plot(govs, usages, 'r-o', label='CPU Usage (%)')
ax1.set_ylabel('Avg Frequency (GHz)')
ax2.set_ylabel('CPU Usage (%)')
plt.title('CPU Governor Performance Comparison')
fig.tight_layout()
plt.savefig('cpufreq_comparison.png')