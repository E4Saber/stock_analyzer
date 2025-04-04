-- 股票数据 - 参考数据

-- 限售股解禁表（share_float）
CREATE TABLE share_float (
    -- Primary key and identification fields
    id SERIAL PRIMARY KEY,
    ts_code VARCHAR(10) NOT NULL,
    ann_date DATE,
    float_date DATE,
    
    -- Share float information
    float_share NUMERIC(20,4),    -- 流通股份(股)
    float_ratio NUMERIC(10,4),    -- 流通股份占总股本比率
    holder_name VARCHAR(100),     -- 股东名称
    share_type VARCHAR(50)        -- 股份类型
);

-- Create indexes for frequently queried fields
CREATE INDEX idx_share_float_ts_code ON share_float(ts_code);
CREATE INDEX idx_share_float_ann_date ON share_float(ann_date);
CREATE INDEX idx_share_float_float_date ON share_float(float_date);
CREATE INDEX idx_share_float_holder_name ON share_float(holder_name);

-- Add unique constraint for upsert operations
ALTER TABLE share_float ADD CONSTRAINT share_float_unique_key 
UNIQUE (ts_code, ann_date, float_date, holder_name);

-- Add table comment
COMMENT ON TABLE share_float IS '限售股解禁';

-- Add column comments
COMMENT ON COLUMN share_float.ts_code IS 'TS股票代码';
COMMENT ON COLUMN share_float.ann_date IS '公告日期';
COMMENT ON COLUMN share_float.float_date IS '解禁日期';
COMMENT ON COLUMN share_float.float_share IS '流通股份(股)';
COMMENT ON COLUMN share_float.float_ratio IS '流通股份占总股本比率';
COMMENT ON COLUMN share_float.holder_name IS '股东名称';
COMMENT ON COLUMN share_float.share_type IS '股份类型';

-- 名称	类型	描述
-- ts_code	str	TS代码
-- ann_date	str	公告日期
-- float_date	str	解禁日期
-- float_share	float	流通股份(股)
-- float_ratio	float	流通股份占总股本比率
-- holder_name	str	股东名称
-- share_type	str	股份类型