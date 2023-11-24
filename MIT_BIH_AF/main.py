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

# 获取时间点的索引值
point1 = MIT_BIH_AF.signal_time_sample("00:06:47.988","10:13:43",len(ECG0))
point2 = MIT_BIH_AF.signal_time_sample("00:06:53.186","10:13:43",len(ECG0))

# 根据索引值查找 2R 峰
signal1, s1, e1 = MIT_BIH_AF.find_nR_peak(2, point1, ECG0, ECG_rpeaks)
signal2, s2, e2 = MIT_BIH_AF.find_nR_peak(2, point2, ECG0, ECG_rpeaks)

# 创建一个关于信号的伴随列表
ECG_ann = MIT_BIH_AF.AFDB_create_mate_ann(len(ECG0), ann_sample, ann_aux_note)

label1 = MIT_BIH_AF.find_signal_label(s1, e1, ECG_ann)
label2 = MIT_BIH_AF.find_signal_label(s2, e2, ECG_ann)

print("采样点1    00:06:47.988 处的标签是：", label1)
print("采样点2    00:06:53.186 处的标签是：", label2)
