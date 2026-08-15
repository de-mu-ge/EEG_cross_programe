package com.neuroai.backend.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.baomidou.mybatisplus.extension.handlers.JacksonTypeHandler;
import lombok.Data;

import java.time.LocalDateTime;
import java.util.Map;

/**
 * EEG 分析记录表实体
 */
@Data
@TableName(value = "eeg_analysis_record", autoResultMap = true)
public class EegAnalysisRecord {

    @TableId(type = IdType.AUTO)
    private Long id;

    /** EEG 原始文件名(.dat) */
    private String fileName;

    /** 服务端存储路径 */
    private String filePath;

    /** 分析状态: WAITING/RUNNING/SUCCESS/FAILED */
    private String status;

    /** 分析结果(主导情绪), 如 {"emotion":"positive","label":0,"confidence":0.92} */
    @TableField(typeHandler = JacksonTypeHandler.class)
    private Map<String, Object> result;

    /** AI 模型返回的完整原始数据 */
    @TableField(typeHandler = JacksonTypeHandler.class)
    private Map<String, Object> modelData;

    private LocalDateTime createTime;

    private LocalDateTime updateTime;
}
