# 手动最高性能
echo performance | sudo tee /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor
# 手动最低功耗
echo powersave | sudo tee /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor
