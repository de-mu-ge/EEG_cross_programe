import os
import cv2

path = r"D:\pragrame\now\dataset\subject3\Video\001_Trial_01_Listening_Neutral.mp4"

FRAME_NUM = 60          # 取前多少帧
HEIGHT = 480
WIDTH = 640

# 输出保存到脚本所在目录
save_dir = os.path.dirname(os.path.abspath(__file__))
save_path = os.path.join(save_dir, "video_60frames.mp4")

cap = cv2.VideoCapture(path)
if not cap.isOpened():
    raise RuntimeError(f"无法打开视频: {path}")

# 沿用源视频的帧率，取不到就默认 30
fps = cap.get(cv2.CAP_PROP_FPS)
if fps <= 0 or fps != fps:  # fps 为 0 或 NaN 时兜底
    fps = 30.0

# mp4v 是 mp4 容器里兼容性最好的编码，Windows 上无需额外解码器
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
writer = cv2.VideoWriter(save_path, fourcc, fps, (WIDTH, HEIGHT))

count = 0
for i in range(FRAME_NUM):
    ret, frame = cap.read()
    if not ret:
        print(f"读到第 {i} 帧时视频结束，只保留前 {i} 帧")
        break
    if frame.shape[1] != WIDTH or frame.shape[0] != HEIGHT:
        frame = cv2.resize(frame, (WIDTH, HEIGHT))
    writer.write(frame)
    count += 1

cap.release()
writer.release()

print(f"已取前 {count} 帧，按 {fps:.1f} fps 保存为视频: {save_path}")