import torch.nn as nn


#16  60, 480, 640, 3
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









#16  60, 480, 640, 3
class TestModel(nn.Module):
    def __init__(self):
        super().__init__()

        self.conv1 = nn.Conv3d(3, 1, 6, 6)
        self.relu1 = nn.ReLU()
        self.conv2 = nn.Conv3d(60, 1, 6, 6)

    def forward(self, x):
        x = x.permute(0, 4, 1, 2, 3)
        x = self.conv1(x)
        x = x.reshape(16, 60, 480, 640)
        x = self.relu1(x)
        x = self.conv2(x)



