import dataclasses
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parents[7]

@dataclasses.dataclass
class Config:
    eav_name: str = "eav-dataset"
    eav_dataset_path: str = r"D:\pragrame\now\dataset"      # 这里先硬编码吧
    # eav_cache_path: str = r"C:\Users\home and dream\Desktop\ing\EEG\Cpython\data\cache\eav-cache.npy"
    pth_path : str = BASE_DIR / "Cpython/src/main/resources/model_out/video_pth/model.pth"

    lrs : float = 0.001
    epochs: int = 50