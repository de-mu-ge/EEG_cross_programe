package com.neuroai.backend.properties;

import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;

/**
 * 文件存储配置，对应 application.yml 的 neuroai.storage.*
 */
@Data
@ConfigurationProperties(prefix = "neuroai.storage")
public class StorageProperties {

    /** 上传文件存放目录 */
    private String uploadDir;
}
