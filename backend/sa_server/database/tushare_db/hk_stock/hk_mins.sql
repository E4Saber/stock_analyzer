-- 香港股票分钟行情表（hk_mins）
CREATE TABLE hk_mins (
    -- Primary key and identification fields
    id SERIAL PRIMARY KEY,
    ts_code VARCHAR(12) NOT NULL,
    trade_time TIMESTAMP NOT NULL,
    freq VARCHAR(10) NOT NULL,
    
    -- Price data
    open FLOAT,
    high FLOAT,
    low FLOAT,
    close FLOAT,
    
    -- Volume and amount
    vol BIGINT,
    amount FLOAT,
    
    -- Add constraints
    CONSTRAINT hk_mins_unique_key UNIQUE (ts_code, trade_time, freq)
);

-- Create indexes for frequently queried fields
CREATE INDEX idx_hk_mins_ts_code ON hk_mins(ts_code);
CREATE INDEX idx_hk_mins_trade_time ON hk_mins(trade_time);
CREATE INDEX idx_hk_mins_freq ON hk_mins(freq);
CREATE INDEX idx_hk_mins_ts_code_freq ON hk_mins(ts_code, freq);
CREATE INDEX idx_hk_mins_ts_code_trade_time_freq ON hk_mins(ts_code, trade_time, freq);

-- Add table comment
COMMENT ON TABLE hk_mins IS '香港股票分钟行情';

-- Add column comments
COMMENT ON COLUMN hk_mins.ts_code IS '股票代码';
COMMENT ON COLUMN hk_mins.trade_time IS '交易时间';
COMMENT ON COLUMN hk_mins.freq IS '分钟频度（1min/5min/15min/30min/60min）';
COMMENT ON COLUMN hk_mins.open IS '开盘价';
COMMENT ON COLUMN hk_mins.high IS '最高价';
COMMENT ON COLUMN hk_mins.low IS '最低价';
COMMENT ON COLUMN hk_mins.close IS '收盘价';
COMMENT ON COLUMN hk_mins.vol IS '成交量';
COMMENT ON COLUMN hk_mins.amount IS '成交金额';



-- 名称	类型	默认显示	描述
-- ts_code	str	Y	股票代码
-- trade_time	str	Y	交易时间
-- open	float	Y	开盘价
-- close	float	Y	收盘价
-- high	float	Y	最高价
-- low	float	Y	最低价
-- vol	int	Y	成交量
-- amount	float	Y	成交金额