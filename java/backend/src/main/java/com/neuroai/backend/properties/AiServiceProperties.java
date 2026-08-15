package com.neuroai.backend.properties;

import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;

/**
 * Python AI 服务连接配置，对应 application.yml 的 neuroai.ai-service.*
 */
@Data
@ConfigurationProperties(prefix = "neuroai.ai-service")
public class AiServiceProperties {

    /** Python FastAPI 服务地址 */
    private String baseUrl;

    private int connectTimeoutMs = 5000;

    private int readTimeoutMs = 60000;
}
