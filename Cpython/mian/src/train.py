from torch.utils.data import DataLoader
from Cpython.mian.dataset.dataset import EegDataset
# from Cpython.mian.dataset.DataRead import Play
import torch
dataset = EegDataset()
dataloader = DataLoader(dataset, batch_size=32, shuffle=True)

cude = torch.device("cuda" if torch.cuda.is_available() else "cpu")
from Cpython.mian.dataset.model import Moudle
model = Moudle()
model.train()
model.to(cude)

optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
criterion = torch.nn.CrossEntropyLoss()

for epoch in range(10):
    for i, (data, labels) in enumerate(dataloader):
        data = data.to(cude)
        labels = labels.to(cude)

        optimizer.zero_grad()   
        outputs = model(data)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        # break

        if (i + 1) % 10 == 0:
            print(f'Epoch [{epoch + 1}/10], Step [{i + 1}/{len(
                dataloader)}], Loss: {loss.item():.4f}')
torch.save(model.state_dict(), 'pt/eeg_model.pth')
print('Model saved to eeg_model.pth')
    