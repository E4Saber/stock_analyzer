-- 股票数据 - 行情数据

-- 实时成交数据(爬虫版)（realtime_tick）
CREATE TABLE realtime_tick (
    id SERIAL PRIMARY KEY,                -- 自增主键
    ts_code VARCHAR(20) NOT NULL,         -- 股票代码
    trade_date DATE NOT NULL,             -- 交易日期
    time TIME NOT NULL,                   -- 交易时间
    price NUMERIC(12,4) NOT NULL,         -- 现价
    change NUMERIC(12,4),                 -- 价格变动
    volume INT NOT NULL,                  -- 成交量（单位：手）
    amount NUMERIC(20,4) NOT NULL,        -- 成交金额（元）
    type VARCHAR(10) NOT NULL,            -- 类型：买入/卖出/中性
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, -- 记录创建时间
    CONSTRAINT ck_realtime_tick_type CHECK (type IN ('买入', '卖出', '中性'))
);

-- 表注释
COMMENT ON TABLE realtime_tick IS '实时逐笔交易';

-- 列注释
COMMENT ON COLUMN realtime_tick.id IS '自增主键';
COMMENT ON COLUMN realtime_tick.ts_code IS '股票代码';
COMMENT ON COLUMN realtime_tick.trade_date IS '交易日期';
COMMENT ON COLUMN realtime_tick.time IS '交易时间';
COMMENT ON COLUMN realtime_tick.price IS '现价';
COMMENT ON COLUMN realtime_tick.change IS '价格变动';
COMMENT ON COLUMN realtime_tick.volume IS '成交量（单位：手）';
COMMENT ON COLUMN realtime_tick.amount IS '成交金额（元）';
COMMENT ON COLUMN realtime_tick.type IS '类型：买入/卖出/中性';
COMMENT ON COLUMN realtime_tick.created_at IS '记录创建时间';

-- 添加索引
CREATE INDEX idx_realtime_tick_ts_code ON realtime_tick(ts_code);
CREATE INDEX idx_realtime_tick_trade_date ON realtime_tick(trade_date);
CREATE INDEX idx_realtime_tick_ts_code_trade_date ON realtime_tick(ts_code, trade_date);
CREATE INDEX idx_realtime_tick_type ON realtime_tick(type);
CREATE INDEX idx_realtime_tick_created_at ON realtime_tick(created_at);

-- 添加外键关联到股票基本信息表
ALTER TABLE realtime_tick 
ADD CONSTRAINT fk_realtime_tick_stock_basic 
FOREIGN KEY (ts_code) 
REFERENCES stock_basic (ts_code);

-- 可选：分区表设置（强烈建议用于tick数据，因为数据量非常大）
/*
CREATE TABLE realtime_tick (
    id SERIAL,
    ts_code VARCHAR(20) NOT NULL,
    trade_date DATE NOT NULL,
    time TIME NOT NULL,
    price NUMERIC(12,4) NOT NULL,
    change NUMERIC(12,4),
    volume INT NOT NULL,
    amount NUMERIC(20,4) NOT NULL,
    type VARCHAR(10) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ck_realtime_tick_type CHECK (type IN ('买入', '卖出', '中性'))
) PARTITION BY RANGE (trade_date);

-- 创建分区（按日）
CREATE TABLE realtime_tick_y2025m03d21 PARTITION OF realtime_tick
    FOR VALUES FROM ('2025-03-21') TO ('2025-03-22');

CREATE TABLE realtime_tick_y2025m03d22 PARTITION OF realtime_tick
    FOR VALUES FROM ('2025-03-22') TO ('2025-03-23');

-- 在分区上创建索引
CREATE INDEX idx_realtime_tick_y2025m03d21_ts_code ON realtime_tick_y2025m03d21(ts_code);
CREATE INDEX idx_realtime_tick_y2025m03d21_time ON realtime_tick_y2025m03d21(time);
CREATE INDEX idx_realtime_tick_y2025m03d22_ts_code ON realtime_tick_y2025m03d22(ts_code);
CREATE INDEX idx_realtime_tick_y2025m03d22_time ON realtime_tick_y2025m03d22(time);
*/


-- 名称	类型	描述
-- time	str	交易时间
-- price	float	现价
-- change	float	价格变动
-- volume	int	成交量（单位：手）
-- amount	int	成交金额（元）
-- type	str	类型：买入/卖出/中性