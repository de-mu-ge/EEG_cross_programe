# ------------ Train -----------
from Cpython.main.EEG.Configs import Config
lrs = Config().lrs
epochs = Config().epochs
pth_path = Config().pth_path
# -------------------------------

from torch.utils.data import DataLoader
from Cpython.main.EEG.Dataload.dataset import TrainEegDataset
# from Cpython.mian.dataset.DataRead import Play
import torch
dataset = TrainEegDataset()
dataloader = DataLoader(dataset, batch_size=32, shuffle=True)

cude = torch.device("cuda" if torch.cuda.is_available() else "cpu")
from Cpython.main.EEG.model import Moudle
model = Moudle()
model.train()
model.to(cude)

optimizer = torch.optim.Adam(model.parameters(), lr=lrs)
criterion = torch.nn.CrossEntropyLoss()

print("模型训练开始")

for epoch in range(epochs):

    print("Epoch [{}/{}]".format(epoch + 1, epochs))
    # print("是否有进循环")
    items = []

    for i, (data, labels) in enumerate(dataloader):
        data = data.to(cude)
        labels = labels.to(cude)

        optimizer.zero_grad()   
        outputs = model(data)
        loss = criterion(outputs, labels)
        items.append(loss.item())

        loss.backward()
        optimizer.step()

        # break

    print("loss:", sum(items) / len(items))
        # if (i + 1) % 10 == 0:
            # print(f'Epoch [{epoch + 1}/10], Step [{i + 1}/{len(dataloader)}], Loss: {loss.item():.4f}')
torch.save(model.state_dict(), pth_path)
print('Model saved to eeg_model.pth')
    