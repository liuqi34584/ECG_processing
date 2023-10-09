import numpy as np
import pywt

# 根据采样时间，获取该信号位于的信号坐标点
# 传入：采样时间点 "00:06:45"，信号总时间 "10:13:43",信号总长度 
# 返回值：该处时间的采样点
# 使用举例：signal_point = signal_time_sample("00:00:04.876","10:13:43",len(ECG0))
# 作者：刘琦
def signal_time_sample(sample_time, total_time, signal_length):
    numbers = sample_time.split(':')
    sample_sec = float(numbers[0])*3600 + float(numbers[1])*60 + float(numbers[2])
    numbers = total_time.split(':')
    total_sec = float(numbers[0])*3600 + float(numbers[1])*60 + float(numbers[2])
    sample_point = int(signal_length*(sample_sec/total_sec))

    return sample_point

# 寻找R_R峰在信号中的位置
# 传入：  被寻找的索引值，一整个信号通道，一整个R峰标注
# 返回值：该索引值右边的R_R峰的片段信号,起点索引,止点索引
# 使用举例：signal, s, e = find_R_R_peak(58484, ECG0, ECG_rpeaks)
# 作者：刘琦
def find_R_R_peak(start, ECG_signal, ECG_rpeaks):
    index = np.searchsorted(ECG_rpeaks, start)  # 这个R峰不准确，重新再次寻找R峰
    s0, e0= ECG_rpeaks[index-1]-20, ECG_rpeaks[index-1]+20
    R_peak0 = np.argmax(ECG_signal[s0:e0])

    s1, e1= ECG_rpeaks[index]-20, ECG_rpeaks[index]+20
    R_peak1 = np.argmax(ECG_signal[s1:e1])

    s2, e2= ECG_rpeaks[index+1]-20, ECG_rpeaks[index+1]+20
    R_peak2 = np.argmax(ECG_signal[s2:e2])

    s = int((s0+s1+R_peak0+R_peak1)/2)
    e = int((s1+s2+R_peak1+R_peak2)/2)
    # e = R_peak1 + 10 + s1

    return ECG_signal[s:e], s, e

# 对单个R_R峰去趋势
# 传入：被寻找的索引值，一整个信号单通道，一整个R峰标注
# 返回值：该索引值右边的R_R峰的片段信号
# 作者：刘琦
# 使用举例：signal2 = R_R_detrend(signal_point, ECG0, ECG_rpeaks, long_detrend=True)
def R_R_detrend(start, ECG_signal, ECG_rpeaks, long_detrend=False):
    signal, s, e  = find_R_R_peak(start, ECG_signal, ECG_rpeaks)

    if long_detrend:
        long_s = s-1000
        long_e = e+1000
        if long_s < 0:
            long_signal = ECG_signal[0:2000]
            coeffs = pywt.wavedec(long_signal, 'db6', level=6)  # 进行离散小波变换
            coeffs[0] = np.zeros_like(coeffs[0])  # 将趋势分量置零
            long_signal = pywt.waverec(coeffs, 'db6')  # 重构信号
            ECG_signal[0:len(long_signal)] = long_signal
            signal = ECG_signal[s:e]
        elif long_e > len(ECG_signal):
            long_signal = ECG_signal[-2000:]
            coeffs = pywt.wavedec(long_signal, 'db6', level=6)  # 进行离散小波变换
            coeffs[0] = np.zeros_like(coeffs[0])  # 将趋势分量置零
            long_signal = pywt.waverec(coeffs, 'db6')  # 重构信号
            ECG_signal[-len(long_signal):] = long_signal
            signal = ECG_signal[s:e]
        else:
            long_signal = ECG_signal[long_s:long_e]
            coeffs = pywt.wavedec(long_signal, 'db6', level=6)  # 进行离散小波变换
            coeffs[0] = np.zeros_like(coeffs[0])  # 将趋势分量置零
            long_signal = pywt.waverec(coeffs, 'db6')  # 重构信号
            ECG_signal[long_s:long_s + len(long_signal)] = long_signal
            signal = ECG_signal[s:e]

    coeffs = pywt.wavedec(signal, 'db4', level=4)  # 进行离散小波变换
    coeffs[0] = np.zeros_like(coeffs[0])  # 将趋势分量置零
    coeffs[3] = np.zeros_like(coeffs[3])  # 将趋势分量置零
    coeffs[4] = np.zeros_like(coeffs[4])  # 将趋势分量置零
    signal = pywt.waverec(coeffs, 'db4')  # 重构信号

    return signal


# 寻找R_R_R_R_R峰在信号中的位置
# 传入：  被寻找的索引值，一整个信号通道，一整个R峰标注
# 返回值：该索引值右边的R_R_R_R_R峰的片段信号
# 使用举例：signal = find_R_R_R_R_R_peak(58484, ECG0, ECG_rpeaks)
# 作者：刘琦
def find_R_R_R_R_R_peak(start, ECG_signal, ECG_rpeaks):
    index = np.searchsorted(ECG_rpeaks, start)  # 这个R峰不准确，重新再次寻找R峰
    s1, e1= ECG_rpeaks[index]-20, ECG_rpeaks[index]+20
    R_peak1 = np.argmax(ECG_signal[s1:e1])

    s2, e2= ECG_rpeaks[index+4]-20, ECG_rpeaks[index+4]+20
    R_peak2 = np.argmax(ECG_signal[s2:e2])

    return ECG_signal[R_peak1+s1-10:R_peak2+s2+10]

# 对单个R_R_R_R_R峰去趋势
# 传入：  被寻找的索引值，一整个信号单通道，一整个R峰标注
# 返回值：该索引值右边的R_R_R_R_R峰的片段信号
# 作者：刘琦
def R_R_R_R_R_detrend(start, ECG_signal, ECG_rpeaks):
    signal = find_R_R_R_R_R_peak(start, ECG_signal, ECG_rpeaks)

    coeffs = pywt.wavedec(signal, 'db4', level=4)  # 进行离散小波变换
    coeffs[0] = np.zeros_like(coeffs[0])  # 将趋势分量置零
    signal = pywt.waverec(coeffs, 'db4')  # 重构信号

    return signal


# 创建一个关于信号的伴随列表，此函数废时间，920万信号处理两秒
# 传入：信号长度，标记采样点数组，标记符号数组
# 传出： 一个信号同样长度的标注列表
# 使用举例：ECG_ann = AFDB_create_mate_ann(len(ECG0), ann_sample, ann_aux_note)
# 此方法只适用于 AFDB 数据集的标注样式
# 作者：刘琦
def AFDB_create_mate_ann(signal_length, sample, aux_note):

    # 首先，重刷标记数组,使得列表仅为两种符号 '(AFIB'-1, '(N'-0。最后保存到 note 列表中
    note = []
    current_ann = '(N'
    for ann in aux_note:

        if ann == '(N':
            current_ann = 0
        if ann == '(AFIB':
            current_ann = 1

        note.append(current_ann)

    # 其次，定义一个关于数据的伴随注释列表数据,这个循环的核心目的是为当前的索引位置找到应该属于的类型
    # 当前的数据索引类型，应该等于采样列表左边的值
    C, S = 0, 0  
    mate_ann = []

    for index in np.arange(signal_length):
        if index <= sample[S]:  
            # 当前数据索引小于 sample[********{176}***C----------{S:556677}---------{580971}---------{716110}]
            # 则符号值为        note[********{S-1:N}------------{  AF  }------------{  N  }----------{  AF  }]

            if S-1 < 0:
                C = 1-note[0]
            else:
                C = note[S-1]

        elif index > sample[S]:
            # 当前数据索引大于 sample[********{176}***********{S:556677}C--------{580971}---------{716110}]

            # 刷新S           sample[********{176}***********{556677}C--------{S:580971}---------{716110}]
            # 则符号值为        note[*********{ N }-----------{S-1:AF}---------{  N  }------------{  AF  }]

            if S+1 >= len(sample):
                C = note[len(sample) - 1]
            else:
                S = S + 1
                C = note[S-1]

        mate_ann.append(C)
    
    return mate_ann

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
    # 小波变换
    coeffs = pywt.wavedec(data=signal, wavelet='db5', level=9)
    cA9, cD9, cD8, cD7, cD6, cD5, cD4, cD3, cD2, cD1 = coeffs
    # 阈值去噪
    threshold = (np.median(np.abs(cD1)) / 0.6745) * (np.sqrt(2 * np.log(len(cD1))))
    cD1.fill(0)
    cD2.fill(0)
    for i in range(1, len(coeffs) - 2):
        coeffs[i] = pywt.threshold(coeffs[i], threshold)
    # 小波反变换,获取去噪后的信号
    r_signal = pywt.waverec(coeffs=coeffs, wavelet='db5')

    return r_signal

# 根据时间点，截取一个片段波形
# 传入：采样时间点，采样总时间，原信号，被采样长度，信号对齐方式
# 返回值：被采样起点，被采样终点，信号
# 使用举例：start, end, sample_signal = fragment_signal("00:07:59.051", "10:13:43", 1000, ECG0, alignment="right")
# 作者：刘琦
def fragment_signal(sample_time, total_time, sample_length, ECG_signal, alignment="center"):

    signal_length = len(ECG_signal)
    numbers = sample_time.split(':')
    sample_sec = float(numbers[0])*3600 + float(numbers[1])*60 + float(numbers[2])
    numbers = total_time.split(':')
    total_sec = float(numbers[0])*3600 + float(numbers[1])*60 + float(numbers[2])
    sample_point = int(signal_length*(sample_sec/total_sec))

    if alignment == "right": # 右对齐采样
        start = sample_point
        end = sample_point + sample_length
    elif alignment == "left": # 左对齐采样
        start = sample_point - sample_length
        end = sample_point
    else: # 居中采样 alignment == "center"
        start = sample_point - int(sample_length/2)
        end = sample_point + int(sample_length/2)
    
    if start < 0:
        start = 0
    if end > len(ECG_signal)-1:
        end = len(ECG_signal)-1

    sample_signal = ECG_signal[start:end]

    return start, end, sample_signal

# 根据起止点，找到该范围的所有 R 峰
# 传入：采样起点，采样终点，一整个信号通道，一整个R峰标注
# 返回值：一个包含R峰坐标点的二维列表
# 使用举例：
# r_peaks_position = find_R_R_peaks(start, end, ECG0, ECG_rpeaks)
# for i in r_peaks_position: 
#     r_signal = ECG0[i[0]:i[1]]
# 作者：刘琦
def find_R_R_peaks(start, end, ECG_signal, ECG_rpeaks):
    start_index = np.searchsorted(ECG_rpeaks, start)
    end_index = np.searchsorted(ECG_rpeaks, end)
    r_peaks_position = []

    for index in np.arange(start_index, end_index+1):
        signal, s, e = find_R_R_peak(ECG_rpeaks[index], ECG_signal, ECG_rpeaks)
        r_peaks_position.append([s, e])
    
    return r_peaks_position
