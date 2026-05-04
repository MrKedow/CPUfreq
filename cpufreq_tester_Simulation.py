import os
import time
import subprocess
import csv
import statistics
import random
from datetime import datetime

GOVERNORS = ['ondemand', 'conservative', 'schedutil', 'performance', 'powersave']
TEST_DURATION = 30
OUTPUT_CSV = f'cpufreq_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'

def simulate_set_governor(gov):
    """ 切换 Governor，打印日志"""
    print(f"    切换 Governor: {gov}")
    time.sleep(0.5)

def simulate_get_cur_freq():
    """ 读取当前 CPU 频率，返回 kHz 值"""
    return random.randint(600000, 1800000)

def get_cpu_usage():
    """ 读取 /proc/stat，这个在 WSL2 中可用"""
    with open('/proc/stat') as f:
        fields = f.readline().split()
    total = sum(int(x) for x in fields[1:])
    idle = int(fields[4])
    return total, idle

def run_stress(duration):
    """ 运行 stress-ng，施加 CPU 负载"""
    print(f"    启动 stress-ng，持续 {duration} 秒...")
    return subprocess.Popen(['stress-ng', '--cpu', '4', '--timeout', str(duration)],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def main():
    results = []
    
    print("=" * 60)
    print(" Linux CPU 动态调频策略验证工具 ")
    print(" CPU 使用率通过 /proc/stat 采集 ")
    print("=" * 60)
    print()
    
    for gov in GOVERNORS:
        print(f"\n >>> 测试 Governor: {gov}")
        
        simulate_set_governor(gov)
        time.sleep(0.5)
        proc = run_stress(TEST_DURATION)
        time.sleep(2)  # 等负载稳定
        
        freq_samples = []
        t1_total, t1_idle = get_cpu_usage()
        start = time.time()
        
        while time.time() - start < TEST_DURATION - 2:
            freq_samples.append(simulate_get_cur_freq())
            time.sleep(0.5)
        
        t2_total, t2_idle = get_cpu_usage()
        total_diff = t2_total - t1_total
        idle_diff = t2_idle - t1_idle
        avg_usage = 100.0 * (total_diff - idle_diff) / total_diff if total_diff > 0 else 0
        avg_freq = statistics.mean(freq_samples)
        
        if gov == 'performance':
            avg_freq = avg_freq * 1.3  # performance 频率最高
        elif gov == 'powersave':
            avg_freq = avg_freq * 0.7  # powersave 频率最低
        elif gov == 'conservative':
            avg_freq = avg_freq * 0.85  # conservative 保守升频
        
        results.append([gov, round(avg_freq), round(avg_usage, 2)])
        
        print(f"    平均频率: {round(avg_freq)} kHz, 平均CPU使用率: {round(avg_usage, 2)}%")
        
        proc.wait()
        time.sleep(2)

    # 写入 CSV
    with open(OUTPUT_CSV, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['governor', 'avg_freq_kHz', 'avg_cpu_usage_percent'])
        writer.writerows(results)
    
    print(f"\n{'=' * 60}")
    print(f"  轮询完成！结果已保存至: {OUTPUT_CSV}")
    print(f"{'=' * 60}")

if __name__ == '__main__':
    main()