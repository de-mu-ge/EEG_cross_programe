import dataclasses
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent

@dataclasses.dataclass
class Config:
    dataset_name: str = "deap-dataset"
    dataset_path: str = r"C:\Users\home and dream\Desktop\ing\EEG\Cpython\data\dataset\deap-dataset\data_preprocessed_python"
    cache_path: str = r"C:\Users\home and dream\Desktop\ing\EEG\Cpython\data\cache\deap-cache.npy"
    pth_path : str = r"C:\Users\home and dream\Desktop\ing\EEG\Cpython\main\EEG\out\pth\eeg.pth"


    lrs : float = 0.001
    epochs: int = 50