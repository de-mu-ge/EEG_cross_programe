package com.neuroai.backend.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.neuroai.backend.entity.EegAnalysisRecord;
import com.neuroai.backend.vo.AnalysisResultVO;
import com.neuroai.backend.vo.UploadResultVO;
import org.springframework.web.multipart.MultipartFile;

public interface EegAnalysisService extends IService<EegAnalysisRecord> {

    /**
     * 上传 .dat 并同步完成分析，返回分析记录 id
     */
    UploadResultVO upload(MultipartFile file);

    /**
     * 按 id 查询分析结果
     */
    AnalysisResultVO getResult(Long id);
}
