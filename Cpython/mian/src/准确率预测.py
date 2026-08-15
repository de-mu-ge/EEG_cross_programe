from torch.utils.data import DataLoader
from Cpython.mian.dataset.dataset import TrainEegDataset
from Cpython.mian.dataset.dataset import TestEegDataset
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent
import torch
# import json
train_dataset = TrainEegDataset()
test_dataset = TestEegDataset()

train_dataloader = DataLoader(train_dataset, batch_size=1, shuffle=False)
test_dataloader = DataLoader(test_dataset, batch_size=1, shuffle=False)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
from Cpython.mian.dataset.model import Moudle
model = Moudle()
model.eval()
model.to(device)
import numpy as np
model.load_state_dict(torch.load(BASE_DIR / "pt" / "eeg_model.pth"))

# json_list = []
true = 0
false = 0
index = 0
result = []
for data in [train_dataloader, test_dataloader]:
    for i, (inputs, label) in enumerate(data):
        index += 1
        inputs, label = inputs.to(device), label.to(device)

        out = model(inputs)
        out = torch.sigmoid(out).cpu().detach().numpy()
        out = np.argmax(out, axis=1).tolist()[0]

        label = int(label)
        # print("label的结构 ")
        # print(label)
        # break

        # label = torch.sigmoid(label).cpu().detach().numpy()
        # label = np.argmax(label, axis=1)[0]

        print(out == label, out, label)

        if label == out or label == out + 1 or label == out - 1:
            true += 1
        else:
            false += 1

    result.append(true / index)


print("训练集结果:", result[0])
print("测试集结果:", result[1])













    # data= data.to(cude)
    #
    # saml_list = []
    # saml_list.append(i)
    #
    # data = model(data)
    #
    # data = torch.sigmoid(data).cpu().detach().numpy()
    #
    # # print("data")
    # data = np.argmax(data, axis=1)
    # data = str(data.tolist()[0])
    #
    # label = torch.sigmoid(label).cpu().detach().numpy()
    # label = str(np.argmax(label, axis=1)[0])
    # # print(label)
    # saml_list.append(data)
    # saml_list.append(label)
    #
    # json_list.append(saml_list)

    # break

# with open('./predict/predict.json', 'w') as f:
#     json.dump(json_list, f, indent=4)