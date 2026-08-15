package com.neuroai.backend.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.neuroai.backend.dto.AiPredictResponse;
import com.neuroai.backend.entity.EegAnalysisRecord;
import com.neuroai.backend.exception.BusinessException;
import com.neuroai.backend.mapper.EegAnalysisRecordMapper;
import com.neuroai.backend.service.AIService;
import com.neuroai.backend.service.EegAnalysisService;
import com.neuroai.backend.service.FileStorageService;
import com.neuroai.backend.vo.AnalysisResultVO;
import com.neuroai.backend.vo.UploadResultVO;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.util.HashMap;
import java.util.Map;

@Slf4j
@Service
@RequiredArgsConstructor
public class EegAnalysisServiceImpl extends ServiceImpl<EegAnalysisRecordMapper, EegAnalysisRecord>
        implements EegAnalysisService {

    private final FileStorageService fileStorageService;
    private final AIService aiService;
    private final ObjectMapper objectMapper;

    @Override
    public UploadResultVO upload(MultipartFile file) {
        String filePath = fileStorageService.store(file);

        EegAnalysisRecord record = new EegAnalysisRecord();
        record.setFileName(file.getOriginalFilename());
        record.setFilePath(filePath);

        try {
            AiPredictResponse resp = aiService.predict(filePath);
            record.setStatus("SUCCESS");
            record.setResult(buildResult(resp));
            record.setModelData(objectMapper.convertValue(resp, new TypeReference<Map<String, Object>>() {}));
            save(record);
            log.info("分析完成: id={}, emotion={}, confidence={}", record.getId(), resp.getEmotion(), resp.getConfidence());
        } catch (BusinessException e) {
            record.setStatus("FAILED");
            record.setModelData(Map.of("error", e.getMessage()));
            save(record);
            log.error("分析失败: id={}, error={}", record.getId(), e.getMessage());
            throw e;
        }
        return new UploadResultVO(record.getId());
    }

    @Override
    public AnalysisResultVO getResult(Long id) {
        EegAnalysisRecord record = getById(id);
        if (record == null) {
            throw new BusinessException(404, "分析记录不存在: " + id);
        }
        if ("FAILED".equals(record.getStatus())) {
            Map<String, Object> modelData = record.getModelData();
            Object error = modelData == null ? null : modelData.get("error");
            throw new BusinessException(502, error == null ? "分析失败" : error.toString());
        }
        Map<String, Object> result = record.getResult();
        if (result == null) {
            throw new BusinessException(500, "分析结果为空");
        }
        String emotion = (String) result.get("emotion");
        Object conf = result.get("confidence");
        Double confidence = conf instanceof Number n ? n.doubleValue() : null;
        return new AnalysisResultVO(emotion, confidence);
    }

    private Map<String, Object> buildResult(AiPredictResponse resp) {
        Map<String, Object> result = new HashMap<>();
        result.put("emotion", resp.getEmotion());
        result.put("label", resp.getLabel());
        result.put("confidence", resp.getConfidence());
        return result;
    }
}
