-- 股票数据 - 参考数据

-- 十大股东表（top10_holders）
CREATE TABLE top10_holders (
    -- Primary key and identification fields
    id SERIAL PRIMARY KEY,
    ts_code VARCHAR(10) NOT NULL,
    ann_date DATE,
    end_date DATE,
    
    -- Holder information
    holder_name VARCHAR(100) NOT NULL,
    hold_amount NUMERIC(20,4),
    hold_ratio NUMERIC(10,4),
    hold_float_ratio NUMERIC(10,4),
    hold_change NUMERIC(20,4),
    holder_type VARCHAR(50)
);

-- Create indexes for frequently queried fields
CREATE INDEX idx_top10_holders_ts_code ON top10_holders(ts_code);
CREATE INDEX idx_top10_holders_end_date ON top10_holders(end_date);
CREATE INDEX idx_top10_holders_ann_date ON top10_holders(ann_date);
CREATE INDEX idx_top10_holders_holder_name ON top10_holders(holder_name);

-- Add unique constraint for upsert operations
ALTER TABLE top10_holders ADD CONSTRAINT top10_holders_unique_key 
UNIQUE (ts_code, end_date, holder_name);

-- Add table comment
COMMENT ON TABLE top10_holders IS '十大股东';

-- Add column comments
COMMENT ON COLUMN top10_holders.ts_code IS 'TS股票代码';
COMMENT ON COLUMN top10_holders.ann_date IS '公告日期';
COMMENT ON COLUMN top10_holders.end_date IS '报告期';
COMMENT ON COLUMN top10_holders.holder_name IS '股东名称';
COMMENT ON COLUMN top10_holders.hold_amount IS '持有数量（股）';
COMMENT ON COLUMN top10_holders.hold_ratio IS '占总股本比例(%)';
COMMENT ON COLUMN top10_holders.hold_float_ratio IS '占流通股本比例(%)';
COMMENT ON COLUMN top10_holders.hold_change IS '持股变动';
COMMENT ON COLUMN top10_holders.holder_type IS '股东类型';


-- 名称	类型	描述
-- ts_code	str	TS股票代码
-- ann_date	str	公告日期
-- end_date	str	报告期
-- holder_name	str	股东名称
-- hold_amount	float	持有数量（股）
-- hold_ratio	float	占总股本比例(%)
-- hold_float_ratio	float	占流通股本比例(%)
-- hold_change	float	持股变动
-- holder_type	str	股东类型