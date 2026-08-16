import torch
import torch.nn as nn

# 与 predict.py 中的 Moudle 一致：输入 (B, 32, 2016) → 输出 (B, 2)
class Moudle(nn.Module):
    def __init__(self):
        super().__init__()
        self.liner1 = nn.Linear(2016, 1)
        self.pool = nn.Flatten()
        self.liner2 = nn.Linear(32, 2)

    def forward(self, x):
        x = self.liner1(x)
        x = self.pool(x)
        x = self.liner2(x)
        return x


def load_model(model_path, device):
    model = Moudle()
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()
    model.to(device)
    return model
