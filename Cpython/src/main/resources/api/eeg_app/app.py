from function import result
from fastapi import FastAPI, File, HTTPException, UploadFile

app = FastAPI(title="EEG Signal Prediction API")
@app.get("/hello")
def hello():

    print("访问成功")

    return {"Hello World" : "Hello World"}

@app.post("/predict")
def predict(file: UploadFile = File(...)):
    print(f"[app] 收到请求, 文件名: {file.filename}", flush=True)
    raw = file.file.read()
    print(f"[app] 已读取 {len(raw)} 字节", flush=True)

    print("[app] 即将进行运算", flush=True)
    res = result(raw)
    print(f"[app] 推理完成, 返回 {len(res)} 条预测值", flush=True)

    return {
        "result: ": res
    }

# python -m uvicorn app.app:app --port 8000


