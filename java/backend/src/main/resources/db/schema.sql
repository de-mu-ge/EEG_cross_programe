-- =============================================================
-- NEURO-AI 数据库初始化脚本
-- 执行方式: mysql -uroot -p < schema.sql 或在 MySQL 客户端中执行
-- =============================================================

CREATE DATABASE IF NOT EXISTS neuroai
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE neuroai;

-- 分析记录表：一次 .dat 上传对应一条记录，状态机 WAITING -> RUNNING -> SUCCESS/FAILED
CREATE TABLE IF NOT EXISTS eeg_analysis_record (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '主键',
    file_name   VARCHAR(255) NOT NULL COMMENT 'EEG 原始文件名(.dat)',
    file_path   VARCHAR(512) NOT NULL COMMENT '服务端存储路径',
    status      VARCHAR(16)  NOT NULL DEFAULT 'WAITING' COMMENT '分析状态: WAITING/RUNNING/SUCCESS/FAILED',
    result      JSON                  DEFAULT NULL COMMENT '分析结果(主导情绪), 如 {"emotion":"positive","label":0,"confidence":0.92}',
    model_data  JSON                  DEFAULT NULL COMMENT 'AI 模型返回的完整原始数据',
    create_time DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    KEY idx_status (status),
    KEY idx_create_time (create_time)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = 'EEG分析记录表';
