# ------------ Train -----------
from Cpython.mian.dataset.Configs import Config
lrs = Config().lrs
epochs = Config().epochs
# -------------------------------

from torch.utils.data import DataLoader
from Cpython.mian.dataset.dataset import TrainEegDataset
# from Cpython.mian.dataset.DataRead import Play
import torch
dataset = TrainEegDataset()
dataloader = DataLoader(dataset, batch_size=32, shuffle=True)

cude = torch.device("cuda" if torch.cuda.is_available() else "cpu")
from Cpython.mian.dataset.model import Moudle
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
torch.save(model.state_dict(), 'pt/eeg_model.pth')
print('Model saved to eeg_model.pth')
    