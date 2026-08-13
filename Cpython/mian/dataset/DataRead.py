import pickle
import os
import numpy as np
# import torch
from Cpython.mian.dataset.Configs import Config
dataset_path = Config.dataset_path
cache_path = Config.cache_path

class Play:
    def __init__(self, data, label):
        self.data = data
        self.label = label

def data_read():
    if os.path.exists(cache_path):
          play_list = np.load(cache_path, allow_pickle=True)
    else:
        play_list = []
        list_dir = os.listdir(dataset_path)
        for dirs in list_dir:
            os_dir = os.path.join(dataset_path, dirs)
            with open(os_dir, "rb") as f:
                subject = pickle.load(f, encoding="latin1")
                label = subject['labels']
                data = subject['data']
                # print(type(data))   # <class 'numpy.ndarray'>
                for i in range(40):
                    for j in range(4):
                        play_list.append(Play(data[i][:,j:j+2016], label[i]))
                #     pass
                # print(subject['labels'].shape)
                # print(subject['data'].shape)
                #
                # break

        play_list = np.stack(play_list)
        os.makedirs("cache", exist_ok=True)
        np.save(cache_path, Play_list, allow_pickle=True)

    return play_list

Play_list = data_read()

if __name__ == "__main__":
    print("40个数据分开装,",
          "40个通道",
          "2016个采集点做兼容",
          "总共5120组数据")

# print(len(Play_list))
# print(Play_list[5].data.shape)
# print(Play_list[5].label.shape)

# i = 1
# with open('data_preprocessed_python/s'+ '01' + '.dat', 'rb') as file:
#   subject = pickle.load(file, encoding='latin1')

