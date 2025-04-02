-- 股票数据 - 财报披露日期数据

-- 财报披露日期表（disclosure_date）
CREATE TABLE disclosure_date (
    -- Primary key and identification fields
    id SERIAL PRIMARY KEY,
    ts_code VARCHAR(10) NOT NULL,
    end_date DATE,
    
    -- 披露日期相关字段
    ann_date DATE,
    pre_date DATE,
    actual_date DATE,
    modify_date DATE
);

-- Create indexes for frequently queried fields
CREATE INDEX idx_disclosure_date_ts_code ON disclosure_date(ts_code);
CREATE INDEX idx_disclosure_date_end_date ON disclosure_date(end_date);
CREATE INDEX idx_disclosure_date_actual_date ON disclosure_date(actual_date);
CREATE INDEX idx_disclosure_date_pre_date ON disclosure_date(pre_date);

-- Add unique constraint for upsert operations
ALTER TABLE disclosure_date ADD CONSTRAINT disclosure_date_ts_code_end_date_key 
UNIQUE (ts_code, end_date);

-- Add table comment
COMMENT ON TABLE disclosure_date IS '财报披露日期表';

-- Add column comments
COMMENT ON COLUMN disclosure_date.ts_code IS 'TS代码';
COMMENT ON COLUMN disclosure_date.end_date IS '报告期';
COMMENT ON COLUMN disclosure_date.ann_date IS '最新披露公告日';
COMMENT ON COLUMN disclosure_date.pre_date IS '预计披露日期';
COMMENT ON COLUMN disclosure_date.actual_date IS '实际披露日期';
COMMENT ON COLUMN disclosure_date.modify_date IS '披露日期修正记录';


-- 名称	类型	默认显示	描述
-- ts_code	str	Y	TS代码
-- ann_date	str	Y	最新披露公告日
-- end_date	str	Y	报告期
-- pre_date	str	Y	预计披露日期
-- actual_date	str	Y	实际披露日期
-- modify_date	str	N	披露日期修正记录