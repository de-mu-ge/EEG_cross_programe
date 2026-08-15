import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# 真实模型权重路径（相对 python-service 根目录或绝对路径）
MODEL_PATH = os.getenv("MODEL_PATH", str(BASE_DIR / "models" / "eeg_model.pt"))
DEVICE = os.getenv("DEVICE", "cpu")
# 1=强制演示模式；0=按模型文件/依赖是否可用自动判断
DEMO_MODE = os.getenv("DEMO_MODE", "0") == "1"

# 二分类效价 label → 情绪名称
EMOTION_MAP = {0: "sad", 1: "happy"}

# DEAP .dat 数据格式
CHANNELS = 32
N_TRIALS = 40
N_WINDOWS_PER_TRIAL = 4
FRAME_SIZE = 2016
