-- 股票数据 - 行情数据

-- 周线行情（weekly）
CREATE TABLE weekly (
    id SERIAL PRIMARY KEY,                -- 自增主键
    ts_code VARCHAR(20) NOT NULL,         -- 股票代码
    trade_date DATE NOT NULL,             -- 交易日期
    close NUMERIC(12,4),                  -- 周收盘价
    open NUMERIC(12,4),                   -- 周开盘价
    high NUMERIC(12,4),                   -- 周最高价
    low NUMERIC(12,4),                    -- 周最低价
    pre_close NUMERIC(12,4),              -- 上一周收盘价
    change NUMERIC(12,4),                 -- 周涨跌额
    pct_chg NUMERIC(12,4),                -- 周涨跌幅 （未复权，如果是复权请用 通用行情接口）
    vol NUMERIC(20,2),                    -- 周成交量
    amount NUMERIC(20,4),                 -- 周成交额
    CONSTRAINT uk_weekly_ts_code_trade_date UNIQUE (ts_code, trade_date)
);

-- 表注释
COMMENT ON TABLE weekly IS '周线行情';

-- 列注释
COMMENT ON COLUMN weekly.id IS '自增主键';
COMMENT ON COLUMN weekly.ts_code IS '股票代码';
COMMENT ON COLUMN weekly.trade_date IS '交易日期';
COMMENT ON COLUMN weekly.close IS '周收盘价';
COMMENT ON COLUMN weekly.open IS '周开盘价';
COMMENT ON COLUMN weekly.high IS '周最高价';
COMMENT ON COLUMN weekly.low IS '周最低价';
COMMENT ON COLUMN weekly.pre_close IS '上一周收盘价';
COMMENT ON COLUMN weekly.change IS '周涨跌额';
COMMENT ON COLUMN weekly.pct_chg IS '周涨跌幅 （未复权，如果是复权请用 通用行情接口）';
COMMENT ON COLUMN weekly.vol IS '周成交量';
COMMENT ON COLUMN weekly.amount IS '周成交额';

-- 添加索引
CREATE INDEX idx_weekly_ts_code ON weekly(ts_code);
CREATE INDEX idx_weekly_trade_date ON weekly(trade_date);
CREATE INDEX idx_weekly_ts_code_trade_date ON weekly(ts_code, trade_date);

-- 添加外键关联到股票基本信息表
ALTER TABLE weekly 
ADD CONSTRAINT fk_weekly_stock_basic 
FOREIGN KEY (ts_code) 
REFERENCES stock_basic (ts_code);


-- 名称	类型	默认显示	描述
-- ts_code	str	Y	股票代码
-- trade_date	str	Y	交易日期
-- close	float	Y	周收盘价
-- open	float	Y	周开盘价
-- high	float	Y	周最高价
-- low	float	Y	周最低价
-- pre_close	float	Y	上一周收盘价
-- change	float	Y	周涨跌额
-- pct_chg	float	Y	周涨跌幅 （未复权，如果是复权请用 通用行情接口 ）
-- vol	float	Y	周成交量
-- amount	float	Y	周成交额