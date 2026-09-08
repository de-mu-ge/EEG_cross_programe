import os
import math
import sys
import torch
import cv2
import numpy as np
from torch.utils.data import Dataset, DataLoader

sys.stdout.reconfigure(line_buffering=True)   # 实时看测试进度

from Cpython.src.main.python.youwuyu.Video.model.model import VideoModel
from Cpython.src.main.python.youwuyu.Video.configs.Configs import Config

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# =====================================================================
# 注意：下面这些常量、分割逻辑、标签逻辑必须与训练文件「一站式推理架构.py」完全一致，
#       否则在测试集上取窗口/造样本的方式和训练不一致，模型维度或标签会对不上。
# =====================================================================
VIDEOS_PER_CHUNK   = 6      # 必须与训练一致
WINDOWS_PER_VIDEO  = 2      # 必须与训练一致
FRAMES_PER_WINDOW  = 60     # 必须与训练一致（每窗 2s）
FRAME_H = FRAME_W = 224     # 必须与训练一致
BATCH_SIZE         = 8      # 推理批大小，可适当加大
TEST_RATIO         = 0.2    # 必须与训练一致

def add_label(strs):
    # 必须与训练一致：文件名倒数第9位字符 'A'(Anger)/'d'(Sadness) -> 0 消极，其余 -> 1
    if strs[-9] == 'A' or strs[-9] == 'd':
        return 0
    else:
        return 1

# ---------------- 与训练完全相同的 subject 层划分 ----------------
video_dir = Config.eav_dataset_path
subjects = sorted(m for m in os.listdir(video_dir)
                  if m != "GitHub_Codes"
                  and os.path.isdir(os.path.join(video_dir, m, "Video")))
n_test_subj = int(len(subjects) * TEST_RATIO)
test_subjects = set(subjects[-n_test_subj:])   # 结果必须等价于训练文件里的 test_subjects

def collect_paths(subject_set):
    paths = []
    for m in sorted(subjects):
        if m not in subject_set:
            continue
        vdir = os.path.join(video_dir, m, "Video")
        for n in os.listdir(vdir):
            paths.append(os.path.join(vdir, n))
    return paths

test_list = collect_paths(test_subjects)
print(f"[test] 测试 subject={len(test_subjects)} 视频={len(test_list)}")

# ---------------- 与训练相同的窗口读取 ----------------
def read_windows(path, windows=WINDOWS_PER_VIDEO, frames=FRAMES_PER_WINDOW):
    cap = cv2.VideoCapture(path)
    valid = []
    for _ in range(windows):
        arr = np.zeros((frames, FRAME_H, FRAME_W, 3), dtype=np.uint8)
        full = True
        for b in range(frames):
            ret, fr = cap.read()
            if not ret:
                full = False
                break
            fr = np.array(fr)
            if fr.ndim == 2:
                fr = np.stack([fr] * 3, axis=-1)
            if fr.shape[:2] != (FRAME_H, FRAME_W):
                fr = cv2.resize(fr, (FRAME_W, FRAME_H))
            if fr.shape[2] != 3:
                fr = fr[:, :, :3]
            arr[b] = fr
        if full:
            valid.append(torch.from_numpy(arr).float() / 255.0)   # 归一化到 [0,1]，必须与训练一致
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

# ---------------- 加载模型 ----------------
model = VideoModel().to(device)
model.load_state_dict(torch.load(str(Config.pth_path), map_location=device))
model.eval()

# =====================================================================
# 测试评估：负标签(0，消极) 召回率为主，总准确率为辅
# =====================================================================
if __name__ == "__main__":
    num_test_chunks = math.ceil(len(test_list) / VIDEOS_PER_CHUNK)
    all_pred, all_true = [], []
    with torch.no_grad():
        for ci in range(num_test_chunks):
            chunk = test_list[ci * VIDEOS_PER_CHUNK:(ci + 1) * VIDEOS_PER_CHUNK]
            plays = []
            for path in chunk:
                for arr in read_windows(path):
                    plays.append(Play(add_label(path), arr))
            if not plays:
                continue
            dataloader = DataLoader(DataSet(plays), batch_size=BATCH_SIZE, shuffle=False)
            for data, label in dataloader:
                data = data.to(device)
                out = model(data)
                pred = out.argmax(dim=1).cpu()
                all_pred.extend(pred.tolist())
                all_true.extend(label.tolist())
            pct = (ci + 1) / num_test_chunks * 100
            print(f"\r  [test] 块 {ci + 1}/{num_test_chunks} ({pct:5.1f}%) 已测试",
                  end="", flush=True)
        print()

    # ---------------- 指标 ----------------
    n_class = 2
    conf = [[0, 0] for _ in range(n_class)]          # conf[真实][预测]
    for t, p in zip(all_true, all_pred):
        conf[t][p] += 1
    total = sum(sum(r) for r in conf)
    acc = sum(conf[i][i] for i in range(n_class)) / max(total, 1)

    def metrics(cls):
        tp = conf[cls][cls]
        fn = sum(conf[cls]) - tp
        fp = sum(conf[r][cls] for r in range(n_class)) - tp
        tn = total - tp - fn - fp
        precision = tp / max(tp + fp, 1)
        recall = tp / max(tp + fn, 1)
        f1 = 2 * precision * recall / max(precision + recall, 1)
        return precision, recall, f1

    p0, r0, f1_0 = metrics(0)   # 消极 / 负标签
    p1, r1, f1_1 = metrics(1)   # 非消极

    print("\n================== 推理测试结果 ==================")
    print(f"样本总数: {total}")
    print("混淆矩阵 [真实->预测]:")
    print(f"        预测0  预测1")
    print(f"真实0  {conf[0][0]:6d} {conf[0][1]:6d}   (消极)")
    print(f"真实1  {conf[1][0]:6d} {conf[1][1]:6d}   (非消极)")
    print("---------------------------------------------------")
    # 主指标：负标签(0/消极)召回率
    print(f"【主指标】负标签召回率 (recall of class0/消极) = {r0:.4f}")
    # 辅指标：总准确率
    print(f"【辅指标】总准确率 (accuracy)                 = {acc:.4f}")
    print("---------------------------------------------------")
    print(f"class0 消极  : precision={p0:.4f}  recall={r0:.4f}  F1={f1_0:.4f}")
    print(f"class1 非消极: precision={p1:.4f}  recall={r1:.4f}  F1={f1_1:.4f}")
    print("==================================================")
