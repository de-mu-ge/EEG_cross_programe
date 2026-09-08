import torch
import torch.nn as nn
from torch.utils.data import DataLoader
# -------------------Config-------------------
from Cpython.src.main.python.youwuyu.EEG.configs.Configs import Config
lrs = Config().lrs
# epochs = Config().epochs
epochs = 5
cross_deap_eav_pth_path = Config().cross_deap_eav_pth_path

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
from Cpython.src.main.python.youwuyu.EEG.model.transformer_deap_eav_cross_model import EEGModel
model = EEGModel()
model = model.to(device)

criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=lrs)

from Cpython.src.main.python.youwuyu.EEG.Dataload.eav_deap_cross_dataset import CrossDeapEavDataset
# dataset = CrossDeapEavDataset()
data_loader = DataLoader(CrossDeapEavDataset(), batch_size=64, shuffle=True)

# -------------train-----------------
for epoch in range(epochs):
    loss_item = 0
    length = len(data_loader)
    for batch_idx, (data, target) in enumerate(data_loader):
        data, target = data.to(device), target.to(device)
        optimizer.zero_grad()
        output = model(data)
        loss = criterion(output, target)
        loss.backward()
        optimizer.step()

        loss_item += loss.item()

    print(epoch, "loss:", loss_item/length)

torch.save(model.state_dict(), cross_deap_eav_pth_path)


