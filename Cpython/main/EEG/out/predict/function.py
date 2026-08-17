import torch
from torch.utils.data import Dataset, DataLoader
import torch.nn as nn
import pickle
import io
import numpy as np
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent

# from Cpython.main.EEG.Dataload.dataset import play_list


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
        data = subject['data']

        # 模型期望的输入: 32 通道 × 2016 时间点, 每个样本切成 4 段
        N_CH_TARGET = 32               # 目标通道数
        SEG_LEN = 2016                 # 每段时间长度
        N_SEG = 4                      # 每个样本切成的段数
        TOTAL_LEN = N_SEG * SEG_LEN    # 8064, 单个样本的目标总长度

        print(f"    data shape: {data.shape}, labels shape: {label.shape}", flush=True)

        # ---- 数据维度兜底: 支持 2D (样本, 通道) 或 3D (样本, 通道, 时间) ----
        if data.ndim == 2:
            print("    data 是 2D, 按 (样本, 通道, 1) 处理", flush=True)
            data = data[:, :, np.newaxis]
        elif data.ndim != 3:
            raise ValueError(f"不支持的数据维度: {data.ndim}, 期望 2D 或 3D")

        # ---- 通道维度兼容: 多的裁, 少的补零 ----
        n_ch = data.shape[1]
        if n_ch > N_CH_TARGET:
            print(f"    通道数 {n_ch} > {N_CH_TARGET}, 截取前 {N_CH_TARGET} 个电极", flush=True)
            data_ch = data[:, :N_CH_TARGET, :]
        elif n_ch < N_CH_TARGET:
            print(f"    通道数 {n_ch} < {N_CH_TARGET}, 补零至 {N_CH_TARGET} 个电极", flush=True)
            pad_ch = np.zeros((data.shape[0], N_CH_TARGET - n_ch, data.shape[2]), dtype=data.dtype)
            data_ch = np.concatenate([data, pad_ch], axis=1)
        else:
            data_ch = data

        # ---- 时间维度兼容: 多的裁, 少的补零, 再按每 SEG_LEN 点不重叠切分 ----
        samples = []                 # 外层: 每个样本
        n_trials = data_ch.shape[0]
        for i in range(n_trials):
            seg = data_ch[i]  # (N_CH_TARGET, n_time)
            n_time = seg.shape[1]
            if n_time > TOTAL_LEN:
                print(f"    样本 {i} 时间点数 {n_time} > {TOTAL_LEN}, 截取前 {TOTAL_LEN} 点", flush=True)
                seg = seg[:, :TOTAL_LEN]
            elif n_time < TOTAL_LEN:
                print(f"    样本 {i} 时间点数 {n_time} < {TOTAL_LEN}, 补零至 {TOTAL_LEN} 点", flush=True)
                pad_t = np.zeros((N_CH_TARGET, TOTAL_LEN - n_time), dtype=seg.dtype)
                seg = np.concatenate([seg, pad_t], axis=1)

            # 每个样本按每 SEG_LEN 采集点不重叠切成 N_SEG 段, 每段 (1, 32, 2016) 三维
            segs = []
            for j in range(N_SEG):
                segs.append(seg[:, j * SEG_LEN:(j + 1) * SEG_LEN][np.newaxis, :, :])
            samples.append(segs)  # 嵌套一层, 表示单个样本

    print(f"数据处理完成, 共 {len(samples)} 个样本, 每样本 {N_SEG} 段", flush=True)

    return samples

class Set(Dataset):
    def __init__(self, samples):
        self.data = []
        self.labels = []
        self.sample_idx = []  # 记录每一段属于哪个样本, 推理时按样本分组
        for si, sample in enumerate(samples):
            for seg in sample:
                # seg 是 (1, 32, 2016), 去掉 batch 维, DataLoader 会自动补回
                self.data.append(torch.tensor(seg).float().squeeze(0))
                self.labels.append(0)
                self.sample_idx.append(si)
    def __getitem__(self, index):
        return self.data[index], self.labels[index]
    def __len__(self):
        return len(self.data)

def result(raw):
    import traceback

    try:
        print("开始数据处理(Set构造)", flush=True)
        samples = data_read(raw)
        dataset = Set(samples)
        print(f"数据集样本数: {len(samples)}, 段总数: {len(dataset)}", flush=True)

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
        flat_outs = []  # 平铺的预测结果
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
            flat_outs.append(post)

        # 按样本嵌套: outs[i][j] = 样本 i 的第 j 段的预测 [3个模型的输出]
        n_seg = len(samples[0]) if samples else 0
        outs = [
            [flat_outs[i * n_seg + j] for j in range(n_seg)]
            for i in range(len(samples))
        ]
        print(f"模型正确返回, 共 {total} 个预测值, {len(outs)} 个样本", flush=True)
        return outs

    except Exception:
        print("========== 推理过程出错, 堆栈如下 ==========", flush=True)
        traceback.print_exc()
        print("============================================", flush=True)
        raise
# Loader = DataLoader()

