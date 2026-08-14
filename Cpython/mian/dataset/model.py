# import torch
import torch.nn as nn

# 数据输入格式是 (B, 40, 2016)
class Moudle(nn.Module):
    def __init__(self):
        super().__init__()

        self.liner1 = nn.Linear(2016, 1)
        self.pool = nn.Flatten()
        self.liner2 = nn.Linear(32, 2)
    def forward(self, x):
        x = self.liner1(x)
        # print(x.shape)
        x = self.pool(x)
        # print(x.shape)
        x = self.liner2(x)
        return x

