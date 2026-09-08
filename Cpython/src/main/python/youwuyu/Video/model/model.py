import torch.nn as nn


# 输入来自一站式推理架构.py：每个窗口 shape = (frames, H, W, 3)。
# 模型通过 自适应全局池化 与输入尺寸无关（不再像旧 linear(280) 那样依赖固定维度），
# 因此 frames/空间尺寸都可自由调整，训练/测试只需保持一致即可。
class VideoModel(nn.Module):
    def __init__(self, in_channels: int = 3, num_classes: int = 2):
        super().__init__()

        # 先归一化输入（在 permute 之后、按真实通道轴 C 做 z-score，尺寸无关）
        self.Bath = nn.BatchNorm3d(in_channels)

        # 4 层 3D 卷积，每层 stride=2 逐步下采样时间/空间
        self.features = nn.Sequential(
            nn.Conv3d(in_channels, 24, kernel_size=3, stride=2, padding=1),
            nn.BatchNorm3d(24),
            nn.ReLU(inplace=True),

            nn.Conv3d(24, 48, kernel_size=3, stride=2, padding=1),
            nn.BatchNorm3d(48),
            nn.ReLU(inplace=True),

            nn.Conv3d(48, 96, kernel_size=3, stride=2, padding=1),
            nn.BatchNorm3d(96),
            nn.ReLU(inplace=True),

            nn.Conv3d(96, 128, kernel_size=3, stride=2, padding=1),
            nn.BatchNorm3d(128),
            nn.ReLU(inplace=True),
        )
        # 池化到 1x1x1 -> (B,128,1,1,1)，使输出与 T/H/W 无关
        self.global_pool = nn.AdaptiveAvgPool3d(1)
        self.dropout = nn.Dropout(0.5)
        self.classifier = nn.Sequential(
            nn.Linear(128, 64),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(64, num_classes),
        )

    def forward(self, x):
        # x: (B, T, H, W, C) 来自 DataLoader
        x = x.permute(0, 4, 1, 2, 3)          # -> (B, C, T, H, W)
        x = self.Bath(x)                      # 对真实通道轴 C 做归一化
        x = self.features(x)
        x = self.global_pool(x)
        x = x.flatten(1)                      # -> (B, 128)
        x = self.dropout(x)
        x = self.classifier(x)
        return x


# --------test--------
if __name__ == "__main__":      # (B, 3, 16, 224, 224)
    import torch
    arr = torch.randn(3, 60, 224, 224, 3).float()   # (Bath, 16个采集点， 224H, 224W, 3通道)   # 30FPS
    # model = VideoModel(in_channels=3, num_classes=2)
    model = VideoModel(in_channels=3, num_classes=2)

    out = model(arr)

    print(out)
    print(out.size())

