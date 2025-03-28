-- 股票数据 - 财务数据

-- 财务审计意见（fina_audit）
CREATE TABLE fina_audit (
    -- Primary key and identification fields
    id SERIAL PRIMARY KEY,
    ts_code VARCHAR(10) NOT NULL COMMENT 'TS股票代码',
    ann_date DATE COMMENT '公告日期',
    end_date DATE COMMENT '报告期',
    
    -- Audit information
    audit_result VARCHAR(100) COMMENT '审计结果',
    audit_fees NUMERIC(20,2) COMMENT '审计总费用（元）',
    audit_agency VARCHAR(200) COMMENT '会计事务所',
    audit_sign VARCHAR(200) COMMENT '签字会计师',
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for frequently queried fields
CREATE INDEX idx_fina_audit_ts_code ON fina_audit(ts_code);
CREATE INDEX idx_fina_audit_ann_date ON fina_audit(ann_date);
CREATE INDEX idx_fina_audit_end_date ON fina_audit(end_date);
CREATE INDEX idx_fina_audit_audit_result ON fina_audit(audit_result);
CREATE INDEX idx_fina_audit_audit_agency ON fina_audit(audit_agency);

-- Add table comment
COMMENT ON TABLE fina_audit IS '财务审计意见数据';


-- 名称	类型	描述
-- ts_code	str	TS股票代码
-- ann_date	str	公告日期
-- end_date	str	报告期
-- audit_result	str	审计结果
-- audit_fees	float	审计总费用（元）
-- audit_agency	str	会计事务所
-- audit_sign	str	签字会计师
