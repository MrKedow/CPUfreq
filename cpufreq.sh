# 1. 当前使用的调频驱动
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_driver
# 2. 当前频率调控策略
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor
# 3. 系统支持的策略列表
cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_available_governors