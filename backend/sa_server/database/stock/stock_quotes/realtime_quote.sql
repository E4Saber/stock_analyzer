-- 股票数据 - 行情数据

-- 实时盘口TICK快照(爬虫版)（realtime_quote）
CREATE TABLE realtime_quote (
    id SERIAL PRIMARY KEY,                -- 自增主键
    name VARCHAR(50) NOT NULL,            -- 股票名称
    ts_code VARCHAR(20) NOT NULL,         -- 股票代码
    date DATE NOT NULL,                   -- 交易日期
    time TIME NOT NULL,                   -- 交易时间
    open NUMERIC(12,4),                   -- 开盘价
    pre_close NUMERIC(12,4),              -- 昨收价
    price NUMERIC(12,4),                  -- 现价
    high NUMERIC(12,4),                   -- 今日最高价
    low NUMERIC(12,4),                    -- 今日最低价
    bid NUMERIC(12,4),                    -- 竞买价，即"买一"报价（元）
    ask NUMERIC(12,4),                    -- 竞卖价，即"卖一"报价（元）
    volume BIGINT,                        -- 成交量（src=sina时是股，src=dc时是手）
    amount NUMERIC(20,4),                 -- 成交金额（元 CNY）
    b1_v NUMERIC(16,2),                   -- 委买一（量，单位：手，下同）
    b1_p NUMERIC(12,4),                   -- 委买一（价，单位：元，下同）
    b2_v NUMERIC(16,2),                   -- 委买二（量）
    b2_p NUMERIC(12,4),                   -- 委买二（价）
    b3_v NUMERIC(16,2),                   -- 委买三（量）
    b3_p NUMERIC(12,4),                   -- 委买三（价）
    b4_v NUMERIC(16,2),                   -- 委买四（量）
    b4_p NUMERIC(12,4),                   -- 委买四（价）
    b5_v NUMERIC(16,2),                   -- 委买五（量）
    b5_p NUMERIC(12,4),                   -- 委买五（价）
    a1_v NUMERIC(16,2),                   -- 委卖一（量，单位：手，下同）
    a1_p NUMERIC(12,4),                   -- 委卖一（价，单位：元，下同）
    a2_v NUMERIC(16,2),                   -- 委卖二（量）
    a2_p NUMERIC(12,4),                   -- 委卖二（价）
    a3_v NUMERIC(16,2),                   -- 委卖三（量）
    a3_p NUMERIC(12,4),                   -- 委卖三（价）
    a4_v NUMERIC(16,2),                   -- 委卖四（量）
    a4_p NUMERIC(12,4),                   -- 委卖四（价）
    a5_v NUMERIC(16,2),                   -- 委卖五（量）
    a5_p NUMERIC(12,4),                   -- 委卖五（价）
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, -- 记录创建时间
    CONSTRAINT uk_realtime_quote_ts_code_date_time UNIQUE (ts_code, date, time)
);

-- 表注释
COMMENT ON TABLE realtime_quote IS '实时行情';

-- 列注释
COMMENT ON COLUMN realtime_quote.id IS '自增主键';
COMMENT ON COLUMN realtime_quote.name IS '股票名称';
COMMENT ON COLUMN realtime_quote.ts_code IS '股票代码';
COMMENT ON COLUMN realtime_quote.date IS '交易日期';
COMMENT ON COLUMN realtime_quote.time IS '交易时间';
COMMENT ON COLUMN realtime_quote.open IS '开盘价';
COMMENT ON COLUMN realtime_quote.pre_close IS '昨收价';
COMMENT ON COLUMN realtime_quote.price IS '现价';
COMMENT ON COLUMN realtime_quote.high IS '今日最高价';
COMMENT ON COLUMN realtime_quote.low IS '今日最低价';
COMMENT ON COLUMN realtime_quote.bid IS '竞买价，即"买一"报价（元）';
COMMENT ON COLUMN realtime_quote.ask IS '竞卖价，即"卖一"报价（元）';
COMMENT ON COLUMN realtime_quote.volume IS '成交量（src=sina时是股，src=dc时是手）';
COMMENT ON COLUMN realtime_quote.amount IS '成交金额（元 CNY）';
COMMENT ON COLUMN realtime_quote.b1_v IS '委买一（量，单位：手，下同）';
COMMENT ON COLUMN realtime_quote.b1_p IS '委买一（价，单位：元，下同）';
COMMENT ON COLUMN realtime_quote.b2_v IS '委买二（量）';
COMMENT ON COLUMN realtime_quote.b2_p IS '委买二（价）';
COMMENT ON COLUMN realtime_quote.b3_v IS '委买三（量）';
COMMENT ON COLUMN realtime_quote.b3_p IS '委买三（价）';
COMMENT ON COLUMN realtime_quote.b4_v IS '委买四（量）';
COMMENT ON COLUMN realtime_quote.b4_p IS '委买四（价）';
COMMENT ON COLUMN realtime_quote.b5_v IS '委买五（量）';
COMMENT ON COLUMN realtime_quote.b5_p IS '委买五（价）';
COMMENT ON COLUMN realtime_quote.a1_v IS '委卖一（量，单位：手，下同）';
COMMENT ON COLUMN realtime_quote.a1_p IS '委卖一（价，单位：元，下同）';
COMMENT ON COLUMN realtime_quote.a2_v IS '委卖二（量）';
COMMENT ON COLUMN realtime_quote.a2_p IS '委卖二（价）';
COMMENT ON COLUMN realtime_quote.a3_v IS '委卖三（量）';
COMMENT ON COLUMN realtime_quote.a3_p IS '委卖三（价）';
COMMENT ON COLUMN realtime_quote.a4_v IS '委卖四（量）';
COMMENT ON COLUMN realtime_quote.a4_p IS '委卖四（价）';
COMMENT ON COLUMN realtime_quote.a5_v IS '委卖五（量）';
COMMENT ON COLUMN realtime_quote.a5_p IS '委卖五（价）';
COMMENT ON COLUMN realtime_quote.created_at IS '记录创建时间';

-- 添加索引
CREATE INDEX idx_realtime_quote_ts_code ON realtime_quote(ts_code);
CREATE INDEX idx_realtime_quote_date ON realtime_quote(date);
CREATE INDEX idx_realtime_quote_ts_code_date ON realtime_quote(ts_code, date);
CREATE INDEX idx_realtime_quote_created_at ON realtime_quote(created_at);

-- 添加外键关联到股票基本信息表
ALTER TABLE realtime_quote 
ADD CONSTRAINT fk_realtime_quote_stock_basic 
FOREIGN KEY (ts_code) 
REFERENCES stock_basic (ts_code);

-- 可选：分区表设置（如果数据量大）
-- 可以按日期进行分区，这里是示例
/*
CREATE TABLE realtime_quote (
    id SERIAL,
    name VARCHAR(50) NOT NULL,
    ts_code VARCHAR(20) NOT NULL,
    date DATE NOT NULL,
    time TIME NOT NULL,
    -- 其他字段...
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uk_realtime_quote_ts_code_date_time UNIQUE (ts_code, date, time)
) PARTITION BY RANGE (date);

-- 创建分区（按月）
CREATE TABLE realtime_quote_y2025m03 PARTITION OF realtime_quote
    FOR VALUES FROM ('2025-03-01') TO ('2025-04-01');

CREATE TABLE realtime_quote_y2025m04 PARTITION OF realtime_quote
    FOR VALUES FROM ('2025-04-01') TO ('2025-05-01');

-- 在分区上创建索引
CREATE INDEX idx_realtime_quote_y2025m03_ts_code ON realtime_quote_y2025m03(ts_code);
CREATE INDEX idx_realtime_quote_y2025m04_ts_code ON realtime_quote_y2025m04(ts_code);
*/


-- 名称	类型	描述
-- name	str	股票名称
-- ts_code	str	股票代码
-- date	str	交易日期
-- time	str	交易时间
-- open	float	开盘价
-- pre_close	float	昨收价
-- price	float	现价
-- high	float	今日最高价
-- low	float	今日最低价
-- bid	float	竞买价，即“买一”报价（元）
-- ask	float	竞卖价，即“卖一”报价（元）
-- volume	int	成交量（src=sina时是股，src=dc时是手）
-- amount	float	成交金额（元 CNY）
-- b1_v	float	委买一（量，单位：手，下同）
-- b1_p	float	委买一（价，单位：元，下同）
-- b2_v	float	委买二（量）
-- b2_p	float	委买二（价）
-- b3_v	float	委买三（量）
-- b3_p	float	委买三（价）
-- b4_v	float	委买四（量）
-- b4_p	float	委买四（价）
-- b5_v	float	委买五（量）
-- b5_p	float	委买五（价）
-- a1_v	float	委卖一（量，单位：手，下同）
-- a1_p	float	委卖一（价，单位：元，下同）
-- a2_v	float	委卖二（量）
-- a2_p	float	委卖二（价）
-- a3_v	float	委卖三（量）
-- a3_p	float	委卖三（价）
-- a4_v	float	委卖四（量）
-- a4_p	float	委卖四（价）
-- a5_v	float	委卖五（量）
-- a5_p	float	委卖五（价）