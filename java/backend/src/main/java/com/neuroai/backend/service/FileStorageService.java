package com.neuroai.backend.service;

import com.neuroai.backend.exception.BusinessException;
import com.neuroai.backend.properties.StorageProperties;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.UUID;

/**
 * 上传文件存储：校验并保存 .dat 到 uploadDir/yyyyMMdd/uuid.dat
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class FileStorageService {

    private static final long MAX_FILE_SIZE = 200L * 1024 * 1024;

    private final StorageProperties storageProperties;

    /**
     * 校验并保存文件，返回服务端存储路径
     */
    public String store(MultipartFile file) {
        String originalName = file.getOriginalFilename();
        if (!StringUtils.hasText(originalName) || !originalName.toLowerCase().endsWith(".dat")) {
            throw new BusinessException(400, "仅支持 .dat 文件");
        }
        if (file.isEmpty()) {
            throw new BusinessException(400, "文件内容为空");
        }
        if (file.getSize() > MAX_FILE_SIZE) {
            throw new BusinessException(400, "文件大小超过限制(200MB)");
        }

        String dateDir = LocalDate.now().format(DateTimeFormatter.ofPattern("yyyyMMdd"));
        String fileName = UUID.randomUUID().toString().replace("-", "") + ".dat";
        Path dir = Paths.get(storageProperties.getUploadDir(), dateDir);
        Path target = dir.resolve(fileName);
        try {
            Files.createDirectories(dir);
            file.transferTo(target);
            log.info("文件已保存: {} -> {}", originalName, target);
            return target.toString();
        } catch (IOException e) {
            log.error("文件保存失败: {}", originalName, e);
            throw new BusinessException(500, "文件保存失败: " + e.getMessage());
        }
    }
}
