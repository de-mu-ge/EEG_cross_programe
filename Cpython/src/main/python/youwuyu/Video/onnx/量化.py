import torch
import onnx
from Cpython.src.main.python.youwuyu.Video.model.model import VideoModel
from onnxruntime.quantization import quantize_dynamic, QuantType

model = VideoModel()
model.eval()
model.load_state_dict(torch.load(r"model.pth"))

#16  60, 480, 640, 3
inputs = torch.randn(1, 60, 480, 640, 3)
outputs = model(inputs)
print(outputs.shape)

torch.onnx.export(model,
                  inputs,
                  'model.onnx',
                  input_names=['input'],
                  output_names=['output'],
                  dynamic_axes=None,
                  opset_version=18)

m = onnx.load('model.onnx')
del m.graph.value_info[:]          # ← ★ 加这行：删掉旧 shape 元数据
onnx.save(m,
          'model0.onnx',
          save_as_external_data=False)


m = onnx.load("model0.onnx")

quantize_dynamic(m,
                 'model1.onnx',
                 weight_type=QuantType.QInt8)

