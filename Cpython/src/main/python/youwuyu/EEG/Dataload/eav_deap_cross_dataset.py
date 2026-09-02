from torch.utils.data import Dataset
print("loading dataset")
import torch

from Cpython.src.main.python.youwuyu.EEG.Dataload.DeapDataRead import cross_deap_read
from Cpython.src.main.python.youwuyu.EEG.Dataload.EavDataRead import data_read

# print(cross_deap_read().shape)
# print(data_read().shape)
print("loading data")

class CrossDeapEavDataset(Dataset):
    def __init__(self):
        # self.data = torch.tensor(data_read() + cross_deap_read()).float()
        self.data = (data_read().tolist() + cross_deap_read().tolist())

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        return torch.tensor(self.data[idx].data).float(), self.data[idx].valence


if __name__ == "__main__":
    from torch.utils.data import DataLoader
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    dataset = CrossDeapEavDataset()
    dataloader = DataLoader(dataset=dataset, batch_size=100, shuffle=True, num_workers=0)
    print(len(dataloader))
    for idx, (data, label) in enumerate(dataloader):
        data, label = data.to(device), label.to(device)
        if idx %50 == 0:
            print(data.shape, label.shape)
    # 数据加载通过











