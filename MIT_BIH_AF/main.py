import wfdb
import matplotlib.pyplot as plt

# 设置患者04015的路径
mit_bih_af_path = 'C:/mycode/dataset/mit-bih-atrial-fibrillation-database-1.0.0/files/08405'

# 读取患者文件
record = wfdb.rdrecord(mit_bih_af_path, physical=True)
signal_annotation = wfdb.rdann(mit_bih_af_path, "atr")
r_peak_annotation = wfdb.rdann(mit_bih_af_path, "qrs")

# 获取 R 峰标注点列表值
ECG_rpeaks = r_peak_annotation.sample

# 获取信号的房颤注释列表值
ann_aux_note = signal_annotation.aux_note

# 获取标注索引列表
ann_sample = signal_annotation.sample

# 获取通道 0 的信号
ECG0 = record.p_signal[:, 0]

import MIT_BIH_AF_function as MIT_BIH_AF

# 获取时间点的索引值
point1 = MIT_BIH_AF.signal_time_sample("00:06:47.988","10:13:43",len(ECG0))

# 根据索引值查找 8R 峰
signal0, s1, e1 = MIT_BIH_AF.find_nR_peak(8, point1, ECG0, ECG_rpeaks)
ecg_filtered = MIT_BIH_AF.scipy_denoise(signal0)

plt.subplot(2,1,1)
plt.plot(signal0, color='k')
plt.subplot(2,1,2)
plt.plot(ecg_filtered, color='k')
plt.show()
