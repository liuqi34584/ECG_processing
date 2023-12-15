import numpy as np
import os
import wfdb
from IPython.display import display

# 获取数据所有病人信息
# 传入：病人字符 ID 号码，病人文件位置列表
# 返回值：病人信息字符串
# 使用举例：
# 作者：刘琦
def get_patient_info(id_str:str, patient_list):

    index = 0
    info = ""

    # 提取每个路径中的最后一个文件名
    last_folders = [path.split('/')[-1]  for path in patient_list]
    if id_str in last_folders:
        index = last_folders.index(id_str)

        # 读取患者文件
        record = wfdb.rdrecord(patient_list[index], physical=True)
        signal_annotation = wfdb.rdann(patient_list[index], "atr")
        ann_aux_note = signal_annotation.aux_note
        from collections import Counter
        element_count = Counter(ann_aux_note)

        info = "患者姓名：{}  \n".format(record.record_name) + \
               "通道数量：{}  \n".format(record.n_sig) + \
               "通道名字：{}  \n".format(record.sig_name) + \
               "信号长度：{}  \n".format(record.sig_len) + \
               "R 峰数量： {}  \n".format(len(signal_annotation.sample)) + \
               "标注情况： {}  \n".format(element_count)

    else:
        print("{} 不在文件列表中".format(id_str))
        index = 0
        info = ""

    return index, info

# 获取数据所有病人 ID 号码
# 传入：数据集根路径
# 返回值：病人文件位置列表
# 使用举例：patient_list = CPSC2021.get_patient_ids("C:/mycode/dataset/CPSC2021/")
# 作者：刘琦
def get_patient_ids(dataset_root):

    patient_list = []

    training_I_path = os.path.join(dataset_root, "training_I/")
    training_I_patient_ids = os.listdir(training_I_path)
    training_I_patient_ids = [os.path.splitext(file)[0] for file in training_I_patient_ids]  # 去掉文件的后缀名
    training_I_patient_ids = sorted(list(set(training_I_patient_ids)))
    for i in training_I_patient_ids[2:]:  # 根据文件列表，前两个元素是 'RECORDS', 'REVISED_RECORDS'
        patient_list.append(os.path.join(training_I_path, i))

    training_II_path = os.path.join(dataset_root, "training_II/")
    training_II_patient_ids = os.listdir(training_II_path)
    training_II_patient_ids = [os.path.splitext(file)[0] for file in training_II_patient_ids]  # 去掉文件的后缀名
    training_II_patient_ids = sorted(list(set(training_II_patient_ids)))
    for i in training_II_patient_ids[2:]:  # 根据文件列表，前两个元素是 'RECORDS', 'REVISED_RECORDS'
        patient_list.append(os.path.join(training_II_path, i))

    return patient_list

# 创建一个关于信号的伴随列表
# 传入：信号长度，R峰标注数组，标记符号数组
# 传出： 一个信号同样长度的标注列表
# 使用举例：ECG_ann = CPSC2021.create_mate_ann(len(ECG0), ECG_rpeaks, ann_aux_note)
# 此方法只适用于 CPSC2021 数据集的标注样式
# 作者：刘琦
def create_mate_ann(signal_length, ECG_rpeaks, aux_note):

    # 首先，重刷标记数组,使得列表仅为两种符号 '(AFIB'-1, '(N'-0。最后保存到 note 列表中
    note = []
    current_ann = 0
    for ann in aux_note:

        if ann == '(N':
            current_ann = 0
        if ann == '(AFIB' or  ann == '(AFL' :
            current_ann = 1

        note.append(current_ann)

    # 其次，定义一个关于数据的伴随注释列表数据,这个循环的核心目的是为当前的索引位置找到应该属于的类型
    # 当前的数据索引类型，应该等于采样列表左边的值
    C, S = 0, 0  
    mate_ann = []

    for index in np.arange(signal_length):
        if index <= ECG_rpeaks[S]:  
            # 当前数据索引小于 sample[********{176}***C----------{S:556677}---------{580971}---------{716110}]
            # 则符号值为        note[********{S-1:N}------------{  AF  }------------{  N  }----------{  AF  }]

            if S-1 < 0:
                C = note[0]
            else:
                C = note[S-1]

        elif index > ECG_rpeaks[S]:
            # 当前数据索引大于 sample[********{176}***********{S:556677}C--------{580971}---------{716110}]

            # 刷新S           sample[********{176}***********{556677}C--------{S:580971}---------{716110}]
            # 则符号值为        note[*********{ N }-----------{S-1:AF}---------{  N  }------------{  AF  }]

            if S+1 >= len(note):
                C = note[len(note) - 1]
            else:
                S = S + 1
                C = note[S-1]

        mate_ann.append(C)
    
    return mate_ann

# 根据采样时间，获取该信号位于的信号坐标点
# 传入：采样时间点 "00:06:45",信号总长度 
# 返回值：该处时间的采样点
# 使用举例：signal_point = CPSC2021.signal_time_sample("00:00:12.955",len(ECG0))
# 作者：刘琦
def signal_time_sample(sample_time, signal_length):
    numbers = sample_time.split(':')
    sample_sec = float(numbers[0])*3600 + float(numbers[1])*60 + float(numbers[2])

    total_sec = int(signal_length/200)  # CPSC数据集的采样率都是 200
    sample_point = int(signal_length*(sample_sec/total_sec))

    return sample_point

# 寻找R_R峰在信号中的位置
# 传入：  被寻找的索引值，一整个信号通道，一整个R峰标注
# 返回值：该索引值右边的R_R峰的片段信号,起点索引,止点索引
# 使用举例：signal, s, e = CPSC2021.find_R_R_peak(signal_point, ECG1, ECG_rpeaks)
# 作者：刘琦
def find_R_R_peak(start, ECG_signal, ECG_rpeaks):

    index = np.searchsorted(ECG_rpeaks, start)  # 数据集标注的R峰不准确，重新再次寻找R峰
    if index > len(ECG_rpeaks)-1:  # 超过最后的值会出现index =  len(list)
        index = len(ECG_rpeaks)-1

    if index == 0:  # 如果是第一个R峰，那就不找前面中点
        s = ECG_rpeaks[index]
        e = int((ECG_rpeaks[index]+ECG_rpeaks[index+1])/2)
    elif index == len(ECG_rpeaks)-1: # 如果是最后一个R峰，那就不找后面中点
        s = int((ECG_rpeaks[index-1]+ECG_rpeaks[index])/2)
        e = ECG_rpeaks[index]
    else:
        s = int((ECG_rpeaks[index-1]+ECG_rpeaks[index])/2)
        e = int((ECG_rpeaks[index]+ECG_rpeaks[index+1])/2)

    return ECG_signal[s:e], s, e

# 寻找 nR 峰在信号中的位置
# 传入：  R峰数量n, 被寻找的索引值起点，一整个信号通道，一整个R峰标注
# 返回值： nR 信号片段，片段信号起点，片段信号终点
# 使用举例：signal, s, e = CPSC2021.find_nR_peak(5, signal_point, ECG1, ECG_rpeaks)
# 作者：刘琦
def find_nR_peak(R_num, start, ECG_signal, ECG_rpeaks):

    index = np.searchsorted(ECG_rpeaks, start)  # 数据集标注的R峰不准确，重新再次寻找R峰
    if index > len(ECG_rpeaks)-1-R_num:  # 超过最后的值会出现index =  len(list)
        index = len(ECG_rpeaks)-1-R_num

    start_signal, start_s, start_e = find_R_R_peak(ECG_rpeaks[index], ECG_signal, ECG_rpeaks)
    end_signal, end_s, end_e = find_R_R_peak(ECG_rpeaks[index+R_num], ECG_signal, ECG_rpeaks)

    s = start_s
    e = end_s

    return ECG_signal[s:e], s, e

# 根据起止点，找到该范围的所有 nR 峰
# 传入：R峰数量n, 采样起点，采样终点，一整个信号通道，一整个R峰标注
# 返回值：一个包含R峰坐标点的二维列表
# 使用举例：
# r_peaks_position = CPSC2021.find_nR_peaks(5, s, e, ECG1, ECG_rpeaks)
# for (s,e) in r_peaks_position: 
#     r_signal = ECG1[s:e]
# 作者：刘琦
def find_nR_peaks(R_num, start, end, ECG_signal, ECG_rpeaks):
    start_index = np.searchsorted(ECG_rpeaks, start)
    end_index = np.searchsorted(ECG_rpeaks, end)

    r_peaks_position = []
    for index in np.arange(start_index, end_index-R_num+1):
        signal, s, e = find_nR_peak(R_num, ECG_rpeaks[index], ECG_signal, ECG_rpeaks)
        r_peaks_position.append([s, e])
    
    return r_peaks_position

# 寻找信号段落在信号中的标签
# 传入：  片段信号起点，片段信号终点，一整个信号伴随列表
# 返回值： 该信号片段所属的类别，1为房颤，0为正常
# 使用举例：label = MIT_BIH_AF.find_signal_label(s, e, ECG_ann)
# 作者：刘琦
def find_signal_label(start, end, ECG_ann):
    label_seg = np.array(ECG_ann[start:end])
    num_1 = len(label_seg[label_seg==1])
    num_0 = len(label_seg[label_seg==0])
    
    # 保留三位有效数字
    ratio = num_1/len(label_seg)

    if ratio > 0.4: label = 1
    else: label = 0

    return label


# 根据将信号重采样长度
# 传入：被重采样的信号，想要重采样的长度
# 返回值：被重采样的信号
# 使用举例：signal3 = resample_signal_length(signal2, 800)
# 作者：刘琦
def resample_signal_length(ori_signal, length):
    import numpy
    from scipy.interpolate import interp1d

    # 创建线性插值函数
    f = interp1d(numpy.arange(0, len(ori_signal)), ori_signal, kind='linear', fill_value="extrapolate")

    # 使用插值函数进行重采样
    new_signal = f(numpy.linspace(0, len(ori_signal), length))

    return new_signal[0:length]

# 利用小波变换对信号进行滤波
# 传入：想要滤波的信号
# 返回值：被滤波的信号
# 使用举例：denoise_signal = wavelet_denoise(ori_signal)
# 作者：刘琦
def wavelet_denoise(signal):
    import pywt

    # 小波变换
    coeffs = pywt.wavedec(data=signal, wavelet='db4', level=9)
    cA9, cD9, cD8, cD7, cD6, cD5, cD4, cD3, cD2, cD1 = coeffs
    # 阈值去噪
    threshold = (np.median(np.abs(cD1)) / 0.6745) * (np.sqrt(2 * np.log(len(cD1))))
    cD1.fill(0)
    cD2.fill(0)
    for i in range(1, len(coeffs) - 2):
        coeffs[i] = pywt.threshold(coeffs[i], threshold)
    # 小波反变换,获取去噪后的信号
    r_signal = pywt.waverec(coeffs=coeffs, wavelet='db4')

    return r_signal

# 对单个信号去趋势
# 传入：  想要去趋势的信号
# 返回值：被去趋势的信号
# 使用举例：detrend_signal = wavelet_denoise(ori_signal)
# 作者：刘琦
def wavelet_detrend(ori_signal):
    import pywt

    coeffs = pywt.wavedec(ori_signal, 'db4', level=4)  # 进行离散小波变换
    coeffs[0] = np.zeros_like(coeffs[0])  # 将趋势分量置零
    signal = pywt.waverec(coeffs, 'db4')  # 重构信号

    return signal

# 将信号转化为频谱信号
# 传入：  信号，保存路径
# 返回值：无返回值，结果在指定路径输出图片
# 使用举例：wavelet_cwt2image(sample_signal, "./wavelet.png")
# 作者：刘琦
def wavelet_cwt2image(signal, filename):
        
    import pywt
    import matplotlib.pyplot as plt
    import numpy as np
    import os
    
    # 去掉文件路径中的最后一个文件名
    folder_path = os.path.dirname(filename)

    # 判断文件夹路径是否存在，若不存在则新建文件夹
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)


    # 选择小波函数，这里使用Morlet小波
    scale = 32
    BandWidthfreq = 8  # 增加 Fb 会导致中心频率周围的能量集中度变窄。
    central_freq = 20  # 越大频率分辨率越高,是因为拉开了频率尺度
    wavelet_name = 'cmor{:1.1f}-{:1.1f}'.format(BandWidthfreq, central_freq)

    cwt_coeffs, freqs = pywt.cwt(signal, np.arange(1, scale), wavelet_name)  # 进行小波变换
    # plt.imshow(np.abs(cwt_coeffs), extent=[0, len(signal), min(freqs), max(freqs)], cmap='jet',
    #         aspect='auto', interpolation='bilinear')
    # plt.axis('off')  # 隐藏坐标轴刻度和标签
    # plt.savefig(filename, bbox_inches='tight', pad_inches=0)  # 保存为PNG格式
    # plt.close()

    # 备用保存方式
    x = np.abs(cwt_coeffs)
    # 归一化到 0-255 范围
    normalized_array = ((x - np.min(x)) * (255 / (np.max(x) - np.min(x)))).astype(np.uint8)
    from PIL import Image
    # 创建PIL图像对象
    image = Image.fromarray(normalized_array)
    # 使用resize方法重新调整图像大小
    image = image.resize((120, 80))       
    # 保存图像到文件
    image.save(filename)

