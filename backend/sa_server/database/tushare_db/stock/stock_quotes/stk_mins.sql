-- 股票数据 - 行情数据

-- 分钟线行情（stk_mins）
CREATE TABLE stk_mins (
    id SERIAL PRIMARY KEY,                -- 自增主键
    ts_code VARCHAR(20) NOT NULL,         -- 股票代码
    trade_time TIMESTAMP NOT NULL,        -- 交易时间
    open NUMERIC(12,4),                   -- 开盘价
    close NUMERIC(12,4),                  -- 收盘价
    high NUMERIC(12,4),                   -- 最高价
    low NUMERIC(12,4),                    -- 最低价
    vol BIGINT,                           -- 成交量
    amount NUMERIC(20,4),                 -- 成交金额
    CONSTRAINT uk_stk_mins_ts_code_trade_time UNIQUE (ts_code, trade_time)
);

-- 表注释
COMMENT ON TABLE stk_mins IS '股票分钟行情';

-- 列注释
COMMENT ON COLUMN stk_mins.id IS '自增主键';
COMMENT ON COLUMN stk_mins.ts_code IS '股票代码';
COMMENT ON COLUMN stk_mins.trade_time IS '交易时间';
COMMENT ON COLUMN stk_mins.open IS '开盘价';
COMMENT ON COLUMN stk_mins.close IS '收盘价';
COMMENT ON COLUMN stk_mins.high IS '最高价';
COMMENT ON COLUMN stk_mins.low IS '最低价';
COMMENT ON COLUMN stk_mins.vol IS '成交量';
COMMENT ON COLUMN stk_mins.amount IS '成交金额';

-- 添加索引
CREATE INDEX idx_stk_mins_ts_code ON stk_mins(ts_code);
CREATE INDEX idx_stk_mins_trade_time ON stk_mins(trade_time);
CREATE INDEX idx_stk_mins_ts_code_trade_time ON stk_mins(ts_code, trade_time);

-- 添加外键关联到股票基本信息表
ALTER TABLE stk_mins 
ADD CONSTRAINT fk_stk_mins_stock_basic 
FOREIGN KEY (ts_code) 
REFERENCES stock_basic (ts_code);

-- 可选：创建分区表（如果数据量很大）
-- 以下是基于时间范围的分区示例，实际使用时可根据需求调整
/*
CREATE TABLE stk_mins (
    id SERIAL,
    ts_code VARCHAR(20) NOT NULL,
    trade_time TIMESTAMP NOT NULL,
    open NUMERIC(12,4),
    close NUMERIC(12,4),
    high NUMERIC(12,4),
    low NUMERIC(12,4),
    vol BIGINT,
    amount NUMERIC(20,4),
    CONSTRAINT uk_stk_mins_ts_code_trade_time UNIQUE (ts_code, trade_time)
) PARTITION BY RANGE (trade_time);

-- 创建分区
CREATE TABLE stk_mins_y2023 PARTITION OF stk_mins
    FOR VALUES FROM ('2023-01-01') TO ('2024-01-01');

CREATE TABLE stk_mins_y2024 PARTITION OF stk_mins
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');

-- 在每个分区上创建索引
CREATE INDEX idx_stk_mins_y2023_ts_code_trade_time ON stk_mins_y2023(ts_code, trade_time);
CREATE INDEX idx_stk_mins_y2024_ts_code_trade_time ON stk_mins_y2024(ts_code, trade_time);
*/


-- 名称	类型	默认显示	描述
-- ts_code	str	Y	股票代码
-- trade_time	str	Y	交易时间
-- open	float	Y	开盘价
-- close	float	Y	收盘价
-- high	float	Y	最高价
-- low	float	Y	最低价
-- vol	int	Y	成交量
-- amount	float	Y	成交金额