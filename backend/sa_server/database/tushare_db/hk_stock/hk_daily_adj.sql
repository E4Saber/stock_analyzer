-- 香港股票复权日线行情表（hk_daily_adj）
CREATE TABLE hk_daily_adj (
    -- Primary key and identification fields
    id SERIAL PRIMARY KEY,
    ts_code VARCHAR(12) NOT NULL,
    trade_date DATE NOT NULL,
    
    -- Price data
    open FLOAT,
    high FLOAT,
    low FLOAT,
    close FLOAT,
    pre_close FLOAT,
    change FLOAT,
    pct_change FLOAT,
    
    -- Volume and amount
    vol BIGINT,
    amount FLOAT,
    vwap FLOAT,
    
    -- Adjustment factor
    adj_factor FLOAT,
    
    -- Share data
    turnover_ratio FLOAT,
    free_share BIGINT,
    total_share BIGINT,
    
    -- Market value
    free_mv FLOAT,
    total_mv FLOAT,
    
    -- Add constraints
    CONSTRAINT hk_daily_adj_unique_key UNIQUE (ts_code, trade_date)
);

-- Create indexes for frequently queried fields
CREATE INDEX idx_hk_daily_adj_ts_code ON hk_daily_adj(ts_code);
CREATE INDEX idx_hk_daily_adj_trade_date ON hk_daily_adj(trade_date);
CREATE INDEX idx_hk_daily_adj_ts_code_trade_date ON hk_daily_adj(ts_code, trade_date);

-- Add table comment
COMMENT ON TABLE hk_daily_adj IS '香港股票复权日线行情';

-- Add column comments
COMMENT ON COLUMN hk_daily_adj.ts_code IS '股票代码';
COMMENT ON COLUMN hk_daily_adj.trade_date IS '交易日期';
COMMENT ON COLUMN hk_daily_adj.open IS '开盘价';
COMMENT ON COLUMN hk_daily_adj.high IS '最高价';
COMMENT ON COLUMN hk_daily_adj.low IS '最低价';
COMMENT ON COLUMN hk_daily_adj.close IS '收盘价';
COMMENT ON COLUMN hk_daily_adj.pre_close IS '昨收价';
COMMENT ON COLUMN hk_daily_adj.change IS '涨跌额';
COMMENT ON COLUMN hk_daily_adj.pct_change IS '涨跌幅';
COMMENT ON COLUMN hk_daily_adj.vol IS '成交量';
COMMENT ON COLUMN hk_daily_adj.amount IS '成交额';
COMMENT ON COLUMN hk_daily_adj.vwap IS '平均价';
COMMENT ON COLUMN hk_daily_adj.adj_factor IS '复权因子';
COMMENT ON COLUMN hk_daily_adj.turnover_ratio IS '换手率';
COMMENT ON COLUMN hk_daily_adj.free_share IS '流通股本';
COMMENT ON COLUMN hk_daily_adj.total_share IS '总股本';
COMMENT ON COLUMN hk_daily_adj.free_mv IS '流通市值';
COMMENT ON COLUMN hk_daily_adj.total_mv IS '总市值';


-- 名称	类型	默认显示	描述
-- ts_code	str	Y	股票代码
-- trade_date	str	Y	交易日期
-- close	float	Y	收盘价
-- open	float	Y	开盘价
-- high	float	Y	最高价
-- low	float	Y	最低价
-- pre_close	float	Y	昨收价
-- change	float	Y	涨跌额
-- pct_change	float	Y	涨跌幅
-- vol	None	Y	成交量
-- amount	float	Y	成交额
-- vwap	float	Y	平均价
-- adj_factor	float	Y	复权因子
-- turnover_ratio	float	Y	换手率
-- free_share	None	Y	流通股本
-- total_share	None	Y	总股本
-- free_mv	float	Y	流通市值
-- total_mv	float	Y	总市值