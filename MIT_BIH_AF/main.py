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

# 获取 一个起点时间点的索引值
start_index = MIT_BIH_AF.signal_time_sample("00:08:04.772","10:13:43",len(ECG0))

# 获取 一个终点时间点的索引值
end_index = MIT_BIH_AF.signal_time_sample("00:08:11.672","10:13:43",len(ECG0))

# 建立原信号的伴随标注信号
ECG_ann = MIT_BIH_AF.AFDB_create_mate_ann(len(ECG0), ann_sample, ann_aux_note)

import matplotlib.pyplot as plt
plt.subplot(2,1,1)
plt.plot(ECG0[start_index:end_index])  # 展示原信号
plt.subplot(2,1,2)
plt.plot(ECG_ann[start_index:end_index])  # 展示biaozhu
plt.show()
