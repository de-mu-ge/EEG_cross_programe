from torch.utils.data import DataLoader
from Cpython.mian.dataset.dataset import EegDataset
import torch
import json
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent     # 路径解析
dataset = EegDataset()
dataloader = DataLoader(dataset, batch_size=1, shuffle=False)

cude = torch.device("cuda" if torch.cuda.is_available() else "cpu")
from Cpython.mian.dataset.model import Moudle
model = Moudle()

model.eval()
model.to(cude)
import numpy as np
model.load_state_dict(torch.load(BASE_DIR /"mod" / "eeg_model.pth"))

json_list = []
for i, (data, label) in enumerate(dataloader):

    data= data.to(cude)

    saml_list = []
    saml_list.append(i)

    data = model(data)

    data = torch.sigmoid(data).cpu().detach().numpy()

    # print("data")
    data = np.argmax(data, axis=1)
    data = str(data.tolist()[0])

    # label = torch.sigmoid(label).cpu().detach().numpy()
    # label = str(np.argmax(label, axis=1)[0])
    # print(label)
    saml_list.append(data)
    saml_list.append(str(int(label)))

    json_list.append(saml_list)

    # break

with open(BASE_DIR / 'output' / 'predict.json', 'w') as f:
    json.dump(json_list, f, indent=4)




