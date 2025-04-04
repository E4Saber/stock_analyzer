-- 股票数据 - 参考数据

-- 股东户数表（stk_holdernumber）
CREATE TABLE stk_holdernumber (
    -- Primary key and identification fields
    id SERIAL PRIMARY KEY,
    ts_code VARCHAR(10) NOT NULL,
    ann_date DATE,
    end_date DATE,
    
    -- Holder number information
    holder_num INTEGER
);

-- Create indexes for frequently queried fields
CREATE INDEX idx_stk_holdernumber_ts_code ON stk_holdernumber(ts_code);
CREATE INDEX idx_stk_holdernumber_end_date ON stk_holdernumber(end_date);
CREATE INDEX idx_stk_holdernumber_ann_date ON stk_holdernumber(ann_date);

-- Add unique constraint for upsert operations
ALTER TABLE stk_holdernumber ADD CONSTRAINT stk_holdernumber_unique_key 
UNIQUE (ts_code, end_date);

-- Add table comment
COMMENT ON TABLE stk_holdernumber IS '股东户数';

-- Add column comments
COMMENT ON COLUMN stk_holdernumber.ts_code IS 'TS股票代码';
COMMENT ON COLUMN stk_holdernumber.ann_date IS '公告日期';
COMMENT ON COLUMN stk_holdernumber.end_date IS '截止日期';
COMMENT ON COLUMN stk_holdernumber.holder_num IS '股东户数';

-- 名称	类型	描述
-- ts_code	str	TS股票代码
-- ann_date	str	公告日期
-- end_date	str	截止日期
-- holder_num	int	股东户数