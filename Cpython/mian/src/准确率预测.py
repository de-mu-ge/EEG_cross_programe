from unittest import result

from torch.nn.utils import remove_weight_norm
from torch.utils.data import DataLoader
from Cpython.mian.dataset.dataset import EegDataset
import torch
# import json
dataset = EegDataset()
dataloader = DataLoader(dataset, batch_size=1, shuffle=False)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
from Cpython.mian.dataset.model import Moudle
model = Moudle()
model.eval()
model.to(device)
import numpy as np
model.load_state_dict(torch.load("./pt/eeg_model.pth"))

# json_list = []
true = 0
false = 0
result = 0
for i, (data, label) in enumerate(dataloader):
    result += 1
    data, label = data.to(device), label.to(device)

    out = model(data)
    out = torch.sigmoid(out).cpu().detach().numpy()
    out = np.argmax(out, axis=1).tolist()[0]

    label = int(label)
    # print("label的结构 ")
    # print(label)
    # break

    # label = torch.sigmoid(label).cpu().detach().numpy()
    # label = np.argmax(label, axis=1)[0]

    if label == out:
        true += 1
    else:
        false += 1

print("准确率:", true / result)












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