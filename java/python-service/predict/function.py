import torch
from torch.utils.data import Dataset, DataLoader
import torch.nn as nn
import pickle
import io
import numpy as np
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent

# from Cpython.main.EEG.Dataload.dataset import play_list


class Play():
    def __init__(self, data, valence, arousal, dominance):
        self.data = data
        self.valence = valence
        self.arousal = arousal
        self.dominance = dominance

class MoD(nn.Module):
    def __init__(self):
        super().__init__()

        self.liner1 = nn.Linear(2016, 1)
        self.relu1 = nn.ReLU()
        self.dropout1 = nn.Dropout(0.2)
        self.pool = nn.Flatten()
        self.liner2 = nn.Linear(32, 10)
    def forward(self, x):
        x = self.liner1(x)
        # print(x.shape)
        x = self.relu1(x)
        x = self.dropout1(x)
        # print(x.shape)
        x = self.pool(x)
        # print(x.shape)
        x = self.liner2(x)
        return x

def data_read(raw):

    print("数据开始处理", flush=True)

    play_list = []
    print(f"    raw 类型: {type(raw)}", flush=True)
    if isinstance(raw, (str, Path)):
        fp = open(raw, 'rb')
        print(f"    raw 是路径: {raw}", flush=True)
    else:
        fp = io.BytesIO(raw)
        print(f"    raw 是文件内容, 共 {len(raw)} 字节", flush=True)
    with fp as f:
        print("    pickle.load 开始...", flush=True)
        subject = pickle.load(f, encoding="latin1")
        print(f"    pickle.load 成功, 键: {list(subject.keys())}", flush=True)
        label = subject['labels']
        data = subject['data'][:, :32]  # 前32个电极为脑电数据
        print(f"    data shape: {data.shape}, labels shape: {label.shape}", flush=True)
        for i in range(40):
            input = label[i].tolist()
            for j in range(4):
                play_list.append(Play(data[i][:, j:j + 2016], None, None, None))

    print(f"数据处理完成, 共构造 {len(play_list)} 个样本", flush=True)

    return play_list

class Set(Dataset):
    def __init__(self, play_list):
        self.data = []
        self.labels = []
        for play in play_list:
            self.data.append(torch.tensor(play.data).float())
            self.labels.append(0)
    def __getitem__(self, index):
        return self.data[index], self.labels[index]
    def __len__(self):
        return len(self.data)

def result(raw):
    import traceback

    try:
        outs = []
        print("开始数据处理(Set构造)", flush=True)
        dataset = Set(data_read(raw))
        print(f"数据集样本数: {len(dataset)}", flush=True)

        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"使用设备: {device}", flush=True)
        Loader = DataLoader(dataset, batch_size=1, shuffle=False)

        models = []
        for i in range(3):
            print(f"加载模型 {i}.pth ...", flush=True)
            model = MoD()
            model.eval()
            model.to(device)
            model.load_state_dict(torch.load(BASE_DIR / 'predict' / 'mod' / f'{i}.pth', map_location=device))
            models.append(model)
            print(f"模型 {i}.pth 加载完成", flush=True)

        total = 0
        for idx, (data, label) in enumerate(Loader):
            inputs = data.to(device)

            post = []
            for model in models:
                out = model(inputs)
                out = torch.sigmoid(out).cpu().detach().numpy()
                out = str(np.argmax(out, axis=1).tolist()[0])
                post.append(out)
                total += 1
            # if idx % 20 == 0:

            #     print(f"推理进度: 第 {idx + 1}/{len(Loader)} 个样本", flush=True)
            outs.append(post)

        print(f"模型正确返回, 共 {total} 个预测值", flush=True)
        return outs

    except Exception:
        print("========== 推理过程出错, 堆栈如下 ==========", flush=True)
        traceback.print_exc()
        print("============================================", flush=True)
        raise
# Loader = DataLoader()

