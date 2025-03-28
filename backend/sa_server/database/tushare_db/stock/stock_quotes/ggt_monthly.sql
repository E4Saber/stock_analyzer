-- 股票数据 - 行情数据

-- 港股通每月成交统计（ggt_monthly）
CREATE TABLE ggt_monthly (
    id SERIAL PRIMARY KEY,                   -- 自增主键
    month VARCHAR(7) NOT NULL,               -- 交易月份（格式：YYYY-MM）
    day_buy_amt NUMERIC(16,4) NOT NULL,      -- 当月日均买入成交金额（亿元）
    day_buy_vol NUMERIC(16,4) NOT NULL,      -- 当月日均买入成交笔数（万笔）
    day_sell_amt NUMERIC(16,4) NOT NULL,     -- 当月日均卖出成交金额（亿元）
    day_sell_vol NUMERIC(16,4) NOT NULL,     -- 当月日均卖出成交笔数（万笔）
    total_buy_amt NUMERIC(16,4) NOT NULL,    -- 总买入成交金额（亿元）
    total_buy_vol NUMERIC(16,4) NOT NULL,    -- 总买入成交笔数（万笔）
    total_sell_amt NUMERIC(16,4) NOT NULL,   -- 总卖出成交金额（亿元）
    total_sell_vol NUMERIC(16,4) NOT NULL,   -- 总卖出成交笔数（万笔）
    CONSTRAINT uk_ggt_monthly_month UNIQUE (month)
);

-- 表注释
COMMENT ON TABLE ggt_monthly IS '港股通月度成交统计';

-- 列注释
COMMENT ON COLUMN ggt_monthly.id IS '自增主键';
COMMENT ON COLUMN ggt_monthly.month IS '交易月份（格式：YYYY-MM）';
COMMENT ON COLUMN ggt_monthly.day_buy_amt IS '当月日均买入成交金额（亿元）';
COMMENT ON COLUMN ggt_monthly.day_buy_vol IS '当月日均买入成交笔数（万笔）';
COMMENT ON COLUMN ggt_monthly.day_sell_amt IS '当月日均卖出成交金额（亿元）';
COMMENT ON COLUMN ggt_monthly.day_sell_vol IS '当月日均卖出成交笔数（万笔）';
COMMENT ON COLUMN ggt_monthly.total_buy_amt IS '总买入成交金额（亿元）';
COMMENT ON COLUMN ggt_monthly.total_buy_vol IS '总买入成交笔数（万笔）';
COMMENT ON COLUMN ggt_monthly.total_sell_amt IS '总卖出成交金额（亿元）';
COMMENT ON COLUMN ggt_monthly.total_sell_vol IS '总卖出成交笔数（万笔）';

-- 添加索引
CREATE INDEX idx_ggt_monthly_month ON ggt_monthly(month);

-- 添加派生列（计算净买入金额和净买入笔数）
ALTER TABLE ggt_monthly ADD COLUMN day_net_amt NUMERIC(16,4) 
GENERATED ALWAYS AS (day_buy_amt - day_sell_amt) STORED;

ALTER TABLE ggt_monthly ADD COLUMN day_net_vol NUMERIC(16,4) 
GENERATED ALWAYS AS (day_buy_vol - day_sell_vol) STORED;

ALTER TABLE ggt_monthly ADD COLUMN total_net_amt NUMERIC(16,4) 
GENERATED ALWAYS AS (total_buy_amt - total_sell_amt) STORED;

ALTER TABLE ggt_monthly ADD COLUMN total_net_vol NUMERIC(16,4) 
GENERATED ALWAYS AS (total_buy_vol - total_sell_vol) STORED;

COMMENT ON COLUMN ggt_monthly.day_net_amt IS '当月日均净买入成交金额（亿元）';
COMMENT ON COLUMN ggt_monthly.day_net_vol IS '当月日均净买入成交笔数（万笔）';
COMMENT ON COLUMN ggt_monthly.total_net_amt IS '总净买入成交金额（亿元）';
COMMENT ON COLUMN ggt_monthly.total_net_vol IS '总净买入成交笔数（万笔）';


-- 名称	类型	默认显示	描述
-- month	str	Y	交易日期
-- day_buy_amt	float	Y	当月日均买入成交金额（亿元）
-- day_buy_vol	float	Y	当月日均买入成交笔数（万笔）
-- day_sell_amt	float	Y	当月日均卖出成交金额（亿元）
-- day_sell_vol	float	Y	当月日均卖出成交笔数（万笔）
-- total_buy_amt	float	Y	总买入成交金额（亿元）
-- total_buy_vol	float	Y	总买入成交笔数（万笔）
-- total_sell_amt	float	Y	总卖出成交金额（亿元）
-- total_sell_vol	float	Y	总卖出成交笔数（万笔）