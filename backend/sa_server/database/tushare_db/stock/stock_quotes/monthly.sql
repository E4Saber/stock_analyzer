-- 股票数据 - 行情数据

-- 月线行情（monthly）
CREATE TABLE monthly (
    id SERIAL PRIMARY KEY,                -- 自增主键
    ts_code VARCHAR(20) NOT NULL,         -- 股票代码
    trade_date DATE NOT NULL,             -- 交易日期
    close NUMERIC(12,4),                  -- 月收盘价
    open NUMERIC(12,4),                   -- 月开盘价
    high NUMERIC(12,4),                   -- 月最高价
    low NUMERIC(12,4),                    -- 月最低价
    pre_close NUMERIC(12,4),              -- 上月收盘价
    change NUMERIC(12,4),                 -- 月涨跌额
    pct_chg NUMERIC(12,4),                -- 月涨跌幅 （未复权，如果是复权请用 通用行情接口）
    vol NUMERIC(20,2),                    -- 月成交量
    amount NUMERIC(20,4),                 -- 月成交额
    CONSTRAINT uk_monthly_ts_code_trade_date UNIQUE (ts_code, trade_date)
);

-- 表注释
COMMENT ON TABLE monthly IS '月线行情';

-- 列注释
COMMENT ON COLUMN monthly.id IS '自增主键';
COMMENT ON COLUMN monthly.ts_code IS '股票代码';
COMMENT ON COLUMN monthly.trade_date IS '交易日期';
COMMENT ON COLUMN monthly.close IS '月收盘价';
COMMENT ON COLUMN monthly.open IS '月开盘价';
COMMENT ON COLUMN monthly.high IS '月最高价';
COMMENT ON COLUMN monthly.low IS '月最低价';
COMMENT ON COLUMN monthly.pre_close IS '上月收盘价';
COMMENT ON COLUMN monthly.change IS '月涨跌额';
COMMENT ON COLUMN monthly.pct_chg IS '月涨跌幅 （未复权，如果是复权请用 通用行情接口）';
COMMENT ON COLUMN monthly.vol IS '月成交量';
COMMENT ON COLUMN monthly.amount IS '月成交额';

-- 添加索引
CREATE INDEX idx_monthly_ts_code ON monthly(ts_code);
CREATE INDEX idx_monthly_trade_date ON monthly(trade_date);
CREATE INDEX idx_monthly_ts_code_trade_date ON monthly(ts_code, trade_date);

-- 添加外键关联到股票基本信息表
ALTER TABLE monthly 
ADD CONSTRAINT fk_monthly_stock_basic 
FOREIGN KEY (ts_code) 
REFERENCES stock_basic (ts_code);


-- 名称	类型	默认显示	描述
-- ts_code	str	Y	股票代码
-- trade_date	str	Y	交易日期
-- close	float	Y	月收盘价
-- open	float	Y	月开盘价
-- high	float	Y	月最高价
-- low	float	Y	月最低价
-- pre_close	float	Y	上月收盘价
-- change	float	Y	月涨跌额
-- pct_chg	float	Y	月涨跌幅 （未复权，如果是复权请用 通用行情接口 ）
-- vol	float	Y	月成交量
-- amount	float	Y	月成交额