-- 股票数据 - 参考数据

-- 股票质押统计表（pledge_stat）
CREATE TABLE pledge_stat (
    -- Primary key and identification fields
    id SERIAL PRIMARY KEY,
    ts_code VARCHAR(10) NOT NULL,
    end_date DATE,
    
    -- Pledge statistics
    pledge_count INTEGER,
    unrest_pledge NUMERIC(20,4),  -- 无限售股质押数量（万）
    rest_pledge NUMERIC(20,4),    -- 限售股份质押数量（万）
    total_share NUMERIC(20,4),    -- 总股本
    pledge_ratio NUMERIC(10,4)    -- 质押比例
);

-- Create indexes for frequently queried fields
CREATE INDEX idx_pledge_stat_ts_code ON pledge_stat(ts_code);
CREATE INDEX idx_pledge_stat_end_date ON pledge_stat(end_date);

-- Add unique constraint for upsert operations
ALTER TABLE pledge_stat ADD CONSTRAINT pledge_stat_unique_key 
UNIQUE (ts_code, end_date);

-- Add table comment
COMMENT ON TABLE pledge_stat IS '股票质押统计';

-- Add column comments
COMMENT ON COLUMN pledge_stat.ts_code IS 'TS股票代码';
COMMENT ON COLUMN pledge_stat.end_date IS '截止日期';
COMMENT ON COLUMN pledge_stat.pledge_count IS '质押次数';
COMMENT ON COLUMN pledge_stat.unrest_pledge IS '无限售股质押数量（万）';
COMMENT ON COLUMN pledge_stat.rest_pledge IS '限售股份质押数量（万）';
COMMENT ON COLUMN pledge_stat.total_share IS '总股本';
COMMENT ON COLUMN pledge_stat.pledge_ratio IS '质押比例';

-- 名称	类型	描述
-- ts_code	str	TS代码
-- end_date	str	截止日期
-- pledge_count	int	质押次数
-- unrest_pledge	float	无限售股质押数量（万）
-- rest_pledge	float	限售股份质押数量（万）
-- total_share	float	总股本
-- pledge_ratio	float	质押比例