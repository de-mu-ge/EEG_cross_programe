from torch.utils.data import Dataset
print("loading dataset")
import torch
from Cpython.main.EEG.Dataload.DataRead import data_read
play_list = data_read()
print("loading data")
# print("共计",len(Play_list), "个数据")

class TrainEegDataset(Dataset):
    def __init__(self):
        self.data = []
        self.labels = []
        for play in play_list[5000:]:     # 前5000个点
            self.data.append(torch.tensor(play.data).float())
            # self.labels.append(torch.tensor(play.valence).float())
            self.labels.append(play.valence)

    def __len__(self):
        # print(len(self.data))
        return len(self.data)

    def __getitem__(self, idx):
        # print(self.labels[idx])
        return self.data[idx], self.labels[idx]
        return self.data[idx], self.labels[idx]
#
# data = EegDataset()
# data.__len__()

class TestEegDataset(Dataset):
    def __init__(self):
        self.data = []
        self.labels = []
        for play in play_list[:120]:     # 后 120 个点
            self.data.append(torch.tensor(play.data).float())
            # self.labels.append(torch.tensor(play.valence).float())
            self.labels.append(play.valence)

    def __len__(self):
        # print(len(self.data))
        return len(self.data)

    def __getitem__(self, idx):
        # print(self.labels[idx])
        return self.data[idx], self.labels[idx]

class ValancedDataset(Dataset):
    def __init__(self):
        self.data = []
        self.labels = []
        for play in play_list:     # 前5000个点
            self.data.append(torch.tensor(play.data).float())
            # self.labels.append(torch.tensor(play.valence).float())
            self.labels.append(play.valence)

    def __len__(self):
        # print(len(self.data))
        return len(self.data)

    def __getitem__(self, idx):
        # print(self.labels[idx])
        return self.data[idx], self.labels[idx]

class ArousalDataset(Dataset):
    def __init__(self):
        self.data = []
        self.labels = []
        for play in play_list:     # 前5000个点
            self.data.append(torch.tensor(play.data).float())
            # self.labels.append(torch.tensor(play.valence).float())
            self.labels.append(play.arousal)

    def __len__(self):
        # print(len(self.data))
        return len(self.data)

    def __getitem__(self, idx):
        # print(self.labels[idx])
        return self.data[idx], self.labels[idx]

class DominanceDataset(Dataset):
    def __init__(self):
        self.data = []
        self.labels = []
        for play in play_list:     # 前5000个点
            self.data.append(torch.tensor(play.data).float())
            # self.labels.append(torch.tensor(play.valence).float())
            self.labels.append(play.dominance)

    def __len__(self):
        # print(len(self.data))
        return len(self.data)

    def __getitem__(self, idx):
        # print(self.labels[idx])
        return self.data[idx], self.labels[idx]
