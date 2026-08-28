# 1920 * 1080 * 30
# 60 * 480 * 640


import torch
# from torch.utils.data import Dataset, DataLoader
import torch.nn as nn
import cv2
# import io
import os
import tempfile
import numpy as np
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent

# class VideoDataset(Dataset):
#     def __init__(self, array):
#         self.array = array
#
#     def __len__(self):
#
#
#     def __getitem__(self, idx):
#         pass


# dataset = VideoDataset()
# dataloader = DataLoader(dataset, batch_size=1, shuffle=False)

class VideoModel(nn.Module):
    def __init__(self):
        super().__init__()

        self.conv1 = nn.Conv3d(3, 6, 3, 3)
        self.dropout1 = nn.Dropout3d(0.1)
        self.relu1 = nn.ReLU()

        self.conv2 = nn.Conv3d(6, 2, 3, 2)
        self.dropout2 = nn.Dropout3d(0.1)
        self.minimax = nn.BatchNorm3d(2)
        self.relu2 = nn.ReLU()

        # self.conv3 = nn.Conv3d(16, 4, 3, 1)
        # self.dropout3 = nn.Dropout2d(0.1)
        # self.relu3 = nn.ReLU()

        # self.conv4 = nn.Conv3d(2, 1, 6, 3)
        # self.dropout4 = nn.Dropout3d(0.1)
        # self.relu4 = nn.ReLU()

        self.pool = nn.MaxPool3d(2, 8)
        self.flatten = nn.Flatten()

        self.linear1 = nn.Linear(280, 2)

    def forward(self, x):
        x = x.permute(0, 4, 1, 2, 3)

        # print(x.shape)
        x = self.conv1(x)
        x = self.dropout1(x)
        x = self.relu1(x)

        # print(x.shape)
        x = self.conv2(x)
        x = self.dropout2(x)
        x = self.minimax(x)
        x = self.relu2(x)

        # x = self.conv3(x)
        # x = self.dropout3(x)
        # x = self.relu3(x)

        # print(x.shape)
        # x = self.conv4(x)
        # x = self.dropout4(x)
        # x = self.relu4(x)

        # print(x.shape)
        # x = x.reshape(16, 2, 10, 14)
        # print(x.shape)
        x = self.pool(x)
        x = self.flatten(x)
        # print(x.shape)

        x = self.linear1(x)

        return x

model = VideoModel()
model.eval()
model.load_state_dict(torch.load('model.pth'))


def result(file):
    # file = io.BytesIO(file)

    data = file  # 前端传的 bytes，无需再 io.BytesIO
    with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as f:
        f.write(data)
        tmp_path = f.name

    cap = cv2.VideoCapture(tmp_path)


    # width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    # height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))



    array = np.zeros((60
                          , 480, 640, 3), dtype=np.uint8)
    for i in range(60):    # 我这里期望后端传入 60 帧的视频
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.resize(frame, (480, 640))
        # array[i] = frame

        # print(np.array(frame).shape)
        # print(np.array(frame).shape[(width - 480) // 2 : (width - 480) // 2 + 480][
        #     (height - 640) // 2 : (height - 640) // 2 + 640])
        #
        #
        #
        # array[i] = (
        #     np.array(frame)[(width - 480) // 2 : (width - 480) // 2 + 480][
        #     (height - 640) // 2 : (height - 640) // 2 + 640]
        # )

    cap.release()

    # dataset = VideoDataset(array)
    # dataloader = DataLoader(dataset, batch_size=1, shuffle=False)
    array = torch.from_numpy(array).float()

    print(array.shape)
    array = array.unsqueeze(0)
    res = model(array)
    res = res.cpu().detach().numpy()
    res = str(np.argmax(res, axis=-1))

    os.unlink(tmp_path)
    return res


# arr = np.array([0, 1])
# print(str(np.argmax(arr, axis=-1)))   1
