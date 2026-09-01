import torch.nn as nn
# import torch


# 输入 (32, 2016)

class Model(nn.Module):
    def __init__(self):
        super().__init__()

        self.BatchNorm0 = nn.BatchNorm1d(32)

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
        self.pool0 = nn.MaxPool2d(kernel_size=(3,3), stride=(1,1))


        self.Conv2d2 = nn.Conv2d(in_channels=32, out_channels=4, kernel_size=(3,3), stride=(1,1))
        self.dropout3 = nn.Dropout(0.1)
        self.Conv2d3 = nn.Conv2d(in_channels=4, out_channels=1, kernel_size=(3,3), stride=(1,1))
        self.relu3 = nn.ReLU()

        self.BatchNorm3 = nn.BatchNorm1d(32)
        self.dropout4 = nn.Dropout(0.1)

        self.pool1 = nn.MaxPool2d(kernel_size=(3,3), stride=(1,1))
        self.Flatten = nn.Flatten()

        self.func1 = nn.Linear(in_features=13888, out_features=1024)
        self.BatchNorm3 = nn.BatchNorm1d(1024)
        self.func2 = nn.Linear(in_features=1024, out_features=32)
        self.BatchNorm4 = nn.BatchNorm1d(32)
        self.func3 = nn.Linear(in_features=32, out_features=10)

        

    def forward(self, x):

        x = self.BatchNorm0(x)  # 基础归一化

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
        data = self.pool0(data)
        data = self.dropout2(data)

        data = self.Conv2d2(data)
        data = self.dropout3(data)
        data = self.relu3(data)
        data = self.Conv2d3(data)
        data = self.dropout4(data)

        data = self.pool1(data)
        data = self.Flatten(data)

        # print(data.shape)
        data = self.func1(data)
        data = self.BatchNorm3(data)
        data = self.func2(data)
        data = self.BatchNorm4(data)
        data = self.func3(data)

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

# import torch
# import torch.nn as nn


class DEAPNet(nn.Module):

    def __init__(self, num_classes=10):
        super().__init__()

        # 输入: [B, 32, 2016]
        # 转成: [B, 1, 32, 2016]

        self.features = nn.Sequential(

            # [B, 1, 32, 2016]
            nn.Conv2d(
                in_channels=1,
                out_channels=32,
                kernel_size=(3, 15),
                padding=(1, 7)
            ),
            nn.BatchNorm2d(32),
            nn.ReLU(),

            # [B, 32, 32, 2016]
            nn.MaxPool2d(
                kernel_size=(2, 4)
            ),

            # [B, 32, 16, 504]
            nn.Conv2d(
                in_channels=32,
                out_channels=64,
                kernel_size=(3, 7),
                padding=(1, 3)
            ),
            nn.BatchNorm2d(64),
            nn.ReLU(),

            # [B, 64, 16, 504]
            nn.MaxPool2d(
                kernel_size=(2, 4)
            ),

            # [B, 64, 8, 126]
            nn.Conv2d(
                in_channels=64,
                out_channels=128,
                kernel_size=(3, 5),
                padding=(1, 2)
            ),
            nn.BatchNorm2d(128),
            nn.ReLU(),

            # [B, 128, 8, 126]
            nn.MaxPool2d(
                kernel_size=(2, 2)
            ),

            # [B, 128, 4, 63]
            nn.Conv2d(
                in_channels=128,
                out_channels=256,
                kernel_size=(3, 3),
                padding=1
            ),
            nn.BatchNorm2d(256),
            nn.ReLU(),

            # 不管前面尺寸具体如何变化
            # 最终统一成 [B, 256, 1, 1]
            nn.AdaptiveAvgPool2d((1, 1))
        )

        self.classifier = nn.Sequential(
            nn.Flatten(),

            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Dropout(0.25),

            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Dropout(0.2),

            nn.Linear(64, num_classes)
        )

    def forward(self, x):

        # 支持输入 [B, 32, 2016]
        if x.dim() == 3:
            x = x.unsqueeze(1)

        x = self.features(x)

        x = self.classifier(x)

        return x


# ==========================
# 测试
# ==========================
#
# if __name__ == "__main__":
#
#     model = DEAPNet(num_classes=10)
#
#     x = torch.randn(8, 32, 2016)
#
#     y = model(x)
#
#     print("input :", x.shape)
#     print("output:", y.shape)


