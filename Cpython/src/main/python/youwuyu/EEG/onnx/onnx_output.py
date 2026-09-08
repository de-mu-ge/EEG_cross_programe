# 硬件相关回头再说
# from idlelib.colorizer import color_config

import torch

from Cpython.src.main.python.youwuyu.EEG.configs.Configs import Config
# from Cpython.src.main.python.youwuyu.EEG.train.eav_deap_cross_train import cross_deap_eav_pth_path

config = Config()
cross_deap_eav_pth_path = config.cross_deap_eav_pth_path
cross_deap_eav_pth_onnx_path = config.cross_deap_eav_pth_onnx_path

from Cpython.src.main.python.youwuyu.EEG.model.transformer_deap_eav_cross_model import EEGModel
model = EEGModel()
model.load_state_dict(torch.load(cross_deap_eav_pth_path))
model.eval()
input_name = ['input']
output_name = ['output']

arr = torch.randn([1, 2000, 30])

torch.onnx.export(model, (arr,),
                  cross_deap_eav_pth_onnx_path, 
                  input_names=input_name,
                  output_names=output_name,
                  verbose=True
                  )


