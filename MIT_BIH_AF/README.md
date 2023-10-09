# AFDB
这是一个专门AFDB数据的库

# 介绍数据集
## 下载数据集
AFDB是指 MIT-BIH-AF 数据集。这是一个心电房颤数据集的记录。本文件夹则是针对该数据集开发的快捷使用函数。

数据集生理网下载地址：[https://www.physionet.org/content/afdb/1.0.0/](https://www.physionet.org/content/afdb/1.0.0/)

下载后,一共三种类型的文件，dat后缀是记录心电实际信号的文件，atr后缀是心电实际信号对应的标注文件，qrs后缀是心电实际信号的每个R峰的标注文件。不需要担心三种文件的陌生感，已经有团队专门开发出读取这些文件的python集成包----AFDB。

因此，使用数据集前需要在python环境安装该库：

``` pip install AFDB ```

生理网的资料做的很全，不仅提供的数据集的下载，还提供数据集的很多详细说明，需要多加探索，最常用的是快捷可视化。

数据集可视化地址：[https://www.physionet.org/lightwave/?db=afdb/1.0.0](https://www.physionet.org/lightwave/?db=afdb/1.0.0)

可视化界面不仅显示了数据集的实际信号，数据集的标注也显示了出来，可视化界面如图：


<left><img src = "./images/PhysioNet_wave.jpg" width = 100%><left>

# 函数库使用
## 读取dat,qrc,atr文件
```
import wfdb

# 设置患者04015的路径
mit_bih_af_path = C:/mycode/dataset/mit-bih-atrial-fibrillation-database-1.0.0/files/04015

# 读取患者文件
record = wfdb.rdrecord(mit_bih_af_path, physical=True)
signal_annotation = wfdb.rdann(mit_bih_af_path, "atr")
r_peak_annotation = wfdb.rdann(mit_bih_af_path, "qrs")

# 提取患者文件信息
ECG_rpeaks = r_peak_annotation.sample
ECG0 = record.p_signal[:, 0]
ann_aux_note = signal_annotation.aux_note
ann_sample = signal_annotation.sample
```
使用提取信息
```
# 获取 R 峰标注点列表值
ECG_rpeaks = r_peak_annotation.sample
print(ECG_rpeaks)

# 获取信号的房颤注释列表值
ann_aux_note = signal_annotation.aux_note
print(ann_aux_note)

# 获取标注索引列表
ann_sample = signal_annotation.sample
print(ann_sample)
```
展示信号
```
import matplotlib.pyplot as plt
plt.plot(ECG0[0:2000])  # 打印输出 ECG0 信号0-2000的值
plt.show()
```
<left><img src = "./images/ecg0_0_2000.png" width = 100%><left>

## 寻找某个时间点----signal_time_sample
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
plt.plot(ECG0[index-500:index+500])  # 打印输出 ECG0 信号0-2000的值
plt.show()

```
<left><img src = "./images/PhysioNet_wave_resample_time2.jpg" width = 100%><left>
