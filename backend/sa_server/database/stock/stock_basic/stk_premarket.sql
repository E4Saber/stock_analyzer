-- 股票数据 - 基础数据

-- 每日股本情况（盘前）（stk_permarket）
CREATE TABLE stk_premarket (
    trade_date DATE NOT NULL,
    ts_code VARCHAR(20) NOT NULL,
    total_share NUMERIC(20,2),           -- 总股本（万股）
    float_share NUMERIC(20,2),           -- 流通股本（万股）
    pre_close NUMERIC(10,2),             -- 昨日收盘价
    up_limit NUMERIC(10,2),              -- 今日涨停价
    down_limit NUMERIC(10,2),            -- 今日跌停价
    
    PRIMARY KEY (trade_date, ts_code)    -- 复合主键
);

-- 表注释
COMMENT ON TABLE stk_premarket IS '股票盘前信息';

-- 列注释
COMMENT ON COLUMN stk_premarket.trade_date IS '交易日期';
COMMENT ON COLUMN stk_premarket.ts_code IS 'TS股票代码';
COMMENT ON COLUMN stk_premarket.total_share IS '总股本（万股）';
COMMENT ON COLUMN stk_premarket.float_share IS '流通股本（万股）';
COMMENT ON COLUMN stk_premarket.pre_close IS '昨日收盘价';
COMMENT ON COLUMN stk_premarket.up_limit IS '今日涨停价';
COMMENT ON COLUMN stk_premarket.down_limit IS '今日跌停价';

-- 添加索引
CREATE INDEX idx_stk_premarket_ts_code ON stk_premarket(ts_code);
CREATE INDEX idx_stk_premarket_trade_date ON stk_premarket(trade_date);

-- 添加外键约束 (如果与stock_basic表关联)
ALTER TABLE stk_premarket
ADD CONSTRAINT fk_stk_premarket_stock_basic
FOREIGN KEY (ts_code) REFERENCES stock_basic(ts_code);



-- 名称	类型	默认显示	描述
-- trade_date	str	Y	交易日期
-- ts_code	str	Y	TS股票代码
-- total_share	float	Y	总股本（万股）
-- float_share	float	Y	流通股本（万股）
-- pre_close	float	Y	昨日收盘价
-- up_limit	float	Y	今日涨停价
-- down_limit	float	Y	今日跌停价