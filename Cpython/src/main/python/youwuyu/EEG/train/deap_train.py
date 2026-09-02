# ------------ Train -----------
from Cpython.src.main.python.youwuyu.EEG.configs.Configs import Config
lrs = Config().lrs
epochs = Config().epochs
eeg_pth_path = Config().deap_eeg_pth_path
pth_path = eeg_pth_path
# -------------------------------

from torch.utils.data import DataLoader
from Cpython.src.main.python.youwuyu.EEG.Dataload.deap_dataset import ValancedDataset, DominanceDataset, ArousalDataset
# from Cpython.mian.dataset.DataRead import Play
import torch
valance_dataset = DominanceDataset()
arousal_dataset = ArousalDataset()
dominance_dataset = ValancedDataset()

valance_laoder = DataLoader(valance_dataset, batch_size=32, shuffle=True)
arousal_laoder = DataLoader(arousal_dataset, batch_size=32, shuffle=True)
dominance_laoder = DataLoader(dominance_dataset, batch_size=32, shuffle=True)

cude = torch.device("cuda" if torch.cuda.is_available() else "cpu")
from Cpython.src.main.python.youwuyu.EEG.model.model import Moudle

def train(dataloader, model, index):
    model.train()
    # for epoch in range(epochs):
    model = Moudle()
    model.train()
    model.to(cude)

    optimizer = torch.optim.Adam(model.parameters(), lr=lrs)
    criterion = torch.nn.CrossEntropyLoss()

    print(index, "模型训练开始")

    for epoch in range(epochs):

        print("Epoch [{}/{}]".format(epoch + 1, epochs))
        # print("是否有进循环")
        items = []

        for i, (data, labels) in enumerate(dataloader):
            data = data.to(cude)
            # labels = torch.tensor(labels).to(cude)
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
    torch.save(model.state_dict(), pth_path + "/" + index + ".pth")
    print('Model saved to eeg_model.pth')

data_list  = [valance_laoder, arousal_laoder, dominance_laoder]
for index in range(len(data_list)):
    model = Moudle()
    train(data_list[index], model, str(index))
    print(pth_path + "/" + str(index) + ".pth")