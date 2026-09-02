from function import result
from fastapi import FastAPI, File, HTTPException, UploadFile

app = FastAPI(title="Video Signal Prediction API")
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
    print(f"[app] 推理完成, 返回预测值", flush=True)

    return {
        "result: ": res     # 1表示消极情绪 0表示非消极情绪
    }





# cd Cpython/main/Video/out/app
# python -m uvicorn app:app --port 8001

# curl.exe -X POST http://127.0.0.1:8001/predict -F "file=@Cpython/main/Video/Dataload/video_60frames.mp4"