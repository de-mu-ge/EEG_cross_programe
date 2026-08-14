import torch
# import argparse
import sys
import numpy as np
import os
import json
import pickle
# from Cpython.mian.dataset.DataRead import Play
from torch.utils.data import Dataset, DataLoader
class Play:
    def __init__(self, data, valence, arousal):
        self.data = data
        self.valence = valence
        self.arousal = arousal
# from Cpython.mian.dataset.model import Moudle
# import torch
import torch.nn as nn

# 数据输入格式是 (B, 40, 2016)
class Moudle(nn.Module):
    def __init__(self):
        super().__init__()

        self.liner1 = nn.Linear(2016, 1)
        self.pool = nn.Flatten()
        self.liner2 = nn.Linear(32, 2)
    def forward(self, x):
        x = self.liner1(x)
        # print(x.shape)
        x = self.pool(x)
        # print(x.shape)
        x = self.liner2(x)
        return x

path = sys.argv[1]    # 传入路径
# path = input("Please enter the path of the file: ")

def data_read(dataset_path):
    play_list = []
    list_dir = os.listdir(dataset_path)
    for dirs in list_dir:
        os_dir = os.path.join(dataset_path, dirs)
        with open(os_dir, "rb") as f:
            subject = pickle.load(f, encoding="latin1")
            # label = subject['labels']
            data = subject['data']
            data = data[:, :32]
            # print(type(data))   # <class 'numpy.ndarray'>
            for i in range(40):
                for j in range(4):
                    play_list.append(Play(data[i][:,j:j+2016], 0, 0))
    return play_list

Play_list = data_read(path)

class EegDataset(Dataset):
    def __init__(self):
        self.data = []
        self.labels = []
        for play in Play_list:
            self.data.append(torch.tensor(play.data).float())
            self.labels.append(play.valence)
            # self.labels.append(torch.tensor(play.label).float())

    def __len__(self):
        # print(len(self.data))
        return len(self.data)

    def __getitem__(self, idx):
        return self.data[idx], self.labels[idx]

dataset = EegDataset()
dataloader = DataLoader(dataset, batch_size=1, shuffle=False)

model = Moudle()
model.load_state_dict(torch.load(r"C:\Users\home and dream\Desktop\ing\EEG\Cpython\mian\src\test\eeg_model.pth"))
model.eval()

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model.to(device)

for i, (data, lable) in enumerate(dataloader):
    data = data.to(device)
    out = model(data)
    out = torch.sigmoid(out).cpu().detach().numpy()

    # print("data")
    out = np.argmax(out, axis=1)
    out = str(out.tolist()[0])

out = list(map(str, out))
with open(r"C:\Users\home and dream\Desktop\ing\EEG\Cpython\mian\src\test\out.json", 'w') as f:
    # print(out, file=f)
    json.dump(out, f, indent=4)

print("程序完成")

