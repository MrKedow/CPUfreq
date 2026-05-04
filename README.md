# Linux CPU 动态调频策略验证工具

基于 `Linux cpufreq` 子系统的 CPU 调频策略对比验证工具。通过自动切换不同 ```Governor```、施加标准负载、采集频率与功耗数据，筛选适配低负载场景的最优节能方案。

## 项目背景

在车载计算平台（如域控制器、智能座舱 SoC）中，CPU 的功耗与散热直接影响整车热管理和续航表现。Linux 内核提供了 ```cpufreq``` 子系统，支持多种调频策略（Governor），但不同策略在特定负载场景下的功耗与性能表现差异显著。本项目通过可复现的实验方法，量化对比各策略的实际效果，为车载场景下的调频策略选择提供数据支撑。

## 功能

- 自动遍历 `ondemand`、`conservative`、`schedutil`、`performance`、```powersave``` 五种 ```Governor```
- 使用 `stress-ng` 施加标准 CPU 负载
- 实时采集 CPU 频率（`scaling_cur_freq`）、使用率（`/proc/stat`）和核心电压（树莓派）`vcgencmd`
- 将实验数据写入 CSV 文件，支持后续分析与可视化

## 硬件平台

- **Raspberry Pi（树莓派）**：4B（Broadcom BCM2711, 4 核 Cortex-A72）
- **Orange Pi（香橙派）**：Zero 2W（全志 H616, 4 核 Cortex-A53）
- **不支持**：WSL2 虚拟机（缺少 cpufreq 子系统暴露接口）

## 软件环境

- 操作系统：`Ubuntu Server 22.04 LTS (64-bit)`
- 内核版本：`5.15+`
- Python: `Python 3.8+`
- 系统工具：`stress-ng、linux-tools-common、cpufrequtils`

## 安装依赖

```bash
sudo apt update
sudo apt install stress-ng linux-tools-common cpufrequtils python3 python3-pip -y
```
## 快速开始
1. 克隆仓库
```bash
git clone https://github.com/MrKedow/CPUfreq.git
cd CPUfreq
```
2. 运行实验
```bash
① 创建虚拟环境
cd ~/CPUfreq #这是在`CPUfreq`目录创建虚拟环境，也可选其他目录。`~`代表直达“安装`Ubuntu 24.04`后，以自己名字命名的目录。
python -m venv CPUfreq_venv #创建虚拟环境。CPUfreq_venv是本仓库默认的虚拟环境名，可以换成其他名字。
source ~/CPUfreq/CPUfreq_venv/bin/activate #激活虚拟环境。
② 启动五方案轮询脚本
sudo python3 cpufreq_tester.py
```
轮询过程约 5 分钟，脚本会依次测试五种 `Governor`，每种策略下使用 `stress-ng` 施加 30 秒负载，采集频率和 CPU 使用率数据。

3. 查看结果
实验完成后会在当前目录生成 `cpufreq_results_YYYYMMDD_HHMMSS.csv` 文件，内容格式：
```
governor	avg_freq_kHz	avg_cpu_usage_percent
ondemand	800000	72.3
conservative	600000	70.1
schedutil	700000	69.8
performance	1500000	68.5
powersave	600000	71.2
```
4. 生成图表
```bash
python3 plot_results.py cpufreq_results_YYYYMMDD_HHMMSS.csv
```
此命令会输出 `cpufreq_comparison.png`，包含频率与 CPU 使用率的双 Y 轴对比图。

## 实验结论
在低负载场景下，`schedutil` 策略以接近 `ondemand` 的吞吐量实现了更低的平均频率，能效比最优。`performance` 策略功耗最高，`powersave` 策略导致 CPU 占用率偏高（任务执行时间拉长）。对于车载场景中常见的传感器轮询、日志上报等间歇性低负载任务，推荐使用 `schedutil`。

## Fork 注意事项
1. 轮询期间请关闭其他应用程序，避免干扰 CPU 负载采样

2. 树莓派需要装散热片，避免高温触发 `Thermal Throttling` 导致被内核强制降频

3. 使用 ```vcgencmd measure_volts core``` 可额外记录核心电压（只有树莓派），脚本是仓库内的 `cpufreq_tester_Volt.py`

## 项目结构
```text
CPUfreq/
├── cpufreq_tester.py      # 测试脚本
├── plot_results.py        # 数据、图表脚本
├── README.md
└── .gitignore
```
