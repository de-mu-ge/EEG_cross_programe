import torch.nn as nn
# import torch


# 输入 (32, 2016)

class Model(nn.Module):
    def __init__(self):
        super().__init__()

        self.liner1 = nn.Linear(4, 64)
        self.BatchNorm1 = nn.BatchNorm2d(8)
        self.relu1 = nn.ReLU()
        self.dropout1 = nn.Dropout(0.1)
        # self.liner2 = nn.Linear(64, 64)

        self.liner3 = nn.Linear(2016, 256)
        self.Conv2d1 = nn.Conv2d(in_channels=8, out_channels=32, kernel_size=(3,3), stride=(1,1))
        self.BatchNorm2 = nn.BatchNorm2d(32)
        self.relu2 = nn.ReLU()
        self.dropout2 = nn.Dropout(0.1)


        self.Conv2d2 = nn.Conv2d(in_channels=32, out_channels=4, kernel_size=(3,3), stride=(1,1))
        self.dropout3 = nn.Dropout(0.1)
        self.Conv2d3 = nn.Conv2d(in_channels=4, out_channels=1, kernel_size=(3,3), stride=(1,1))
        self.relu3 = nn.ReLU()

        self.pool = nn.MaxPool2d(kernel_size=(3,3), stride=(1,1))
        self.Flatten = nn.Flatten()

        self.func1 = nn.Linear(in_features=13888, out_features=32)
        self.BatchNorm3 = nn.BatchNorm1d(32)
        self.func2 = nn.Linear(in_features=32, out_features=10)

    def forward(self, x):

        data = x.reshape(x.shape[0], 8, 4, 2016)      # （B, 32， 2016） -> (B, 8, 4 , 2016)

        data = data.permute(0, 1, 3, 2)

        data = self.liner1(data)
        data = self.BatchNorm1(data)
        data = self.relu1(data)
        data = self.dropout1(data)

        data  = data.permute(0, 1, 3, 2)

        data = self.liner3(data)


        data = self.Conv2d1(data)
        data = self.BatchNorm2(data)
        data = self.relu2(data)
        data = self.dropout2(data)

        data = self.Conv2d2(data)
        data = self.relu3(data)
        data = self.Conv2d3(data)
        data = self.dropout3(data)

        data = self.pool(data)
        data = self.Flatten(data)

        # print(data.shape)
        data = self.func1(data)
        data = self.BatchNorm3(data)
        data = self.func2(data)

        return data


#
# class Net(nn.Module):
#     def __init__(self):
#         super().__init__()
#
#
#     def forward(self, x):
#
#
#
#
#         return x



