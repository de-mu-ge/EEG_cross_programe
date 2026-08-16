package com.neuroai.backend.vo;

import lombok.AllArgsConstructor;
import lombok.Data;

@Data
@AllArgsConstructor
public class AnalysisResultVO {

    private String emotion;
    private Double confidence;
}
