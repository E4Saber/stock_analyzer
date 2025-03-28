-- 股票数据 - 行情数据

-- 股票周/月线行情(每日更新)（stk_weekly_monthly）
CREATE TABLE stk_weekly_monthly (
    id SERIAL PRIMARY KEY,                -- 自增主键
    ts_code VARCHAR(20) NOT NULL,         -- 股票代码
    trade_date DATE NOT NULL,             -- 交易日期
    freq VARCHAR(5) NOT NULL,             -- 频率(周week,月month)
    open NUMERIC(12,4),                   -- (周/月)开盘价
    high NUMERIC(12,4),                   -- (周/月)最高价
    low NUMERIC(12,4),                    -- (周/月)最低价
    close NUMERIC(12,4),                  -- (周/月)收盘价
    pre_close NUMERIC(12,4),              -- 上一(周/月)收盘价
    vol NUMERIC(20,2),                    -- (周/月)成交量
    amount NUMERIC(20,4),                 -- (周/月)成交额
    change NUMERIC(12,4),                 -- (周/月)涨跌额
    pct_chg NUMERIC(12,4),                -- (周/月)涨跌幅(未复权,如果是复权请用 通用行情接口)
    CONSTRAINT uk_stk_weekly_monthly_ts_code_trade_date_freq UNIQUE (ts_code, trade_date, freq),
    CONSTRAINT ck_stk_weekly_monthly_freq CHECK (freq IN ('week', 'month'))
);

-- 表注释
COMMENT ON TABLE stk_weekly_monthly IS '周/月线行情合并表';

-- 列注释
COMMENT ON COLUMN stk_weekly_monthly.id IS '自增主键';
COMMENT ON COLUMN stk_weekly_monthly.ts_code IS '股票代码';
COMMENT ON COLUMN stk_weekly_monthly.trade_date IS '交易日期';
COMMENT ON COLUMN stk_weekly_monthly.freq IS '频率(周week,月month)';
COMMENT ON COLUMN stk_weekly_monthly.open IS '(周/月)开盘价';
COMMENT ON COLUMN stk_weekly_monthly.high IS '(周/月)最高价';
COMMENT ON COLUMN stk_weekly_monthly.low IS '(周/月)最低价';
COMMENT ON COLUMN stk_weekly_monthly.close IS '(周/月)收盘价';
COMMENT ON COLUMN stk_weekly_monthly.pre_close IS '上一(周/月)收盘价';
COMMENT ON COLUMN stk_weekly_monthly.vol IS '(周/月)成交量';
COMMENT ON COLUMN stk_weekly_monthly.amount IS '(周/月)成交额';
COMMENT ON COLUMN stk_weekly_monthly.change IS '(周/月)涨跌额';
COMMENT ON COLUMN stk_weekly_monthly.pct_chg IS '(周/月)涨跌幅(未复权,如果是复权请用 通用行情接口)';

-- 添加索引
CREATE INDEX idx_stk_weekly_monthly_ts_code ON stk_weekly_monthly(ts_code);
CREATE INDEX idx_stk_weekly_monthly_trade_date ON stk_weekly_monthly(trade_date);
CREATE INDEX idx_stk_weekly_monthly_freq ON stk_weekly_monthly(freq);
CREATE INDEX idx_stk_weekly_monthly_ts_code_trade_date ON stk_weekly_monthly(ts_code, trade_date);
CREATE INDEX idx_stk_weekly_monthly_ts_code_freq ON stk_weekly_monthly(ts_code, freq);

-- 添加外键关联到股票基本信息表
ALTER TABLE stk_weekly_monthly 
ADD CONSTRAINT fk_stk_weekly_monthly_stock_basic 
FOREIGN KEY (ts_code) 
REFERENCES stock_basic (ts_code);

-- 可选：创建视图，方便单独查询周数据或月数据
CREATE VIEW view_weekly AS
SELECT * FROM stk_weekly_monthly WHERE freq = 'week';

CREATE VIEW view_monthly AS
SELECT * FROM stk_weekly_monthly WHERE freq = 'month';


-- 名称	类型	默认显示	描述
-- ts_code	str	Y	股票代码
-- trade_date	str	Y	交易日期
-- freq	str	Y	频率(周week,月month)
-- open	float	Y	(周/月)开盘价
-- high	float	Y	(周/月)最高价
-- low	float	Y	(周/月)最低价
-- close	float	Y	(周/月)收盘价
-- pre_close	float	Y	上一(周/月)收盘价
-- vol	float	Y	(周/月)成交量
-- amount	float	Y	(周/月)成交额
-- change	float	Y	(周/月)涨跌额
-- pct_chg	float	Y	(周/月)涨跌幅(未复权,如果是复权请用 通用行情接口)