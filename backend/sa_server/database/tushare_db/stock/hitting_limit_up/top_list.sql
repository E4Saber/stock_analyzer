-- 龙虎榜每日交易明细表（top_list）
CREATE TABLE top_list (
    -- Primary key and identification fields
    id SERIAL PRIMARY KEY,
    trade_date DATE NOT NULL,
    ts_code VARCHAR(12) NOT NULL,
    name VARCHAR(100) NOT NULL,
    
    -- Price and change fields
    close NUMERIC(20, 4),
    pct_change NUMERIC(10, 4),
    
    -- Volume and turnover fields
    turnover_rate NUMERIC(10, 4),
    amount NUMERIC(20, 4),
    
    -- Top list specific fields
    l_sell NUMERIC(20, 4),
    l_buy NUMERIC(20, 4),
    l_amount NUMERIC(20, 4),
    net_amount NUMERIC(20, 4),
    net_rate NUMERIC(10, 4),
    amount_rate NUMERIC(10, 4),
    
    -- Market value fields
    float_values NUMERIC(20, 4),
    
    -- Reason field
    reason TEXT
);

-- Create indexes for frequently queried fields
CREATE INDEX idx_top_list_trade_date ON top_list(trade_date);
CREATE INDEX idx_top_list_ts_code ON top_list(ts_code);
CREATE INDEX idx_top_list_reason ON top_list(reason);

-- Add unique constraint for upsert operations
ALTER TABLE top_list ADD CONSTRAINT top_list_unique_key 
UNIQUE (trade_date, ts_code);

-- Add table comment
COMMENT ON TABLE top_list IS '龙虎榜每日交易明细';

-- Add column comments
COMMENT ON COLUMN top_list.trade_date IS '交易日期';
COMMENT ON COLUMN top_list.ts_code IS 'TS代码';
COMMENT ON COLUMN top_list.name IS '名称';
COMMENT ON COLUMN top_list.close IS '收盘价';
COMMENT ON COLUMN top_list.pct_change IS '涨跌幅';
COMMENT ON COLUMN top_list.turnover_rate IS '换手率';
COMMENT ON COLUMN top_list.amount IS '总成交额';
COMMENT ON COLUMN top_list.l_sell IS '龙虎榜卖出额';
COMMENT ON COLUMN top_list.l_buy IS '龙虎榜买入额';
COMMENT ON COLUMN top_list.l_amount IS '龙虎榜成交额';
COMMENT ON COLUMN top_list.net_amount IS '龙虎榜净买入额';
COMMENT ON COLUMN top_list.net_rate IS '龙虎榜净买额占比';
COMMENT ON COLUMN top_list.amount_rate IS '龙虎榜成交额占比';
COMMENT ON COLUMN top_list.float_values IS '当日流通市值';
COMMENT ON COLUMN top_list.reason IS '上榜理由';


-- 名称	类型	默认显示	描述
-- trade_date	str	Y	交易日期
-- ts_code	str	Y	TS代码
-- name	str	Y	名称
-- close	float	Y	收盘价
-- pct_change	float	Y	涨跌幅
-- turnover_rate	float	Y	换手率
-- amount	float	Y	总成交额
-- l_sell	float	Y	龙虎榜卖出额
-- l_buy	float	Y	龙虎榜买入额
-- l_amount	float	Y	龙虎榜成交额
-- net_amount	float	Y	龙虎榜净买入额
-- net_rate	float	Y	龙虎榜净买额占比
-- amount_rate	float	Y	龙虎榜成交额占比
-- float_values	float	Y	当日流通市值
-- reason	str	Y	上榜理由