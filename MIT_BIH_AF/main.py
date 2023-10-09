import wfdb

# 设置患者04015的路径
mit_bih_af_path = 'C:/mycode/dataset/mit-bih-atrial-fibrillation-database-1.0.0/files/04015'

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

# 获取 一个时间点的索引值
index = MIT_BIH_AF.signal_time_sample("00:06:48.772","10:13:43",len(ECG0))

# 获取一段信号，该点左右 800 范围
signal = ECG0[index-800:index+800]

# 将信号进行去趋势处理
detrend_signal = MIT_BIH_AF.wavelet_detrend(signal)

import matplotlib.pyplot as plt
plt.plot(signal)
plt.savefig("./MIT_BIH_AF/images/wavelet_detrend_ori.jpg", bbox_inches='tight', pad_inches=0) 
plt.close()

plt.plot(detrend_signal)
plt.savefig("./MIT_BIH_AF/images/wavelet_detrend_after.jpg", bbox_inches='tight', pad_inches=0)
plt.close()

