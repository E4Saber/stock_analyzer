-- 股票数据 - 财务数据

-- 财报披露计划（disclosure_date）
CREATE TABLE disclosure_date (
    -- Primary key and identification fields
    id SERIAL PRIMARY KEY,
    ts_code VARCHAR(10) NOT NULL COMMENT 'TS代码',
    
    -- Disclosure dates
    ann_date DATE COMMENT '最新披露公告日',
    end_date DATE COMMENT '报告期',
    pre_date DATE COMMENT '预计披露日期',
    actual_date DATE COMMENT '实际披露日期',
    modify_date DATE COMMENT '披露日期修正记录',
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for frequently queried fields
CREATE INDEX idx_disclosure_date_ts_code ON disclosure_date(ts_code);
CREATE INDEX idx_disclosure_date_end_date ON disclosure_date(end_date);
CREATE INDEX idx_disclosure_date_pre_date ON disclosure_date(pre_date);
CREATE INDEX idx_disclosure_date_actual_date ON disclosure_date(actual_date);

-- Add table comment
COMMENT ON TABLE disclosure_date IS '财报披露计划数据';


-- 名称	类型	默认显示	描述
-- ts_code	str	Y	TS代码
-- ann_date	str	Y	最新披露公告日
-- end_date	str	Y	报告期
-- pre_date	str	Y	预计披露日期
-- actual_date	str	Y	实际披露日期
-- modify_date	str	N	披露日期修正记录
