# 数据结构 (32, 2016)
import pickle
import os
import numpy as np
# import torch
from Cpython.src.main.python.youwuyu.EEG.configs.Configs import Config
dataset_path = Config.deap_dataset_path
cache_path = Config.deap_eeg_cache_path
cross_cache_path = Config.cross_deap_cache_path

class DeapPlay:
    def __init__(self, data, valence, arousal, dominance):
        self.data = data
        self.valence = valence
        self.arousal = arousal
        self.dominance = dominance


# def name(x):
#     x = int(x)
#     if x >= 5:
#         return 1
#     else:
#         return 0

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
                # print(label)
                # valence = subject['valence']
                # print(label.shape)
                # break
                data = subject['data'][:,:32]    # 前32个电极为脑电数据                # print(type(data))   # <class 'numpy.ndarray'>
                for i in range(40):
                    # print(type(label[i]))
                    input = label[i].tolist()

                    # print("start")
                    # print(input)
                    # print(input[0])
                    # print(type(input[0]))
                    # print("end")
                    # break

                    valence = int(input[0])
                    arousal = int(input[1])
                    dominance = int(input[2])
                    # print(valence)
                    # arousal = name(input[1])
                    for j in range(4):
                        # 8064 个采样点切成 4 段互不重叠的 2016 点。
                        # 之前写成 j:j+2016，4 段只平移 1 个点，几乎完全相同，
                        # 等于把每个试次复制了 4 份，训练精度全靠背数据。
                        play_list.append(DeapPlay(data[i][:, j*2016:(j+1)*2016], valence, arousal, dominance))
                #     pass
                # print(subject['labels'].shape)
                # print(subject['data'].shape)
                #
                # break

        play_list = np.stack(play_list)
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        np.save(cache_path, play_list, allow_pickle=True)

    return play_list

# Play_list = data_read()

class CrossDeapPlay:
    def __init__(self, data, valence):
        self.data = data
        self.valence = valence

def cross_deap_read():
    if os.path.exists(cross_cache_path):
          play_list = np.load(cross_cache_path, allow_pickle=True)
    else:
        play_list = []
        list_dir = os.listdir(dataset_path)
        for dirs in list_dir:
            os_dir = os.path.join(dataset_path, dirs)
            with open(os_dir, "rb") as f:
                subject = pickle.load(f, encoding="latin1")
                label = subject['labels']
                # print(label)
                # valence = subject['valence']
                # print(label.shape)
                # break
                data = subject['data'][:,:30]    # 前32个电极为脑电数据                # print(type(data))   # <class 'numpy.ndarray'>
                for i in range(40):
                    # print(type(label[i]))
                    input = label[i].tolist()

                    valence = 0 if int(input[0]) <= 5 else 1

                    for j in range(4):
                        # 8064 个采样点切成 4 段互不重叠的 2016 点。
                        # 之前写成 j:j+2016，4 段只平移 1 个点，几乎完全相同，
                        # 等于把每个试次复制了 4 份，训练精度全靠背数据。
                        play_list.append(CrossDeapPlay(data[i][:, j*2000:(j+1)*2000].transpose(-1, 0), valence))
                #     pass
                # print(subject['labels'].shape)
                # print(subject['data'].shape)
                #
                # break

        play_list = np.stack(play_list)
        os.makedirs(os.path.dirname(cross_cache_path), exist_ok=True)
        np.save(cross_cache_path, play_list, allow_pickle=True)

    return play_list



if __name__ == "__main__":
    print("40个数据分开装,",
          "40个通道",
          "2016个采集点做兼容",
          "总共5120组数据")

    Play_list = data_read()

    print(len(Play_list))       # 5120
    # print(Play_list[19].data.shape)
    # print(Play_list[412].valence)
    # print(Play_list[9].arousal)
    # print(Play_list[10].dominance)

    labels = []
    for index in Play_list:
        labels.append(index.valence)

    print(labels)






    #
    # # i = 1
    # with open('data_preprocessed_python/s'+ '01' + '.dat', 'rb') as file:
    #   subject = pickle.load(file, encoding='latin1')
"""
  1. Valence 效价（愉悦度）

  你感觉这个视频是"正面"还是"负面"。
  - 1 = 非常不愉快（恶心、痛苦）
  - 9 = 非常愉快（开心、兴奋）
  - 中间 5 ≈ 无所谓/中性

  2. Arousal 唤醒度（激活程度）

  你有多兴奋/被激起来。 跟情绪正负无关，只跟"强烈程度"有关。
  - 1 = 完全平静、昏昏欲睡、放松
  - 9 = 非常激动、紧张、心跳加速
  - 例：很安静的悲伤音乐 = 低效价 + 低唤醒；恐怖片 = 高效价正负不确定 + 高唤醒

  3. Dominance 支配度（控制感）

  你在看视频时觉得自己"掌控局面"还是"被控制/受支配"。
  - 1 = 完全被牵着走、无力、被压迫
  - 9 = 完全掌控、强势
  - 例：惊悚片往往唤起低支配感（无力感），激励类视频高支配感

  4. Liking 喜好度（喜爱程度）

  你有多喜欢这个视频本身。 DEAP 专门加的，不是标准的情绪维度。
  - 1 = 完全不喜欢，9 = 非常喜欢

"""
