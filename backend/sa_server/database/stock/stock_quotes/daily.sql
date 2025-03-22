-- 股票数据 - 行情数据

-- 日线行情（daily）
CREATE TABLE daily (
    id SERIAL PRIMARY KEY,                -- 自增主键
    ts_code VARCHAR(20) NOT NULL,         -- 股票代码
    trade_date DATE NOT NULL,             -- 交易日期
    open NUMERIC(12,4),                   -- 开盘价
    high NUMERIC(12,4),                   -- 最高价
    low NUMERIC(12,4),                    -- 最低价
    close NUMERIC(12,4),                  -- 收盘价
    pre_close NUMERIC(12,4),              -- 昨收价【除权价，前复权】
    change NUMERIC(12,4),                 -- 涨跌额
    pct_chg NUMERIC(12,4),                -- 涨跌幅 【基于除权后的昨收计算的涨跌幅：（今收-除权昨收）/除权昨收】
    vol NUMERIC(20,2),                    -- 成交量（手）
    amount NUMERIC(20,4),                 -- 成交额（千元）
    CONSTRAINT uk_daily_ts_code_trade_date UNIQUE (ts_code, trade_date)
);

-- 表注释
COMMENT ON TABLE daily IS '日线行情';

-- 列注释
COMMENT ON COLUMN daily.id IS '自增主键';
COMMENT ON COLUMN daily.ts_code IS '股票代码';
COMMENT ON COLUMN daily.trade_date IS '交易日期';
COMMENT ON COLUMN daily.open IS '开盘价';
COMMENT ON COLUMN daily.high IS '最高价';
COMMENT ON COLUMN daily.low IS '最低价';
COMMENT ON COLUMN daily.close IS '收盘价';
COMMENT ON COLUMN daily.pre_close IS '昨收价【除权价，前复权】';
COMMENT ON COLUMN daily.change IS '涨跌额';
COMMENT ON COLUMN daily.pct_chg IS '涨跌幅 【基于除权后的昨收计算的涨跌幅：（今收-除权昨收）/除权昨收】';
COMMENT ON COLUMN daily.vol IS '成交量（手）';
COMMENT ON COLUMN daily.amount IS '成交额（千元）';

-- 添加索引
CREATE INDEX idx_daily_ts_code ON daily(ts_code);
CREATE INDEX idx_daily_trade_date ON daily(trade_date);
CREATE INDEX idx_daily_ts_code_trade_date ON daily(ts_code, trade_date);

-- 添加外键关联到股票基本信息表
ALTER TABLE daily 
ADD CONSTRAINT fk_daily_stock_basic 
FOREIGN KEY (ts_code) 
REFERENCES stock_basic (ts_code);


-- 名称	类型	描述
-- ts_code	str	股票代码
-- trade_date	str	交易日期
-- open	float	开盘价
-- high	float	最高价
-- low	float	最低价
-- close	float	收盘价
-- pre_close	float	昨收价【除权价，前复权】
-- change	float	涨跌额
-- pct_chg	float	涨跌幅 【基于除权后的昨收计算的涨跌幅：（今收-除权昨收）/除权昨收 】
-- vol	float	成交量 （手）
-- amount	float	成交额 （千元）