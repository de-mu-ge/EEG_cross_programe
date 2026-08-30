# ------------ Train -----------
from Cpython.main.EEG.Configs import Config
# from Cpython.mian.dataset.Configs import Config
lrs = Config().lrs
epochs = Config().epochs

# -------------------------------
from matplotlib import pyplot as plt
import numpy as np
# import torch
from torch.utils.data import DataLoader
# from Cpython.mian.dataset.dataset import TrainEegDataset, TestEegDataset
# from Cpython.mian.dataset.DataRead import Play
from Cpython.main.EEG.Dataload.dataset import TrainEegDataset, TestEegDataset
import torch
train_dataset = TrainEegDataset()
test_dataset = TestEegDataset()
train_dataloader = DataLoader(train_dataset, batch_size=32, shuffle=True)
train_dataloader_iter = DataLoader(train_dataset, batch_size=1, shuffle=False)
test_dataloader = DataLoader(test_dataset, batch_size=1, shuffle=False)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# from Cpython.mian.dataset.model import Moudle

from Cpython.main.EEG.src.test.test_model import Model
# from Cpython.main.EEG.model import Moudle
from Cpython.main.EEG.src.test.test_model import DEAPNet
# model = Moudle()
# model = DEAPNet()

model = Model()
model.train()
model.to(device)


class_counts = torch.tensor([
    440,   # class 0
    1068,  # class 1
    844,   # class 2
    828,   # class 3
    800,   # class 4
    452,   # class 5
    292,   # class 6
    268,   # class 7
    108,   # class 8
    20     # class 9
], dtype=torch.float32)

weights = 1.0 / torch.sqrt(class_counts)
weights = weights / weights.mean()
weights = weights.to(device)

optimizer = torch.optim.Adam(model.parameters(), lr=lrs, weight_decay=1e-3)
criterion = torch.nn.CrossEntropyLoss(weight=weights)

# print("模型训练开始")

train_mat = []
test_mat = []

for epoch in range(epochs):

    print("Epoch [{}/{}]".format(epoch + 1, epochs))
    # print("是否有进循环")
    items = []

    for i, (data, labels) in enumerate(train_dataloader):


        # --------------噪声--------------------
        # num = (0.01 * torch.randn([24, 32, 2016])).float().to(device)


        data = data.to(device)

        # --------------添加噪声--------------------
        # data += num

        labels = labels.to(device)

        optimizer.zero_grad()
        outputs = model(data)
        loss = criterion(outputs, labels)
        items.append(loss.item())

        loss.backward()
        optimizer.step()

        # break

    print("loss:", sum(items) / len(items))

    model.eval()

    result = []

    for data in [train_dataloader_iter, test_dataloader]:

        true = 0        # 重新积累
        false = 0
        index = 0

        for i, (inputs, label) in enumerate(data):
            index += 1
            inputs, label = inputs.to(device), label.to(device)

            out = model(inputs)
            out = out.cpu().detach().numpy()
            out = np.argmax(out, axis=1).tolist()[0]

            # print(type(label))
            # print(label)
            label = int(label)
            # print("label的结构 ")
            # print(label)
            # break

            # label = torch.sigmoid(label).cpu().detach().numpy()
            # label = np.argmax(label, axis=1)[0]

            # print(out == label, out, label)

            # if label == out:
            #
            #     true += 1
            # else:
            #     false += 1

            if index % 100 == 0:
                # true = true + 1
                print("")
                print("")
                # print(str(data))
                print(label, out)


            if label == out or label == out + 1 or label == out - 1:
                true += 1
            else:
                false += 1

        result.append(true / index)

    train_mat.append(result[0])
    test_mat.append(result[1])

    print("训练集结果:", result[0])
    print("测试集结果:", result[1])
    print('')
    print('')
    print('')


print(train_mat)
print(test_mat)

plt.plot(train_mat)
plt.plot(test_mat)
plt.show()

