from torch.utils.data import Dataset
print("loading dataset")
import torch

from Cpython.src.main.python.youwuyu.EEG.Dataload.DeapDataRead import cross_deap_read
from Cpython.src.main.python.youwuyu.EEG.Dataload.EavDataRead import data_read

# print(cross_deap_read().shape)
# print(data_read().shape)
print("loading data")

class CrossDeapEavDataset(Dataset):     # 训练数据
    def __init__(self):
        # self.data = torch.tensor(data_read() + cross_deap_read()).float()
        self.data = (data_read().tolist() + cross_deap_read().tolist()[160 * 3:])   # 将这里修订（找到测试集比训练集强的原因）

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        return torch.tensor(self.data[idx].data).float(), self.data[idx].valence

class TextCrossDeapEavDataset(Dataset):         # 测试数据
    def __init__(self):
        # self.data = torch.tensor(data_read() + cross_deap_read()).float()
        self.data = cross_deap_read().tolist()[:160 * 3]     # 使用deap数据集前120个数据

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        return torch.tensor(self.data[idx].data).float(), self.data[idx].valence

class TrainExamCrossDeapEavDataset(Dataset):        # 训练集检验数据
    def __init__(self):
        # self.data = torch.tensor(data_read() + cross_deap_read()).float()
        self.data =  cross_deap_read().tolist()[160 * 3 :]     # 使用deap数据集(120：)个数据

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        return torch.tensor(self.data[idx].data).float(), self.data[idx].valence


if __name__ == "__main__":
    print(CrossDeapEavDataset().__len__())
    print(TrainExamCrossDeapEavDataset().__len__())
    print(TextCrossDeapEavDataset().__len__())











