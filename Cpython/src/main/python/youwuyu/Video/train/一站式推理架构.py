import os
import math
import random
import sys
import time
import torch
import cv2
import numpy as np
from torch.utils.data import Dataset, DataLoader

sys.stdout.reconfigure(line_buffering=True)   # 一有 print 就刷新，运行时可实时看到进度

from Cpython.src.main.python.youwuyu.Video.model.model import VideoModel
from Cpython.src.main.python.youwuyu.Video.configs.Configs import Config

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# =====================================================================
# 参数（决定 运行时长 / 显存 / 内存，请按机器调整）
#   VideoModel 已改为「自适应全局池化」，与窗口帧数/空间尺寸无关，无需再匹配 280。
#   帧数/尺寸越大越有信息但越慢，按机器调。
# =====================================================================
VIDEOS_PER_CHUNK   = 6      # 每个循环块一次读入的视频数
WINDOWS_PER_VIDEO  = 2      # 每个视频取多少个窗口（满量=10）
FRAMES_PER_WINDOW  = 60     # 每窗帧数 = 2s（30fps x 2s），工程化对齐
FRAME_H = FRAME_W = 224     # 每帧缩放到的空间尺寸（训练/测试必须一致）
BATCH_SIZE         = 8      # 每批窗口数（12G 显存 + 224 输入可开到 8~16）
EPOCHS             = 3      # 跑几圈；单圈几乎学不到，负召回需要多圈
TEST_RATIO         = 0.2    # 按 subject 层留出比例
LR                 = 0.0001

def add_label(strs):
    # 负标签/消极: 文件名倒数第9位字符为 'A'(Anger) 或 'd'(Sadness) -> 0，其余 -> 1
    #   情绪 -> -9位: Neutral 'u' | Anger 'A' | Calmness 'm' | Sadness 'd' | Happiness 'i'
    #   类别数量(全量): neg {Anger,Sadness}=3360 / pos=5040
    if strs[-9] == 'A' or strs[-9] == 'd':
        return 0    # 表示消极情绪
    else:
        return 1    # 表示非消极情绪

# ---------------- 划分 train / test（subject 层，确定性，防泄漏）----------------
# 注意：测试文件 依托于一站式推理框架的模型测试.py 用【完全相同的】划分逻辑，
#       否则 train/test 会不一致。
video_dir = Config.eav_dataset_path
subjects = sorted(m for m in os.listdir(video_dir)
                  if m != "GitHub_Codes"
                  and os.path.isdir(os.path.join(video_dir, m, "Video")))
n_test_subj = int(len(subjects) * TEST_RATIO)
test_subjects = set(subjects[-n_test_subj:])            # 末尾 TEST_RATIO 的 subject 全部做测试
train_subjects = set(subjects) - test_subjects          # 其余做训练

def collect_paths(subject_set):
    paths = []
    for m in sorted(subjects):
        if m not in subject_set:
            continue
        vdir = os.path.join(video_dir, m, "Video")
        for n in os.listdir(vdir):
            paths.append(os.path.join(vdir, n))
    return paths

train_list = collect_paths(train_subjects)
test_list = collect_paths(test_subjects)

# ---------------- 训练集类别数量 -> 分类权重 ----------------
train_counts = [0, 0]
for p in train_list:
    train_counts[add_label(p)] += 1
total = max(sum(train_counts), 1)
weights = [total / (2.0 * max(train_counts[c], 1)) for c in range(2)]
class_weights = torch.tensor(weights, dtype=torch.float32).to(device)
# 各标签数量（注释，运行时会再打印）：
#   label 0 消极(Anger+Sadness)              = 2720 (34 subject 训练集) / 3360 (全量)
#   label 1 非消极(Neutral+Happiness+Calmness) = 4080 (34 subject 训练集) / 5040 (全量)
print(f"[split] 训练 subject={len(train_subjects)} 视频={len(train_list)} | "
      f"测试 subject={len(test_subjects)} 视频={len(test_list)}")
print(f"[label] 训练集类别计数 -> 消极(0)={train_counts[0]}  非消极(1)={train_counts[1]}")
print(f"[wt  ] 分类权重(class_weights)={weights}")

# ---------------- 数据读取（不完整窗口直接丢弃，不再黑帧补齐）----------------
def read_windows(path, windows=WINDOWS_PER_VIDEO, frames=FRAMES_PER_WINDOW):
    cap = cv2.VideoCapture(path)
    valid = []
    for _ in range(windows):
        arr = np.zeros((frames, FRAME_H, FRAME_W, 3), dtype=np.uint8)
        full = True
        for b in range(frames):
            ret, fr = cap.read()
            if not ret:
                full = False          # 窗口不足 frames 帧 -> 丢弃，避免黑帧污染
                break
            fr = np.array(fr)
            if fr.ndim == 2:
                fr = np.stack([fr] * 3, axis=-1)        # 灰度兜底 -> 3 通道
            if fr.shape[:2] != (FRAME_H, FRAME_W):
                fr = cv2.resize(fr, (FRAME_W, FRAME_H))
            if fr.shape[2] != 3:
                fr = fr[:, :, :3]
            arr[b] = fr
        if full:
            valid.append(torch.from_numpy(arr).float() / 255.0)   # 归一化到 [0,1]
        else:
            break
    cap.release()
    return valid

class Play:
    def __init__(self, valance, video):
        self.valance = valance
        self.video = video

class DataSet(Dataset):
    def __init__(self, datas):
        self.datas = datas
    def __len__(self):
        return len(self.datas)
    def __getitem__(self, item):
        return self.datas[item].video, self.datas[item].valance

# ---------------- 模型 / 损失 / 优化器 ----------------
model = VideoModel().to(device)
criterion = torch.nn.CrossEntropyLoss(weight=class_weights)
optimizer = torch.optim.Adam(model.parameters(), lr=LR)

# =====================================================================
# 一站式训练：完整跑满一圈训练集（不再硬编码 range(10)）
# =====================================================================
if __name__ == "__main__":
    model.train()
    num_train_chunks = math.ceil(len(train_list) / VIDEOS_PER_CHUNK)
    print(f"[train] 总块数 = {num_train_chunks}（每块 {VIDEOS_PER_CHUNK} 视频，"
          f"每视频 {WINDOWS_PER_VIDEO} 窗，每窗 {FRAMES_PER_WINDOW} 帧 @ {FRAME_H}x{FRAME_W}，"
          f"EPOCHS={EPOCHS}）")
    loss = None
    for ep in range(EPOCHS):
        chunk_order = list(range(num_train_chunks))
        random.shuffle(chunk_order)          # 每圈打乱块顺序，避免固定顺序过拟合
        print(f"\n[epoch {ep + 1}/{EPOCHS}] 开始")
        epoch_start = time.time()
        for k, ci in enumerate(chunk_order, start=1):
            chunk = train_list[ci * VIDEOS_PER_CHUNK:(ci + 1) * VIDEOS_PER_CHUNK]
            plays = []
            for path in chunk:
                for arr in read_windows(path):
                    plays.append(Play(add_label(path), arr))
            if not plays:
                continue
            dataloader = DataLoader(DataSet(plays), batch_size=BATCH_SIZE, shuffle=True)
            for data, label in dataloader:
                data = data.to(device) 
                label = label.to(device)
                optimizer.zero_grad()
                out = model(data)
                loss = criterion(out, label)
                loss.backward()
                optimizer.step()
            # —— 实时进度：同一行刷新 % / 已用时长 / 预计剩余 ——
            pct = k / num_train_chunks * 100
            elapsed = time.time() - epoch_start
            eta = elapsed / k * (num_train_chunks - k)
            ltxt = f"{loss.item():.3f}" if loss is not None else "--"
            print(f"\r  [epoch {ep + 1}/{EPOCHS}] 块 {k}/{num_train_chunks} ({pct:5.1f}%)  "
                  f"已用{elapsed:6.1f}s  预计剩余{eta:6.1f}s  loss={ltxt}",
                  end="", flush=True)
        print()
        print(f"[epoch {ep + 1}/{EPOCHS}] 完成")

    save_path = str(Config.pth_path)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    torch.save(model.state_dict(), save_path)
    print("\n[train] 完成，模型保存到:", save_path)
