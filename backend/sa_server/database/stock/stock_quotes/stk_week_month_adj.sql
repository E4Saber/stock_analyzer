-- 股票数据 - 行情数据

-- 股票周/月线行情(复权--每日更新)（stk_week_month_adj）
CREATE TABLE stk_week_month_adj (
    id SERIAL PRIMARY KEY,                -- 自增主键
    ts_code VARCHAR(20) NOT NULL,         -- 股票代码
    trade_date DATE NOT NULL,             -- 交易日期
    freq VARCHAR(5) NOT NULL,             -- 频率(周week,月month)
    open NUMERIC(12,4),                   -- (周/月)开盘价
    high NUMERIC(12,4),                   -- (周/月)最高价
    low NUMERIC(12,4),                    -- (周/月)最低价
    close NUMERIC(12,4),                  -- (周/月)收盘价
    pre_close NUMERIC(12,4),              -- 上一(周/月)收盘价【除权价，前复权】
    open_qfq NUMERIC(12,4),               -- 前复权(周/月)开盘价
    high_qfq NUMERIC(12,4),               -- 前复权(周/月)最高价
    low_qfq NUMERIC(12,4),                -- 前复权(周/月)最低价
    close_qfq NUMERIC(12,4),              -- 前复权(周/月)收盘价
    open_hfq NUMERIC(12,4),               -- 后复权(周/月)开盘价
    high_hfq NUMERIC(12,4),               -- 后复权(周/月)最高价
    low_hfq NUMERIC(12,4),                -- 后复权(周/月)最低价
    close_hfq NUMERIC(12,4),              -- 后复权(周/月)收盘价
    vol NUMERIC(20,2),                    -- (周/月)成交量
    amount NUMERIC(20,4),                 -- (周/月)成交额
    change NUMERIC(12,4),                 -- (周/月)涨跌额
    pct_chg NUMERIC(12,4),                -- (周/月)涨跌幅 【基于除权后的昨收计算的涨跌幅：（今收-除权昨收）/除权昨收】
    CONSTRAINT uk_stk_week_month_adj_ts_code_trade_date_freq UNIQUE (ts_code, trade_date, freq),
    CONSTRAINT ck_stk_week_month_adj_freq CHECK (freq IN ('week', 'month'))
);

-- 表注释
COMMENT ON TABLE stk_week_month_adj IS '周/月线行情(含前后复权)';

-- 列注释
COMMENT ON COLUMN stk_week_month_adj.id IS '自增主键';
COMMENT ON COLUMN stk_week_month_adj.ts_code IS '股票代码';
COMMENT ON COLUMN stk_week_month_adj.trade_date IS '交易日期';
COMMENT ON COLUMN stk_week_month_adj.freq IS '频率(周week,月month)';
COMMENT ON COLUMN stk_week_month_adj.open IS '(周/月)开盘价';
COMMENT ON COLUMN stk_week_month_adj.high IS '(周/月)最高价';
COMMENT ON COLUMN stk_week_month_adj.low IS '(周/月)最低价';
COMMENT ON COLUMN stk_week_month_adj.close IS '(周/月)收盘价';
COMMENT ON COLUMN stk_week_month_adj.pre_close IS '上一(周/月)收盘价【除权价，前复权】';
COMMENT ON COLUMN stk_week_month_adj.open_qfq IS '前复权(周/月)开盘价';
COMMENT ON COLUMN stk_week_month_adj.high_qfq IS '前复权(周/月)最高价';
COMMENT ON COLUMN stk_week_month_adj.low_qfq IS '前复权(周/月)最低价';
COMMENT ON COLUMN stk_week_month_adj.close_qfq IS '前复权(周/月)收盘价';
COMMENT ON COLUMN stk_week_month_adj.open_hfq IS '后复权(周/月)开盘价';
COMMENT ON COLUMN stk_week_month_adj.high_hfq IS '后复权(周/月)最高价';
COMMENT ON COLUMN stk_week_month_adj.low_hfq IS '后复权(周/月)最低价';
COMMENT ON COLUMN stk_week_month_adj.close_hfq IS '后复权(周/月)收盘价';
COMMENT ON COLUMN stk_week_month_adj.vol IS '(周/月)成交量';
COMMENT ON COLUMN stk_week_month_adj.amount IS '(周/月)成交额';
COMMENT ON COLUMN stk_week_month_adj.change IS '(周/月)涨跌额';
COMMENT ON COLUMN stk_week_month_adj.pct_chg IS '(周/月)涨跌幅 【基于除权后的昨收计算的涨跌幅：（今收-除权昨收）/除权昨收】';

-- 添加索引
CREATE INDEX idx_stk_week_month_adj_ts_code ON stk_week_month_adj(ts_code);
CREATE INDEX idx_stk_week_month_adj_trade_date ON stk_week_month_adj(trade_date);
CREATE INDEX idx_stk_week_month_adj_freq ON stk_week_month_adj(freq);
CREATE INDEX idx_stk_week_month_adj_ts_code_trade_date ON stk_week_month_adj(ts_code, trade_date);
CREATE INDEX idx_stk_week_month_adj_ts_code_freq ON stk_week_month_adj(ts_code, freq);

-- 添加外键关联到股票基本信息表
ALTER TABLE stk_week_month_adj 
ADD CONSTRAINT fk_stk_week_month_adj_stock_basic 
FOREIGN KEY (ts_code) 
REFERENCES stock_basic (ts_code);

-- 可选：创建视图，方便单独查询周数据或月数据
CREATE VIEW view_weekly_adj AS
SELECT * FROM stk_week_month_adj WHERE freq = 'week';

CREATE VIEW view_monthly_adj AS
SELECT * FROM stk_week_month_adj WHERE freq = 'month';


-- 名称	类型	默认显示	描述
-- ts_code	str	Y	股票代码
-- trade_date	str	Y	交易日期
-- freq	str	Y	频率(周week,月month)
-- open	float	Y	(周/月)开盘价
-- high	float	Y	(周/月)最高价
-- low	float	Y	(周/月)最低价
-- close	float	Y	(周/月)收盘价
-- pre_close	float	Y	上一(周/月)收盘价【除权价，前复权】
-- open_qfq	float	Y	前复权(周/月)开盘价
-- high_qfq	float	Y	前复权(周/月)最高价
-- low_qfq	float	Y	前复权(周/月)最低价
-- close_qfq	float	Y	前复权(周/月)收盘价
-- open_hfq	float	Y	后复权(周/月)开盘价
-- high_hfq	float	Y	后复权(周/月)最高价
-- low_hfq	float	Y	后复权(周/月)最低价
-- close_hfq	float	Y	后复权(周/月)收盘价
-- vol	float	Y	(周/月)成交量
-- amount	float	Y	(周/月)成交额
-- change	float	Y	(周/月)涨跌额
-- pct_chg	float	Y	(周/月)涨跌幅 【基于除权后的昨收计算的涨跌幅：（今收-除权昨收）/除权昨收 】