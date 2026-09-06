import torch.nn as nn

class Model(nn.Module):
    def __init__(self):
        super().__init__()

        self.Net1 = nn.Sequential(
            nn.BatchNorm1d(2000),
            nn.Linear(30, 64),
            nn.ReLU(),
            nn.Linear(64, 1),
        )
        self.Net2 = nn.Sequential(
            nn.BatchNorm1d(2000),
            nn.Flatten(),
            nn.Linear(2000, 2),
        )

    def forward(self, x):       # 输入 (2000, 30)
        x = self.Net1(x)
        x = self.Net2(x)
        return x


class CrossModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.Net1 = nn.Sequential(  # 升维
            nn.BatchNorm2d(40),
            nn.Conv2d(40, 120, 5, padding=2),
            nn.ReLU(),
            nn.AvgPool2d(2, stride=2),  # 池化
            nn.Linear(15, 50),
            nn.Dropout(0.2),
        )

        self.Net2 = nn.Sequential(     # 理解
            nn.BatchNorm2d(120),
            nn.Conv2d(120, 10, 5, padding=2),
            nn.ReLU(),
            nn.AvgPool2d(2, stride=2),
            nn.Linear(25, 5),
            nn.Dropout(0.2),
        )

        self.Net3 = nn.Sequential(  # 降维
            nn.BatchNorm2d(10),
            nn.Conv2d(10, 1, 5, padding=2),
            nn.ReLU(),
            nn.AvgPool2d(2, stride=2),
            nn.Linear(2, 1),
            nn.Dropout(0.2),
            nn.Flatten(),
        )

        self.Net4 = nn.Sequential(  # 决策
            # nn.AvgPool2d(2, stride=2),
            nn.Linear(6, 2),
        )


    def forward(self, x):   # (B, 2000, 30)
        x = x.reshape(x.shape[0], 40, 50, 30)   # （B， 40， 50， 30）

        x = self.Net1(x)
        x = self.Net2(x)
        x = self.Net3(x)

        # print("x的尺寸是")
        # print(x.shape)
        x = self.Net4(x)

        return x

class EEGClassifier(nn.Module):

    def __init__(self):
        super().__init__()

        self.features = nn.Sequential(
            # (B, 30, 2000)
            nn.Conv1d(30, 64, kernel_size=15, padding=7),
            nn.BatchNorm1d(64),
            nn.GELU(),

            # (B, 64, 2000)
            nn.Conv1d(64, 128, kernel_size=15, stride=2, padding=7),
            nn.BatchNorm1d(128),
            nn.GELU(),

            # (B, 128, 1000)
            nn.Conv1d(128, 256, kernel_size=15, stride=2, padding=7),
            nn.BatchNorm1d(256),
            nn.GELU(),

            # (B, 256, 500)
            nn.Conv1d(256, 256, kernel_size=15, stride=2, padding=7),
            nn.BatchNorm1d(256),
            nn.GELU(),

            # (B, 256, 250)
            nn.AdaptiveAvgPool1d(1)
        )

        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(256, 128),
            nn.GELU(),
            nn.Dropout(0.3),
            nn.Linear(128, 2)
        )

    def forward(self, x):
        # 输入:
        # (B, 2000, 30)

        # Conv1d需要:
        # (B, 30, 2000)
        x = x.transpose(1, 2)

        x = self.features(x)

        # (B, 256, 1)

        x = self.classifier(x)

        # (B, 2)

        return x


# =========================
# 测试
# =========================




if __name__ == "__main__":
    import torch

    model = EEGClassifier()

    x = torch.randn(8, 2000, 30)

    y = model(x)

    print("输入 :", x.shape)
    print("输出 :", y.shape)
    print("参数量 :", sum(p.numel() for p in model.parameters()))
