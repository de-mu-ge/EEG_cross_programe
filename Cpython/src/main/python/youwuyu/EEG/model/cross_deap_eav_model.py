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