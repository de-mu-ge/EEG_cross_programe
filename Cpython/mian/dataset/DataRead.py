import pickle
import os
import numpy as np
# import torch
from Cpython.mian.dataset.Configs import Config
dataset_path = Config.dataset_path
cache_path = Config.cache_path

class Play():
    def __init__(self, data, valence, arousal):
        self.data = data
        self.valence = valence
        self.arousal = arousal

def name(x):
    x = int(x)
    if x >= 5:
        return 1
    else:
        return 0

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
                    arousal = 0    # 这里先0
                    # print(valence)
                    # arousal = name(input[1])
                    for j in range(4):
                        play_list.append(Play(data[i][:,j:j+2016], valence, arousal))
                #     pass
                # print(subject['labels'].shape)
                # print(subject['data'].shape)
                #
                # break

        play_list = np.stack(play_list)
        os.makedirs("cache", exist_ok=True)
        np.save(cache_path, play_list, allow_pickle=True)

    return play_list

Play_list = data_read()


if __name__ == "__main__":
    print("40个数据分开装,",
          "40个通道",
          "2016个采集点做兼容",
          "总共5120组数据")

    Play_list = data_read()

    print(len(Play_list))
    print(Play_list[5].data.shape)
    print(Play_list[7].valence)
    print(Play_list[9].arousal)
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
