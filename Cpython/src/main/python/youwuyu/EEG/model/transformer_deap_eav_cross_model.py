import torch.nn as nn
import torch

class Net(nn.Module):
    def __init__(self):
        super().__init__()

    def forward(self, x):

        return x

class Encoder(nn.Module):
    def __init__(self):     # (B, 1000, 15)
        super().__init__()

        # 通道处理，位置
        self.embedding = nn.Linear(in_features=15, out_features=128)
        self.linear = nn.Linear(in_features=1000, out_features=256)

        # 添加时间信息
        self.time_dim = nn.Parameter(torch.randn([1, 256], requires_grad=True))

    def forward(self, x):

        # 位置编码通道
        x = self.embedding(x)
        x = x.permute(0, 2, 1)      # （B, 128, 1000）
        x = self.linear(x)      # （B, 128, 256）     # (通道， 采集点)

        # 添加时间信息
        x = x + self.time_dim

        return x






class Transformer(nn.Module):
    def __init__(self):
        super().__init__()

        # 三层堆叠的子注意力机制
        self.Attention = nn.MultiheadAttention(embed_dim=256, num_heads=8, dropout=0.1)

        # 残差连接

        self.Norm1 = nn.LayerNorm(256)
        self.Fnn = nn.Sequential(
            nn.Linear(in_features=256, out_features=512),
            nn.ReLU(),
            # nn.Dropout(0.2),
            nn.Linear(in_features=512, out_features=256),
        )

        self.Norm2 = nn.LayerNorm(256)


    def forward(self,x):
        attn_out, _ = self.Attention(x, x,  x)

        # 残差链接
        x = self.Norm1(x + attn_out)
        fnn_out = self.Fnn(x)
        x = self.Norm2(x + fnn_out)


        return x

class EEGModel(nn.Module):
    def __init__(self):
        super().__init__()

        # 初始化处理
        self.Bath0 = nn.BatchNorm1d(2000, eps=1e-05, momentum=0.1, affine=True, track_running_stats=True)
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2)
        self.dropout = nn.Dropout(0.1)

        # 编码
        self.encoder = Encoder()

        # 自注意力
        self.Transformer = Transformer()

        # 分类        # # （B, 128, 256）     # (通道， 采集点)

        self.out = nn.Sequential(
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.Dropout(0.2),
            nn.Linear(in_features=64, out_features=2),
            nn.Flatten(),
            nn.Linear(in_features=64, out_features=2),
        )
        # self.pool2 = nn.MaxPool2d(kernel_size=2, stride=2)      # （B， 64， 128）
        # self.relu = nn.ReLU()
        # self.pool3 = nn.MaxPool2d(kernel_size=2, stride=2)      # （B， 32， 64）
        # self.dropout = nn.Dropout(0.1)
        # self.line1 = nn.Linear(in_features=64, out_features=2)
        # self.Fnn = nn.Flatten() # (B, 64)
        # self.line2 = nn.Linear(in_features=64, out_features=2)





    def forward(self,x):

        # 初始化处理
        x = self.Bath0(x)       # 归一化-处理量数据集不同数据
        x = self.pool(x)        # 池化，减少训练量，增强鲁棒性 ----(B, 1000, 15)
        x = self.dropout(x)

        # 编码
        x = self.encoder(x)

        # 自注意力
        x = self.Transformer(x)

        # 决策
        x = self.out(x)

        return x










if "__main__" == __name__:
    # import torch
    arr = torch.randn([2, 2000, 30]).float()

    model = EEGModel()

    model.eval()
    print(model(arr).shape)         # 二分类
    # print(model(arr))

