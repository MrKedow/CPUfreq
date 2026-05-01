import os
import time
import subprocess
import csv
import statistics

GOVERNORS = ['ondemand', 'conservative', 'schedutil', 'performance', 'powersave']
TEST_DURATION = 30
OUTPUT_CSV = 'cpufreq_results.csv'

def set_governor(gov):
    for cpu in range(4):
        with open(f'/sys/devices/system/cpu/cpu{cpu}/cpufreq/scaling_governor', 'w') as f:
            f.write(gov)

def get_cur_freq(cpu=0):
    with open(f'/sys/devices/system/cpu/cpu{cpu}/cpufreq/scaling_cur_freq') as f:
        return int(f.read().strip())

def get_cpu_usage():
    with open('/proc/stat') as f:
        fields = f.readline().split()
    total = sum(int(x) for x in fields[1:])
    idle = int(fields[4])
    return total, idle
def get_voltage():
    try:
        out = subprocess.check_output(['vcgencmd', 'measure_volts', 'core'], text=True)
        return float(out.strip().split('=')[1][:-1])
    except:
        return 0.0

def run_stress(duration):
    return subprocess.Popen(['stress-ng', '--cpu', '4', '--timeout', str(duration)])

def main():
    results = []
    for gov in GOVERNORS:
        set_governor(gov)
        time.sleep(0.5)
        proc = run_stress(TEST_DURATION)
        time.sleep(2)  # 等负载稳定
        freq_samples = []
        t1_total, t1_idle = get_cpu_usage()
        start = time.time()
        while time.time() - start < TEST_DURATION - 2:
            freq_samples.append(get_cur_freq(0))
            time.sleep(0.5)
        t2_total, t2_idle = get_cpu_usage()
        total_diff = t2_total - t1_total
        idle_diff = t2_idle - t1_idle
        avg_usage = 100.0 * (total_diff - idle_diff) / total_diff if total_diff > 0 else 0
        avg_freq = statistics.mean(freq_samples)
        results.append([gov, avg_freq, avg_usage])
        proc.wait()
        time.sleep(2)

    with open(OUTPUT_CSV, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['governor', 'avg_freq_kHz', 'avg_cpu_usage_percent'])
        writer.writerows(results)
    print(f'Done. Results saved to {OUTPUT_CSV}')

if __name__ == '__main__':
    main()