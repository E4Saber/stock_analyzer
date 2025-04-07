-- 香港股票日线行情表（hk_daily）
CREATE TABLE hk_daily (
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
    pct_chg FLOAT,
    
    -- Volume and amount
    vol FLOAT,
    amount FLOAT,
    
    -- Add constraints
    CONSTRAINT hk_daily_unique_key UNIQUE (ts_code, trade_date)
);

-- Create indexes for frequently queried fields
CREATE INDEX idx_hk_daily_ts_code ON hk_daily(ts_code);
CREATE INDEX idx_hk_daily_trade_date ON hk_daily(trade_date);
CREATE INDEX idx_hk_daily_ts_code_trade_date ON hk_daily(ts_code, trade_date);

-- Add table comment
COMMENT ON TABLE hk_daily IS '香港股票日线行情';

-- Add column comments
COMMENT ON COLUMN hk_daily.ts_code IS '股票代码';
COMMENT ON COLUMN hk_daily.trade_date IS '交易日期';
COMMENT ON COLUMN hk_daily.open IS '开盘价';
COMMENT ON COLUMN hk_daily.high IS '最高价';
COMMENT ON COLUMN hk_daily.low IS '最低价';
COMMENT ON COLUMN hk_daily.close IS '收盘价';
COMMENT ON COLUMN hk_daily.pre_close IS '昨收价';
COMMENT ON COLUMN hk_daily.change IS '涨跌额';
COMMENT ON COLUMN hk_daily.pct_chg IS '涨跌幅(%)';
COMMENT ON COLUMN hk_daily.vol IS '成交量(股)';
COMMENT ON COLUMN hk_daily.amount IS '成交额(元)';


-- 名称	类型	默认显示	描述
-- ts_code	str	Y	股票代码
-- trade_date	str	Y	交易日期
-- open	float	Y	开盘价
-- high	float	Y	最高价
-- low	float	Y	最低价
-- close	float	Y	收盘价
-- pre_close	float	Y	昨收价
-- change	float	Y	涨跌额
-- pct_chg	float	Y	涨跌幅(%)
-- vol	float	Y	成交量(股)
-- amount	float	Y	成交额(元)