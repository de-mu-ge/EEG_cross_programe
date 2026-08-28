import dataclasses
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent

@dataclasses.dataclass
class Config:
    eav_name: str = "eav-dataset"
    eav_dataset_path: str = r"D:\pragrame\now\dataset"
    eav_cache_path: str = r"C:\Users\home and dream\Desktop\ing\EEG\Cpython\data\cache\eav-cache.npy"
    pth_path : str = r"C:\Users\home and dream\Desktop\ing\EEG\Cpython\main\EEG\out\pth"

    lrs : float = 0.001
    epochs: int = 50