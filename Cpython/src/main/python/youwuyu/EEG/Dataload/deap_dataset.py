from torch.utils.data import Dataset
print("loading dataset")
import torch
from Cpython.src.main.python.youwuyu.EEG.Dataload.DeapDataRead import data_read
play_list = data_read()
print("loading data")
# print("共计",len(Play_list), "个数据")

class TrainEegDataset(Dataset):
    def __init__(self):
        self.data = []
        self.labels = []
        # 按被试划分训练/测试集：每人 40 试次 * 4 段 = 160 条，
        # 前 28 个被试做训练，后 4 个被试（s29~s32）做跨被试测试。
        # 之前按样本序号 0~5000 / 5000: 切分，测试集=最后一个被试的
        # 一部分，模型只需要背训练被试、对没见过的被试直接退化成瞎猜。
        for play in play_list[:28 * 160]:
            self.data.append(torch.tensor(play.data).float())
            # self.labels.append(torch.tensor(play.valence).float())
            self.labels.append(play.valence)

    def __len__(self):
        # print(len(self.data))
        # print(len(self.data))
        return len(self.data)

    def __getitem__(self, idx):
        # print(self.labels[idx])
        return self.data[idx] +  0.01 *  torch.randn([32, 2016]).float()  , self.labels[idx]     # 添加噪声
        return self.data[idx], self.labels[idx]     # 原始EEG噪声最佳0.01
#
# data = EegDataset()
# data.__len__()

class TestEegDataset(Dataset):
    def __init__(self):
        self.data = []
        self.labels = []
        # 后 4 个被试（s29~s32）作为测试集，共 640 条，均为训练时没见过的被试
        for play in play_list[28 * 160:]:
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
