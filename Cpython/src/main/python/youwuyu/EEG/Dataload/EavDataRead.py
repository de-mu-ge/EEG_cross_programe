# 数据结构 (30, 2000)   做交叉

# import pickle
from scipy.io import loadmat
import os
import numpy as np
# import torch
from Cpython.src.main.python.youwuyu.EEG.configs.Configs import Config
dataset_path = Config.eav_dataset_path
cache_path = Config.eav_eeg_cache_path

class EavPlay:
    def __init__(self, data, valence):
        self.data = data
        self.valence = valence

def get_negative_label(label):
    """
    0 = 消极
    1 = 积极

    消极：
    2 = 愤怒（听）
    3 = 愤怒（说）
    6 = 悲伤（听）
    7 = 悲伤（说）
    """
    label = np.argmax(label, axis=-1)
    if label in [2, 3, 6, 7]:
        return 0    # 消极
    else:
        return 1    # 积极

def data_read():
    if os.path.exists(cache_path):
          play_list = np.load(cache_path, allow_pickle=True)
    else:
        play_list = []

        data_list = []
        # label_list = []
        list_dir = os.listdir(dataset_path)
        for dirs in list_dir:
            if dirs == "GitHub_Codes":
                continue
            # print(dirs)
            for eeg in os.listdir(os.path.join(dataset_path, dirs, 'EEG')):
                data_list.append(os.path.join(dataset_path, dirs, 'EEG', eeg))

        valance_list = data_list[0::2]
        label_list = data_list[1::2]

        for i in range(len(valance_list)):

            print("数据处理", i + 1, "/ 42")

            valance = loadmat(valance_list[i])
            print("数据提取")
            # 部分文件的变量名是 seg,部分是 seg1
            valance = valance['seg'] if 'seg' in valance else valance['seg1']
            valance = valance.transpose(-1, 0, 1)
            print("数据提取完毕")

            label = loadmat(label_list[i])
            label = label['label'].transpose(-1, 0)

            # print(valance.shape)
            # print(label.shape)

            for _ in range(200):        # 200个样本
                # print("进入200分割循环")
                valance_data = valance[_]
                label_data = get_negative_label(label[_])
                for j in range(5):      # 一段数据切成五分
                    play_list.append(EavPlay(valance_data[2000 * j: 2000 * (j + 1)], label_data))

        play_list = np.stack(play_list)
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        np.save(cache_path, play_list, allow_pickle=True)

    return play_list



if __name__ == '__main__':
    Play_list = data_read()
    print(len(Play_list))



