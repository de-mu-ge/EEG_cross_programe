package com.neuroai.backend.service;

import com.neuroai.backend.dto.AiPredictResponse;

public interface AIService {

    /**
     * 将已落盘的 .dat 文件传输给 Python 推理服务并解析结果
     */
    AiPredictResponse predict(String filePath);
}
