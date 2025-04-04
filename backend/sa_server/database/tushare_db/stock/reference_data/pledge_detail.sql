-- 股票数据 - 参考数据

-- 股票质押明细表（pledge_detail）
CREATE TABLE pledge_detail (
    -- Primary key and identification fields
    id SERIAL PRIMARY KEY,
    ts_code VARCHAR(10) NOT NULL,
    ann_date DATE,
    holder_name VARCHAR(100) NOT NULL,
    
    -- Pledge information
    pledge_amount NUMERIC(20,4),    -- 质押数量（万股）
    start_date DATE,                -- 质押开始日期
    end_date DATE,                  -- 质押结束日期
    is_release VARCHAR(1),          -- 是否已解押
    release_date DATE,              -- 解押日期
    pledgor VARCHAR(100),           -- 质押方
    
    -- Holdings information
    holding_amount NUMERIC(20,4),   -- 持股总数（万股）
    pledged_amount NUMERIC(20,4),   -- 质押总数（万股）
    p_total_ratio NUMERIC(10,4),    -- 本次质押占总股本比例
    h_total_ratio NUMERIC(10,4),    -- 持股总数占总股本比例
    is_buyback VARCHAR(1)           -- 是否回购
);

-- Create indexes for frequently queried fields
CREATE INDEX idx_pledge_detail_ts_code ON pledge_detail(ts_code);
CREATE INDEX idx_pledge_detail_ann_date ON pledge_detail(ann_date);
CREATE INDEX idx_pledge_detail_holder_name ON pledge_detail(holder_name);
CREATE INDEX idx_pledge_detail_is_release ON pledge_detail(is_release);
CREATE INDEX idx_pledge_detail_start_date ON pledge_detail(start_date);
CREATE INDEX idx_pledge_detail_end_date ON pledge_detail(end_date);

-- Add unique constraint for upsert operations (assuming these fields together create a unique record)
ALTER TABLE pledge_detail ADD CONSTRAINT pledge_detail_unique_key 
UNIQUE (ts_code, ann_date, holder_name, start_date, pledgor);

-- Add table comment
COMMENT ON TABLE pledge_detail IS '股票质押明细';

-- Add column comments
COMMENT ON COLUMN pledge_detail.ts_code IS 'TS股票代码';
COMMENT ON COLUMN pledge_detail.ann_date IS '公告日期';
COMMENT ON COLUMN pledge_detail.holder_name IS '股东名称';
COMMENT ON COLUMN pledge_detail.pledge_amount IS '质押数量（万股）';
COMMENT ON COLUMN pledge_detail.start_date IS '质押开始日期';
COMMENT ON COLUMN pledge_detail.end_date IS '质押结束日期';
COMMENT ON COLUMN pledge_detail.is_release IS '是否已解押';
COMMENT ON COLUMN pledge_detail.release_date IS '解押日期';
COMMENT ON COLUMN pledge_detail.pledgor IS '质押方';
COMMENT ON COLUMN pledge_detail.holding_amount IS '持股总数（万股）';
COMMENT ON COLUMN pledge_detail.pledged_amount IS '质押总数（万股）';
COMMENT ON COLUMN pledge_detail.p_total_ratio IS '本次质押占总股本比例';
COMMENT ON COLUMN pledge_detail.h_total_ratio IS '持股总数占总股本比例';
COMMENT ON COLUMN pledge_detail.is_buyback IS '是否回购';

-- 名称	类型	描述
-- ts_code	str	TS股票代码
-- ann_date	str	公告日期
-- holder_name	str	股东名称
-- pledge_amount	float	质押数量（万股）
-- start_date	str	质押开始日期
-- end_date	str	质押结束日期
-- is_release	str	是否已解押
-- release_date	str	解押日期
-- pledgor	str	质押方
-- holding_amount	float	持股总数（万股）
-- pledged_amount	float	质押总数（万股）
-- p_total_ratio	float	本次质押占总股本比例
-- h_total_ratio	float	持股总数占总股本比例
-- is_buyback	str	是否回购