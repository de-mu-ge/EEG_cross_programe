import os
import random
import torch

from Cpython.src.main.python.youwuyu.Video.model.model import VideoModel
model = VideoModel()
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
model.train()
criterion = torch.nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr = 0.0001)

from torch.utils.data import Dataset, DataLoader
import cv2
import numpy as np
# import scipy.io as sio
from Cpython.src.main.python.youwuyu.Video.configs.Configs import Config
eav_dataset_path = Config.eav_dataset_path
# eav_cache_path = Config.eav_cache_path



# class Play:
#     def __init__(self, eeg_data,
#                  video_data,
#                  audio_data,
#                  valance):
#
#         self.eeg_data = eeg_data
#         self.video_data = video_data
#         self.audio_data = audio_data
#         self.valance = valance

class Play: # 为了减少使用内存，先这样训练
    def __init__(self, valance, video):
        self.valance = valance
        self.video = video

class DataSet(Dataset):
    def __init__(self, datas):
        self.datas = datas
    def __len__(self):
        return len(self.datas)
    def __getitem__(self, item):
        return self.datas[item].video, self.datas[item].valance

path_list = []
for m in os.listdir(eav_dataset_path):    # 打开 subject 文件夹
    if m == "GitHub_Codes":
        continue
    # people_list = []
    # for n in os.listdir(os.path.join(eav_dataset_path, m)):    # 打开个人文件夹
    for n in os.listdir(os.path.join(eav_dataset_path, m, 'Video')):
        # people_list.append(n)
        path_list.append(os.path.join(eav_dataset_path, m, 'Video', n))

# print(len(path_list))         # 8400
random.shuffle(path_list)
# input_list = []
# for o in range(200):
#     for i in path_list:
#         input_list.append(i[o])

def add_label(strs):
    if strs[-9] == 'A' or strs[-9] == 'S':
        return 1    # 表示消极情绪
    else:
        return 0    # 表示非消极情绪



# -------------- 一站式推理 -------------------

# for i in range(340):   # 8400
for i in range(10):
    play_list = []

    num = 6
    inputs = path_list[i*num:(i+1)*num]
    for j in inputs:
        # print(type(j))
        # print(j)

        valance = add_label(j)
        cap = cv2.VideoCapture(j)

        for a in range(10):

            # video_array = np.zeros([60,])
            video_array = np.zeros(
                (60, 480, 640, 3),
                dtype=np.uint8
            )
            for b in range(60):
                ret, frame = cap.read()     # 迭代取出
                if not ret:
                    break

                frame = np.array(frame)
                # print(frame.shape)

                video_array[b] = frame

            video_array = torch.from_numpy(video_array).float()
            play_list.append(Play(valance, video_array))

        cap.release()

    # --------------------------------------------------------
    dataset = DataSet(play_list)
    dataloader = DataLoader(dataset, batch_size=16, shuffle=True)
    # dataset = None

    print("这是第几次训练:", i + 1)
    for index, (data, label) in enumerate(dataloader):
        data = data.to(device)
        label = label.to(device)
        optimizer.zero_grad()
        out = model(data)
        loss = criterion(out, label)
        loss.backward()
        optimizer.step()


        print(index, "批次", loss.item())

    print("训练完成")
    print("")
    print("")
    print("")

torch.save(model.state_dict(), r"C:\Users\home and dream\Desktop\ing\EEG\Cpython\main\Video\out\pth\model.pth")




































