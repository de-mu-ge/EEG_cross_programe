import pickle
import time
from pathlib import Path

import numpy as np
from fastapi import FastAPI, File, HTTPException, UploadFile

from . import config

app = FastAPI(title="NEURO-AI EEG AI Service")


def _load_model():
    """启动时加载真实模型；torch 未装或权重缺失时返回 None（自动进入演示兜底）"""
    try:
        import torch
        from .model import load_model
    except ImportError:
        return None
    path = Path(config.MODEL_PATH)
    if not path.exists():
        return None
    device = torch.device(config.DEVICE)
    return {"model": load_model(str(path), device), "device": device}


_model = _load_model()


@app.get("/api/health")
def health():
    return {
        "status": "UP",
        "model_loaded": _model is not None,
        "model_path": str(config.MODEL_PATH),
        "demo_mode": _model is None,
        "device": config.DEVICE,
    }


def _parse_windows(raw: bytes):
    """解析 DEAP pickle .dat，返回全部 (CHANNELS, FRAME_SIZE) 窗口列表"""
    subject = pickle.loads(raw, encoding="latin1")
    data = np.asarray(subject["data"])[:, : config.CHANNELS]
    windows = []
    for i in range(config.N_TRIALS):
        for j in range(config.N_WINDOWS_PER_TRIAL):
            windows.append(data[i][:, j : j + config.FRAME_SIZE])
    return windows


def _predict_real(model, device, windows):
    """全窗推理并聚合（平均 sigmoid 概率后 argmax），修复 predict.py 只保留最后一窗口的 BUG"""
    import torch

    probs = []
    with torch.no_grad():
        for w in windows:
            x = torch.tensor(w, dtype=torch.float32).unsqueeze(0).to(device)
            out = torch.sigmoid(model(x)).cpu().numpy()[0]
            probs.append(out)
    mean_prob = np.mean(probs, axis=0)
    label = int(np.argmax(mean_prob))
    confidence = float(mean_prob[label])
    emotion = config.EMOTION_MAP.get(label, "unknown")
    return emotion, label, confidence


@app.post("/api/predict")
async def predict(file: UploadFile = File(...)):
    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=400, detail="文件内容为空")

    start = time.time()
    if config.DEMO_MODE or _model is None:
        return {
            "status": "success",
            "message": "演示模式(未加载真实模型)",
            "emotion": "happy",
            "label": 1,
            "confidence": 0.92,
            "elapsed_ms": int((time.time() - start) * 1000),
        }

    try:
        windows = _parse_windows(raw)
        emotion, label, confidence = _predict_real(_model["model"], _model["device"], windows)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"推理失败: {e}")

    return {
        "status": "success",
        "message": f"分析完成，主导情绪: {emotion}",
        "emotion": emotion,
        "label": label,
        "confidence": confidence,
        "elapsed_ms": int((time.time() - start) * 1000),
    }
