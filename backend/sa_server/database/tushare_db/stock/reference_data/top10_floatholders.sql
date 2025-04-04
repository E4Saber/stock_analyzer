-- 股票数据 - 参考数据

-- 十大流通股东表（top10_floatholders）
CREATE TABLE top10_floatholders (
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
CREATE INDEX idx_top10_floatholders_ts_code ON top10_floatholders(ts_code);
CREATE INDEX idx_top10_floatholders_end_date ON top10_floatholders(end_date);
CREATE INDEX idx_top10_floatholders_ann_date ON top10_floatholders(ann_date);
CREATE INDEX idx_top10_floatholders_holder_name ON top10_floatholders(holder_name);

-- Add unique constraint for upsert operations
ALTER TABLE top10_floatholders ADD CONSTRAINT top10_floatholders_unique_key 
UNIQUE (ts_code, end_date, holder_name);

-- Add table comment
COMMENT ON TABLE top10_floatholders IS '十大流通股东';

-- Add column comments
COMMENT ON COLUMN top10_floatholders.ts_code IS 'TS股票代码';
COMMENT ON COLUMN top10_floatholders.ann_date IS '公告日期';
COMMENT ON COLUMN top10_floatholders.end_date IS '报告期';
COMMENT ON COLUMN top10_floatholders.holder_name IS '股东名称';
COMMENT ON COLUMN top10_floatholders.hold_amount IS '持有数量（股）';
COMMENT ON COLUMN top10_floatholders.hold_ratio IS '占总股本比例(%)';
COMMENT ON COLUMN top10_floatholders.hold_float_ratio IS '占流通股本比例(%)';
COMMENT ON COLUMN top10_floatholders.hold_change IS '持股变动';
COMMENT ON COLUMN top10_floatholders.holder_type IS '股东类型';

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