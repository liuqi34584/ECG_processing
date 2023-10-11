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

# 获取 起点时间点的索引值
start_index = MIT_BIH_AF.signal_time_sample("00:06:48.067","10:13:43",len(ECG0))

# 获取 终点时间点的索引值
end_index = MIT_BIH_AF.signal_time_sample("00:06:51.764","10:13:43",len(ECG0))

# 根据索引值查找 3R 峰
r_peaks_position = MIT_BIH_AF.find_nR_peaks(3, start_index, end_index, ECG0, ECG_rpeaks)

for i in r_peaks_position: 
    r_signal = ECG0[i[0]:i[1]]
    
    # 展示信号
    import matplotlib.pyplot as plt
    plt.plot(r_signal)
    plt.show()
