-- 指数数据

-- 指数日线行情（index_daily）
CREATE TABLE index_daily (
    id SERIAL PRIMARY KEY,               -- 自增主键
    ts_code VARCHAR(20) NOT NULL,        -- TS指数代码
    trade_date DATE NOT NULL,            -- 交易日
    close FLOAT,                         -- 收盘点位
    open FLOAT,                          -- 开盘点位
    high FLOAT,                          -- 最高点位
    low FLOAT,                           -- 最低点位
    pre_close FLOAT,                     -- 昨日收盘点
    change FLOAT,                        -- 涨跌点
    pct_chg FLOAT,                       -- 涨跌幅（%）
    vol FLOAT,                           -- 成交量（手）
    amount FLOAT                         -- 成交额（千元）
);

-- 表注释
COMMENT ON TABLE index_daily IS '指数日线行情';

-- 列注释
COMMENT ON COLUMN index_daily.id IS '自增主键';
COMMENT ON COLUMN index_daily.ts_code IS 'TS指数代码';
COMMENT ON COLUMN index_daily.trade_date IS '交易日';
COMMENT ON COLUMN index_daily.close IS '收盘点位';
COMMENT ON COLUMN index_daily.open IS '开盘点位';
COMMENT ON COLUMN index_daily.high IS '最高点位';
COMMENT ON COLUMN index_daily.low IS '最低点位';
COMMENT ON COLUMN index_daily.pre_close IS '昨日收盘点';
COMMENT ON COLUMN index_daily.change IS '涨跌点';
COMMENT ON COLUMN index_daily.pct_chg IS '涨跌幅（%）';
COMMENT ON COLUMN index_daily.vol IS '成交量（手）';
COMMENT ON COLUMN index_daily.amount IS '成交额（千元）';

-- 添加索引
CREATE INDEX idx_index_daily_ts_code ON index_daily(ts_code);
CREATE INDEX idx_index_daily_trade_date ON index_daily(trade_date);
CREATE INDEX idx_index_daily_ts_code_trade_date ON index_daily(ts_code, trade_date);

-- 添加外键约束
ALTER TABLE index_daily ADD CONSTRAINT fk_index_daily_ts_code 
    FOREIGN KEY (ts_code) REFERENCES index_basic(ts_code);

-- 注意：这里添加了复合唯一约束，确保每个指数每天只有一条记录
ALTER TABLE index_daily ADD CONSTRAINT uk_index_daily_ts_code_trade_date 
    UNIQUE (ts_code, trade_date);


-- 名称	类型	描述
-- ts_code	str	TS指数代码
-- trade_date	str	交易日
-- close	float	收盘点位
-- open	float	开盘点位
-- high	float	最高点位
-- low	float	最低点位
-- pre_close	float	昨日收盘点
-- change	float	涨跌点
-- pct_chg	float	涨跌幅（%）
-- vol	float	成交量（手）
-- amount	float	成交额（千元）