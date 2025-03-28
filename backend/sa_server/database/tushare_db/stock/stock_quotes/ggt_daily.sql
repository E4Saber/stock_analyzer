-- 股票数据 - 行情数据

-- 港股通每日成交统计（ggt_daily）
CREATE TABLE ggt_daily (
    id SERIAL PRIMARY KEY,                -- 自增主键
    trade_date DATE NOT NULL,             -- 交易日期
    buy_amount NUMERIC(16,4) NOT NULL,    -- 买入成交金额（亿元）
    buy_volume NUMERIC(16,4) NOT NULL,    -- 买入成交笔数（万笔）
    sell_amount NUMERIC(16,4) NOT NULL,   -- 卖出成交金额（亿元）
    sell_volume NUMERIC(16,4) NOT NULL,   -- 卖出成交笔数（万笔）
    CONSTRAINT uk_ggt_daily_trade_date UNIQUE (trade_date)
);

-- 表注释
COMMENT ON TABLE ggt_daily IS '港股通每日成交统计';

-- 列注释
COMMENT ON COLUMN ggt_daily.id IS '自增主键';
COMMENT ON COLUMN ggt_daily.trade_date IS '交易日期';
COMMENT ON COLUMN ggt_daily.buy_amount IS '买入成交金额（亿元）';
COMMENT ON COLUMN ggt_daily.buy_volume IS '买入成交笔数（万笔）';
COMMENT ON COLUMN ggt_daily.sell_amount IS '卖出成交金额（亿元）';
COMMENT ON COLUMN ggt_daily.sell_volume IS '卖出成交笔数（万笔）';

-- 添加索引
CREATE INDEX idx_ggt_daily_trade_date ON ggt_daily(trade_date);

-- 可以添加派生列（计算净买入金额和净买入笔数）
ALTER TABLE ggt_daily ADD COLUMN net_amount NUMERIC(16,4) 
GENERATED ALWAYS AS (buy_amount - sell_amount) STORED;

ALTER TABLE ggt_daily ADD COLUMN net_volume NUMERIC(16,4) 
GENERATED ALWAYS AS (buy_volume - sell_volume) STORED;

COMMENT ON COLUMN ggt_daily.net_amount IS '净买入成交金额（亿元）';
COMMENT ON COLUMN ggt_daily.net_volume IS '净买入成交笔数（万笔）';


-- 名称	类型	默认显示	描述
-- trade_date	str	Y	交易日期
-- buy_amount	float	Y	买入成交金额（亿元）
-- buy_volume	float	Y	买入成交笔数（万笔）
-- sell_amount	float	Y	卖出成交金额（亿元）
-- sell_volume	float	Y	卖出成交笔数（万笔）