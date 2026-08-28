import dataclasses
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent

@dataclasses.dataclass
class Config:
    deap_name: str = "deap-dataset"
    eav_name: str = "eav-dataset"

    deap_dataset_path: str = r"C:\Users\home and dream\Desktop\ing\EEG\Cpython\data\dataset\deap-dataset\data_preprocessed_python"
    eav_dataset_path : str = r"D:\pragrame\now\dataset"

    cache_path: str = r"C:\Users\home and dream\Desktop\ing\EEG\Cpython\data\cache\deap-cache.npy"
    eeg_pth_path : str = r"C:\Users\home and dream\Desktop\ing\EEG\Cpython\main\EEG\out\pth"


    lrs : float = 0.001
    epochs: int = 50