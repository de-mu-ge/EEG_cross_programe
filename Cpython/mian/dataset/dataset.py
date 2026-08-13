from torch.utils.data import Dataset
print("loading dataset")
import torch
from Cpython.mian.dataset.DataRead import Play_list
print("loading data")
print("共计",len(Play_list), "个数据")


class EegDataset(Dataset):
    def __init__(self):
        self.data = []
        self.labels = []
        for play in Play_list:
            self.data.append(torch.tensor(play.data).float())
            self.labels.append(torch.tensor(play.label).float())

    def __len__(self):
        # print(len(self.data))
        return len(self.data)

    def __getitem__(self, idx):
        return self.data[idx], self.labels[idx]
#
# data = EegDataset()
# data.__len__()