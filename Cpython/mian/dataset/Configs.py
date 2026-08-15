import dataclasses

@dataclasses.dataclass
class Config:
    dataset_name: str = "deap-dataset"
    dataset_path: str = r"C:\Users\home and dream\Desktop\ing\EEG\Cpython\data\deap-dataset\data_preprocessed_python"
    cache_path: str = r"C:\Users\home and dream\Desktop\ing\EEG\Cpython\mian\dataset\cache\cache.npy"


    lrs : float = 0.001
    epochs: int = 50