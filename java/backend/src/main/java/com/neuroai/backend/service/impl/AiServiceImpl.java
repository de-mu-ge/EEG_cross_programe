package com.neuroai.backend.service.impl;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.neuroai.backend.dto.AiPredictResponse;
import com.neuroai.backend.exception.BusinessException;
import com.neuroai.backend.properties.AiServiceProperties;
import com.neuroai.backend.service.AIService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.core.io.FileSystemResource;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatusCode;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.HttpStatusCodeException;
import org.springframework.web.client.ResourceAccessException;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestTemplate;

import java.io.File;
import java.util.List;

/**
 * 调用 Python FastAPI 推理服务：multipart 转发文件 → 解析结果
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class AiServiceImpl implements AIService {

    private static final String PREDICT_PATH = "/api/predict";

    private final RestTemplate restTemplate;
    private final AiServiceProperties aiServiceProperties;
    private final ObjectMapper objectMapper;

    @Override
    public AiPredictResponse predict(String filePath) {
        File file = new File(filePath);
        if (!file.exists()) {
            throw new BusinessException(500, "待分析文件不存在: " + filePath);
        }

        // 勿手动设置 Content-Type: multipart/form-data，交由 FormHttpMessageConverter 自动生成 boundary
        HttpHeaders headers = new HttpHeaders();
        headers.setAccept(List.of(MediaType.APPLICATION_JSON));

        MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
        body.add("file", new FileSystemResource(file));
        HttpEntity<MultiValueMap<String, Object>> request = new HttpEntity<>(body, headers);

        String url = aiServiceProperties.getBaseUrl() + PREDICT_PATH;
        log.info("调用 AI 服务: {}", url);
        long start = System.currentTimeMillis();
        try {
            ResponseEntity<String> response = restTemplate.postForEntity(url, request, String.class);
            HttpStatusCode status = response.getStatusCode();
            if (!status.is2xxSuccessful()) {
                throw new BusinessException(502, "AI 服务异常: HTTP " + status.value());
            }
            AiPredictResponse resp = objectMapper.readValue(response.getBody(), AiPredictResponse.class);
            log.info("AI 服务返回: emotion={}, label={}, confidence={}, 耗时={}ms",
                    resp.getEmotion(), resp.getLabel(), resp.getConfidence(),
                    System.currentTimeMillis() - start);
            if (!"success".equals(resp.getStatus())) {
                throw new BusinessException(502, resp.getMessage() == null ? "AI 分析失败" : resp.getMessage());
            }
            return resp;
        } catch (HttpStatusCodeException e) {
            log.error("AI 服务返回错误状态: {}", e.getStatusCode(), e);
            throw new BusinessException(502, "AI 服务异常: " + extractError(e.getResponseBodyAsString()));
        } catch (ResourceAccessException e) {
            log.error("AI 服务不可达: {}", url, e);
            throw new BusinessException(502, "AI 服务不可达，请确认 Python 服务已启动");
        } catch (RestClientException e) {
            log.error("调用 AI 服务失败", e);
            throw new BusinessException(502, "调用 AI 服务失败: " + e.getMessage());
        } catch (Exception e) {
            log.error("AI 服务响应解析失败", e);
            throw new BusinessException(502, "AI 返回结果解析失败");
        }
    }

    private String extractError(String body) {
        if (body == null || body.isBlank()) {
            return "";
        }
        try {
            JsonNode node = objectMapper.readTree(body);
            if (node.has("detail")) {
                return node.get("detail").asText();
            }
            if (node.has("message")) {
                return node.get("message").asText();
            }
        } catch (Exception ignored) {
            // 非 JSON 错误体，原样截断返回
        }
        return body.length() > 200 ? body.substring(0, 200) : body;
    }
}
