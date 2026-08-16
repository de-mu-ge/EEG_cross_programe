package com.neuroai.backend.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;

/**
 * Python /api/predict 返回结果的解析对象
 */
@Data
public class AiPredictResponse {

    private String status;
    private String emotion;
    private Integer label;
    private Double confidence;
    @JsonProperty("elapsed_ms")
    private Long elapsedMs;
    private String message;
}
