-- 股票数据 - 行情数据

-- 每日涨跌停价格（stk_limit）
CREATE TABLE stk_limit (
    id SERIAL PRIMARY KEY,                -- 自增主键
    trade_date DATE NOT NULL,             -- 交易日期
    ts_code VARCHAR(20) NOT NULL,         -- TS股票代码
    pre_close NUMERIC(12,4),              -- 昨日收盘价
    up_limit NUMERIC(12,4) NOT NULL,      -- 涨停价
    down_limit NUMERIC(12,4) NOT NULL,    -- 跌停价
    CONSTRAINT uk_stk_limit_ts_code_trade_date UNIQUE (ts_code, trade_date)
);

-- 表注释
COMMENT ON TABLE stk_limit IS '涨跌停限制';

-- 列注释
COMMENT ON COLUMN stk_limit.id IS '自增主键';
COMMENT ON COLUMN stk_limit.trade_date IS '交易日期';
COMMENT ON COLUMN stk_limit.ts_code IS 'TS股票代码';
COMMENT ON COLUMN stk_limit.pre_close IS '昨日收盘价';
COMMENT ON COLUMN stk_limit.up_limit IS '涨停价';
COMMENT ON COLUMN stk_limit.down_limit IS '跌停价';

-- 添加索引
CREATE INDEX idx_stk_limit_ts_code ON stk_limit(ts_code);
CREATE INDEX idx_stk_limit_trade_date ON stk_limit(trade_date);
CREATE INDEX idx_stk_limit_ts_code_trade_date ON stk_limit(ts_code, trade_date);

-- 添加外键关联到股票基本信息表
ALTER TABLE stk_limit 
ADD CONSTRAINT fk_stk_limit_stock_basic 
FOREIGN KEY (ts_code) 
REFERENCES stock_basic (ts_code);


-- 名称	类型	默认显示	描述
-- trade_date	str	Y	交易日期
-- ts_code	str	Y	TS股票代码
-- pre_close	float	N	昨日收盘价
-- up_limit	float	Y	涨停价
-- down_limit	float	Y	跌停价