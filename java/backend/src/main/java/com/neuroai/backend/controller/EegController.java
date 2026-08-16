package com.neuroai.backend.controller;

import com.neuroai.backend.service.EegAnalysisService;
import com.neuroai.backend.vo.AnalysisResultVO;
import com.neuroai.backend.vo.Result;
import com.neuroai.backend.vo.UploadResultVO;
import jakarta.validation.constraints.Positive;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

@Slf4j
@Validated
@RestController
@RequestMapping("/api/eeg")
@RequiredArgsConstructor
public class EegController {

    private final EegAnalysisService eegAnalysisService;

    /**
     * 上传 .dat 并同步完成分析
     */
    @PostMapping("/upload")
    public Result<UploadResultVO> upload(@RequestParam("file") MultipartFile file) {
        log.info("收到上传请求: file={}, size={}", file.getOriginalFilename(), file.getSize());
        UploadResultVO vo = eegAnalysisService.upload(file);
        return Result.ok("upload success", vo);
    }

    /**
     * 按 id 查询分析结果
     */
    @GetMapping("/result/{id}")
    public Result<AnalysisResultVO> result(@PathVariable("id") @Positive Long id) {
        return Result.ok(eegAnalysisService.getResult(id));
    }
}
