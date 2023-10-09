# MIT_BIH_AF
本文件夹是一个专门开发 MIT-BIH-AF 数据集的库

# 目录

- [1 介绍数据集 ](#1-介绍数据集)
  - [1.1 下载数据集](#11-下载数据集)
- [2 函数库使用](#2-函数库使用)
  - [2.1 读取dat,qrc,atr文件，获得ECG_rpeaks，ann_aux_note，ann_sample，ECG0](#21-读取datqrcatr文件获得ecg_rpeaksann_aux_noteann_sampleecg0)
  - [2.2 寻找时间点函数----signal_time_sample](#22-寻找时间点函数----signal_time_sample)
  - [2.3 寻找R_R峰在信号中的位置----find_R_R_peak](#23-寻找r_r峰在信号中的位置----find_r_r_peak)
  - [2.4 寻找一段信号中的所有 R 峰----find_R_R_peaks](#24-寻找一段信号中的所有-r-峰----find_r_r_peaks)
  - [2.5 为信号建立伴随标注信号----AFDB_create_mate_ann](#25-为信号建立伴随标注信号----afdb_create_mate_ann)
  - [2.6 重采样信号长度----resample_signal_length](#26-重采样信号长度----resample_signal_length)

# 1 介绍数据集 
MIT-BIH-AF 是一个心电图信号房颤数据集。本文件夹则是针对该数据集开发的快捷使用函数。MIT-BIH-AF 数据集采集有 23 人的两导联数据。总长十个小时。单个病人约920万个数据点长度。注意,'00735', '03665' 病人没有 data 数据,虽然数据集有他们的标注但没有他们的信号，不可用。

<left><img src = "./images/MIT-BIH-AF.jpg" width = 100%><left>

## 1.1 下载数据集

数据集生理网下载地址：[https://www.physionet.org/content/afdb/1.0.0/](https://www.physionet.org/content/afdb/1.0.0/)

下载后,一共三种类型的文件，分别是dat,atr,qrc后缀。不需要担心三种文件的陌生感，已经有团队专门开发出读取这些文件的python集成包----WFDB。

因此，使用数据集前需要在python环境安装该库：```pip install wfdb```

生理网的资料做的很全，不仅提供的数据集的下载，网站还提供了数据集的很多详细说明，如记录时长，采样率，患者描述等。更多信息需要自己多探索，而最常用的是快捷波形可视化。

数据集可视化地址：[https://www.physionet.org/lightwave/?db=afdb/1.0.0](https://www.physionet.org/lightwave/?db=afdb/1.0.0)

可视化界面不仅显示了数据集的实际信号，而且对数据集的标注也显示了出来，可视化界面如图：

<left><img src = "./images/PhysioNet_wave.jpg" width = 100%><left>

其他可视化资源：[PhysioBank ATM 彩色版](https://archive.physionet.org/cgi-bin/atm/ATM)

# 2 函数库使用

如下介绍的库函数功能，都是平时用得最为频繁的基础功能，为了避免重复编写代码因此自己编写成库，使用代码```import MIT_BIH_AF_function as MIT_BIH_AF```将本文件夹代码库加载。

## 2.1 读取dat,qrc,atr文件，获得ECG_rpeaks，ann_aux_note，ann_sample，ECG0


dat后缀是记录心电实际信号的文件，atr后缀是心电实际信号对应的标注文件，qrs后缀是心电实际信号的每个R峰的标注文件
```
import wfdb

# 设置患者04015的路径
mit_bih_af_path = 'C:/mycode/dataset/mit-bih-atrial-fibrillation-database-1.0.0/files/04015'

# 读取患者文件
record = wfdb.rdrecord(mit_bih_af_path, physical=True)
signal_annotation = wfdb.rdann(mit_bih_af_path, "atr")
r_peak_annotation = wfdb.rdann(mit_bih_af_path, "qrs")

# 获取 R 峰标注点列表值
ECG_rpeaks = r_peak_annotation.sample
print(ECG_rpeaks)

# 获取信号的房颤注释列表值
ann_aux_note = signal_annotation.aux_note
print(ann_aux_note)

# 获取标注索引列表
ann_sample = signal_annotation.sample
print(ann_sample)

# 获取通道 0 的信号
ECG0 = record.p_signal[:, 0]

# 展示信号
import matplotlib.pyplot as plt
plt.plot(ECG0[0:2000])  # 打印输出 ECG0 信号0-2000的值
plt.show()
```
<left><img src = "./images/ecg0_0_2000.png" width = 60%><left>

## 2.2 寻找时间点函数----signal_time_sample


本函数用于在代码中找到我们看到的感兴趣段落的位置。
如可视化界面我们的时间点为 "00:06:50.316"。
<left><img src = "./images/PhysioNet_wave_resample_time.jpg" width = 100%><left>

获取该处时间点在信号中的索引值，并展示
```
import MIT_BIH_AF_function as MIT_BIH_AF 

# 输入时间点，获取该处时间点的索引值
index = MIT_BIH_AF.signal_time_sample("00:06:50.316","10:13:43",len(ECG0))

# 展示该索引值左右500的信号
import matplotlib.pyplot as plt
plt.plot(ECG0[index-500:index+500])  # 打印输出 ECG0 信号
plt.show()
```
<left><img src = "./images/PhysioNet_wave_resample_time2.jpg" width = 60%><left>

## 2.3 寻找R_R峰在信号中的位置----find_R_R_peak
日常使用时经常遇到提取单个R峰的情况，本函数具备此功能。

使用代码举例：
```
import MIT_BIH_AF_function as MIT_BIH_AF

# 获取该处时间点的索引值
index = MIT_BIH_AF.signal_time_sample("00:06:48.817","10:13:43",len(ECG0))

# 根据索引值找到 R 峰信号，起点s, 终点e
signal, s, e = MIT_BIH_AF.find_R_R_peak(index, ECG0, ECG_rpeaks)

# 展示信号
import matplotlib.pyplot as plt
plt.plot(signal)  # 打印输出 signal 信号
plt.show()
```

|原采样点|采样出的R峰|
|:--------------:|:-----:|
|<left><img src = "./images/find_r_r_peak1.jpg" width = 80%><left>|<left><img src = "./images/find_r_r_peak2.jpg" width = 100%><left>|

## 2.4 寻找一段信号中的所有 R 峰----find_R_R_peaks
我们除了上面的要提取单独 R 峰。很多情况下，我们还要在一段心电信号中提取出该段落的所有单个 R 峰信号。

使用代码举例：
```
import MIT_BIH_AF_function as MIT_BIH_AF

# 获取 起点时间点的索引值
start_index = MIT_BIH_AF.signal_time_sample("00:06:48.067","10:13:43",len(ECG0))

# 获取 终点时间点的索引值
end_index = MIT_BIH_AF.signal_time_sample("00:06:51.764","10:13:43",len(ECG0))

# 根据索引值查找 R 峰
r_peaks_position = MIT_BIH_AF.find_R_R_peaks(start_index, end_index, ECG0, ECG_rpeaks)

for i in r_peaks_position: 
    r_signal = ECG0[i[0]:i[1]]
    
    # 展示信号
    import matplotlib.pyplot as plt
    plt.plot(r_signal)
    plt.show()
```
原信号片段

<left><img src = "./images/find_r_r_peaks1.jpg" width = 100%><left>

|1|2|3|4|5|6|7|
|----|----|----|----|----|----|----|
|<left><img src = "./images/find_r_r_peaks_r0.jpg" width = 100%><left> |<left><img src = "./images/find_r_r_peaks_r1.jpg" width = 100%><left> |<left><img src = "./images/find_r_r_peaks_r2.jpg" width = 100%><left> |<left><img src = "./images/find_r_r_peaks_r3.jpg" width = 100%><left> |<left><img src = "./images/find_r_r_peaks_r4.jpg" width = 100%><left> |<left><img src = "./images/find_r_r_peaks_r5.jpg" width = 100%><left> |<left><img src = "./images/find_r_r_peaks_r6.jpg" width = 100%><left> |

## 2.5 为信号建立伴随标注信号----AFDB_create_mate_ann
建立伴随标注信号在代码中存在很大的好处。使得波形提取对应的标注更加方便。避免麻烦的原信号标注类型寻找。如图下面的波形可视化原信号，根据atr文件的标注可以看到，患者发生了一秒左右的房颤。但数据集并不是对每一个点进行标注，伴随标注信号应运而生。
<left><img src = "./images/AFDB_create_mate_ann.jpg" width = 100%><left>

使用代码举例：
```
import MIT_BIH_AF_function as MIT_BIH_AF

# 获取 一个起点时间点的索引值
start_index = MIT_BIH_AF.signal_time_sample("00:08:04.772","10:13:43",len(ECG0))

# 获取 一个终点时间点的索引值
end_index = MIT_BIH_AF.signal_time_sample("00:08:11.672","10:13:43",len(ECG0))

# 建立原信号的伴随标注信号
ECG_ann = MIT_BIH_AF.AFDB_create_mate_ann(len(ECG0), ann_sample, ann_aux_note)

# 展示波形
import matplotlib.pyplot as plt
plt.subplot(2,1,1)
plt.plot(ECG0[start_index:end_index])  # 展示原信号
plt.subplot(2,1,2)
plt.plot(ECG_ann[start_index:end_index])  # 展示biaozhu
plt.show()
```
运行结果如下，下图中第一张表是原信号，第二张表是伴随标注信号（"1"代表房颤，"0"表示正常）

<left><img src = "./images/AFDB_create_mate_ann1.jpg" width = 60%><left>

## 2.6 重采样信号长度----resample_signal_length
在我们提取信号之后，最终将信号送入模型训练。但多数情况下，模型信号输入长度有要求。而我们采集的信号可能不是固定长度的，于是开发了本函数将一段信号重采样到指定的长度。注意本函数是基于 scipy 库实现的，如果出现缺少 scipy 库缺失相关的报错，请使用```pip install scipy```

使用代码举例：
```
import MIT_BIH_AF_function as MIT_BIH_AF

# 获取 一个起点时间点的索引值
start_index = MIT_BIH_AF.signal_time_sample("00:08:04.772","10:13:43",len(ECG0))

# 获取一段信号
signal, s, e = MIT_BIH_AF.find_R_R_peak(start_index, ECG0, ECG_rpeaks)

# 将信号长度重采样到500
resample_signal = MIT_BIH_AF.resample_signal_length(signal, 500)
```
运行结果如图，原信号长度 200（蓝色），重采样到了 500 长度（橙色）

<left><img src = "./images/signal_time_sample.jpg" width = 60%><left>
