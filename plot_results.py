import os
import sys
import csv
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

def plot_results(csv_file):
    """读取 CSV 文件并生成双 Y 轴对比图"""
    govs, freqs, usages = [], [], []

    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            govs.append(row['governor'])
            # 将 kHz 转为 GHz
            freqs.append(float(row['avg_freq_kHz']) / 1_000_000)
            usages.append(float(row['avg_cpu_usage_percent']))

    # 创建图表
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # 左侧 Y 轴：平均频率（GHz），柱状图
    color_freq = '#2c3e50'
    ax1.set_xlabel('Governor', fontsize=12)
    ax1.set_ylabel('Average Frequency (GHz)', color=color_freq, fontsize=12)
    bars = ax1.bar(govs, freqs, alpha=0.8, color=color_freq, width=0.5)
    ax1.tick_params(axis='y', labelcolor=color_freq)
    ax1.set_ylim(0, max(freqs) * 1.25)

    # 在柱子上方标注具体频率值
    for bar, freq in zip(bars, freqs):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                 f'{freq:.2f}', ha='center', va='bottom', fontsize=9)

    # 右侧 Y 轴：平均 CPU 使用率，折线图
    ax2 = ax1.twinx()
    color_usage = '#e74c3c'
    ax2.set_ylabel('Average CPU Usage (%)', color=color_usage, fontsize=12)
    ax2.plot(govs, usages, 'o-', color=color_usage, linewidth=2, markersize=8, label='CPU Usage')
    ax2.tick_params(axis='y', labelcolor=color_usage)
    ax2.set_ylim(0, 100)

    # 在数据点旁标注使用率
    for i, usage in enumerate(usages):
        ax2.text(i, usage + 2, f'{usage:.1f}%', ha='center', fontsize=9, color=color_usage)

    # 标题与网格
    plt.title('CPU Governor Performance & Power Comparison', fontsize=14, fontweight='bold')
    ax1.grid(axis='y', alpha=0.3, linestyle='--')

    # 图例
    from matplotlib.patches import Patch
    from matplotlib.lines import Line2D
    legend_elements = [
        Patch(facecolor=color_freq, alpha=0.8, label='Average Frequency (GHz)'),
        Line2D([0], [0], color=color_usage, marker='o', linewidth=2, markersize=8, label='CPU Usage (%)')
    ]
    ax1.legend(handles=legend_elements, loc='upper right', fontsize=9)

    fig.tight_layout()

    # 生成输出文件名
    output_file = csv_file.replace('.csv', '.png')
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"图表已保存: {output_file}")

    # 如果环境支持图形界面，显示图表
    try:
        plt.show()
    except:
        pass

if __name__ == '__main__':
    # 如果有命令行参数，直接使用
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    else:
        # 否则列出当前目录下所有 csv 文件，让用户选择
        csv_files = [f for f in os.listdir('.') if f.startswith('cpufreq_results') and f.endswith('.csv')]
        if not csv_files:
            print("未找到 cpufreq_results 开头的 CSV 文件。")
            print("用法: python3 plot_results.py 你的结果文件.csv")
            sys.exit(1)

        print("找到以下结果文件：")
        for i, f in enumerate(csv_files):
            print(f"  [{i+1}] {f}")

        try:
            choice = int(input("请选择要绘图的文件序号: ")) - 1
            csv_file = csv_files[choice]
        except (ValueError, IndexError):
            print("无效的选择，请重新运行。")
            sys.exit(1)

    # 检查文件是否存在
    if not os.path.exists(csv_file):
        print(f"错误: 文件 '{csv_file}' 不存在。")
        sys.exit(1)

    # 检查是否有 matplotlib
    try:
        import matplotlib
    except ImportError:
        print("错误: 需要安装 matplotlib。请运行: pip install matplotlib")
        sys.exit(1)

    plot_results(csv_file)