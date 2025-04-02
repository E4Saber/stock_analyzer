-- 股票数据 - 财务审计数据

-- 财务审计表（fina_audit）
CREATE TABLE fina_audit (
    -- Primary key and identification fields
    id SERIAL PRIMARY KEY,
    ts_code VARCHAR(10) NOT NULL,
    ann_date DATE,
    end_date DATE,
    
    -- 审计相关字段
    audit_result VARCHAR(100),
    audit_fees NUMERIC(20,2),
    audit_agency VARCHAR(100),
    audit_sign VARCHAR(100)
);

-- Create indexes for frequently queried fields
CREATE INDEX idx_fina_audit_ts_code ON fina_audit(ts_code);
CREATE INDEX idx_fina_audit_end_date ON fina_audit(end_date);
CREATE INDEX idx_fina_audit_ann_date ON fina_audit(ann_date);
CREATE INDEX idx_fina_audit_audit_agency ON fina_audit(audit_agency);

-- Add unique constraint for upsert operations
ALTER TABLE fina_audit ADD CONSTRAINT fina_audit_ts_code_end_date_key 
UNIQUE (ts_code, end_date);

-- Add table comment
COMMENT ON TABLE fina_audit IS '财务审计表';

-- Add column comments
COMMENT ON COLUMN fina_audit.ts_code IS 'TS股票代码';
COMMENT ON COLUMN fina_audit.ann_date IS '公告日期';
COMMENT ON COLUMN fina_audit.end_date IS '报告期';
COMMENT ON COLUMN fina_audit.audit_result IS '审计结果';
COMMENT ON COLUMN fina_audit.audit_fees IS '审计总费用（元）';
COMMENT ON COLUMN fina_audit.audit_agency IS '会计事务所';
COMMENT ON COLUMN fina_audit.audit_sign IS '签字会计师';


-- 名称	类型	描述
-- ts_code	str	TS股票代码
-- ann_date	str	公告日期
-- end_date	str	报告期
-- audit_result	str	审计结果
-- audit_fees	float	审计总费用（元）
-- audit_agency	str	会计事务所
-- audit_sign	str	签字会计师