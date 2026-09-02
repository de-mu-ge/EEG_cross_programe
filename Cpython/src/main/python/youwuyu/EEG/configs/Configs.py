import dataclasses
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parents[7]

@dataclasses.dataclass
class Config:
    deap_name: str = "deap-dataset"
    eav_name: str = "eav-dataset"

    deap_dataset_path: str = BASE_DIR / "Cpython/src/main/resources/dataset/deap-dataset/data_preprocessed_python"
    eav_dataset_path : str = r"D:\pragrame\now\dataset"

    deap_eeg_cache_path: str = BASE_DIR / "Cpython/src/main/resources/cache/deap_eeg_cache.npy"
    eav_eeg_cache_path: str = BASE_DIR / "Cpython/src/main/resources/cache/eav_eeg_cache.npy"
    cross_deap_cache_path: str = BASE_DIR / "Cpython/src/main/resources/cache/cross_deap_cache.npy"

    deap_eeg_pth_path : str = BASE_DIR / "Cpython/src/main/resources/model_out/deap_eeg_pth"
    eav_eeg_pth_path : str = BASE_DIR / "Cpython/src/main/resources/model_out/eeg_pth/eav_eeg_pth"


    lrs : float = 0.001
    epochs: int = 40