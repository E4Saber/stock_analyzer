-- 股票数据 - 行情数据

-- 实时涨跌幅排名(爬虫版)（realtime_list）
CREATE TABLE realtime_list (
    id SERIAL PRIMARY KEY,                -- 自增主键
    ts_code VARCHAR(20) NOT NULL,         -- 股票代码
    name VARCHAR(50) NOT NULL,            -- 股票名称
    price NUMERIC(12,4),                  -- 当前价格
    pct_change NUMERIC(10,4),             -- 涨跌幅
    change NUMERIC(12,4),                 -- 涨跌额
    volume BIGINT,                        -- 成交量（东财：手，新浪：股）
    amount NUMERIC(20,4),                 -- 成交金额（元）
    swing NUMERIC(10,4),                  -- 振幅（东财数据）
    low NUMERIC(12,4),                    -- 今日最低价
    high NUMERIC(12,4),                   -- 今日最高价
    open NUMERIC(12,4),                   -- 今日开盘价
    close NUMERIC(12,4),                  -- 今日收盘价
    buy NUMERIC(12,4),                    -- 买入价（新浪数据）
    sale NUMERIC(12,4),                   -- 卖出价（新浪数据）
    vol_ratio NUMERIC(10,4),              -- 量比（东财数据）
    turnover_rate NUMERIC(10,4),          -- 换手率（东财数据）
    pe NUMERIC(16,4),                     -- 市盈率PE（东财数据）
    pb NUMERIC(10,4),                     -- 市净率PB（东财数据）
    total_mv NUMERIC(20,4),               -- 总市值（元）（东财数据）
    float_mv NUMERIC(20,4),               -- 流通市值（元）（东财数据）
    rise NUMERIC(10,4),                   -- 涨速（东财数据）
    min5 NUMERIC(10,4),                   -- 5分钟涨幅（东财数据）
    day60 NUMERIC(10,4),                  -- 60天涨幅（东财数据）
    year1 NUMERIC(10,4),                  -- 1年涨幅（东财数据）
    time TIMESTAMP,                       -- 当前时间（新浪数据）
    trade_date DATE NOT NULL,             -- 交易日期
    data_source VARCHAR(10) NOT NULL,     -- 数据源（eastmoney/sina）
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, -- 记录创建时间
    CONSTRAINT ck_realtime_list_data_source CHECK (data_source IN ('eastmoney', 'sina'))
);

-- 表注释
COMMENT ON TABLE realtime_list IS '实时行情列表（支持东财/新浪数据源）';

-- 列注释
COMMENT ON COLUMN realtime_list.id IS '自增主键';
COMMENT ON COLUMN realtime_list.ts_code IS '股票代码';
COMMENT ON COLUMN realtime_list.name IS '股票名称';
COMMENT ON COLUMN realtime_list.price IS '当前价格';
COMMENT ON COLUMN realtime_list.pct_change IS '涨跌幅';
COMMENT ON COLUMN realtime_list.change IS '涨跌额';
COMMENT ON COLUMN realtime_list.volume IS '成交量（东财：手，新浪：股）';
COMMENT ON COLUMN realtime_list.amount IS '成交金额（元）';
COMMENT ON COLUMN realtime_list.swing IS '振幅（东财数据）';
COMMENT ON COLUMN realtime_list.low IS '今日最低价';
COMMENT ON COLUMN realtime_list.high IS '今日最高价';
COMMENT ON COLUMN realtime_list.open IS '今日开盘价';
COMMENT ON COLUMN realtime_list.close IS '今日收盘价';
COMMENT ON COLUMN realtime_list.buy IS '买入价（新浪数据）';
COMMENT ON COLUMN realtime_list.sale IS '卖出价（新浪数据）';
COMMENT ON COLUMN realtime_list.vol_ratio IS '量比（东财数据）';
COMMENT ON COLUMN realtime_list.turnover_rate IS '换手率（东财数据）';
COMMENT ON COLUMN realtime_list.pe IS '市盈率PE（东财数据）';
COMMENT ON COLUMN realtime_list.pb IS '市净率PB（东财数据）';
COMMENT ON COLUMN realtime_list.total_mv IS '总市值（元）（东财数据）';
COMMENT ON COLUMN realtime_list.float_mv IS '流通市值（元）（东财数据）';
COMMENT ON COLUMN realtime_list.rise IS '涨速（东财数据）';
COMMENT ON COLUMN realtime_list.min5 IS '5分钟涨幅（东财数据）';
COMMENT ON COLUMN realtime_list.day60 IS '60天涨幅（东财数据）';
COMMENT ON COLUMN realtime_list.year1 IS '1年涨幅（东财数据）';
COMMENT ON COLUMN realtime_list.time IS '当前时间（新浪数据）';
COMMENT ON COLUMN realtime_list.trade_date IS '交易日期';
COMMENT ON COLUMN realtime_list.data_source IS '数据源（eastmoney/sina）';
COMMENT ON COLUMN realtime_list.created_at IS '记录创建时间';

-- 添加索引
CREATE INDEX idx_realtime_list_ts_code ON realtime_list(ts_code);
CREATE INDEX idx_realtime_list_trade_date ON realtime_list(trade_date);
CREATE INDEX idx_realtime_list_data_source ON realtime_list(data_source);
CREATE INDEX idx_realtime_list_ts_code_trade_date ON realtime_list(ts_code, trade_date);
CREATE INDEX idx_realtime_list_created_at ON realtime_list(created_at);

-- 添加外键关联到股票基本信息表
ALTER TABLE realtime_list 
ADD CONSTRAINT fk_realtime_list_stock_basic 
FOREIGN KEY (ts_code) 
REFERENCES stock_basic (ts_code);

-- 可选：分区表设置
/*
CREATE TABLE realtime_list (
    id SERIAL,
    -- 其他字段...
    trade_date DATE NOT NULL,
    data_source VARCHAR(10) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ck_realtime_list_data_source CHECK (data_source IN ('eastmoney', 'sina'))
) PARTITION BY RANGE (trade_date);

-- 创建分区（按月）
CREATE TABLE realtime_list_y2025m03 PARTITION OF realtime_list
    FOR VALUES FROM ('2025-03-01') TO ('2025-04-01');

CREATE TABLE realtime_list_y2025m04 PARTITION OF realtime_list
    FOR VALUES FROM ('2025-04-01') TO ('2025-05-01');

-- 在分区上创建索引
CREATE INDEX idx_realtime_list_y2025m03_ts_code ON realtime_list_y2025m03(ts_code);
CREATE INDEX idx_realtime_list_y2025m03_data_source ON realtime_list_y2025m03(data_source);
*/

-- 可选：创建视图，单独查看东财数据或新浪数据
CREATE VIEW view_realtime_eastmoney AS
SELECT * FROM realtime_list WHERE data_source = 'eastmoney';

CREATE VIEW view_realtime_sina AS
SELECT * FROM realtime_list WHERE data_source = 'sina';


-- 东财数据输出参数

-- 名称	类型	描述
-- ts_code	str	股票代码
-- name	str	股票名称
-- price	float	当前价格
-- pct_change	float	涨跌幅
-- change	float	涨跌额
-- volume	int	成交量（单位：手）
-- amount	int	成交金额（元）
-- swing	float	振幅
-- low	float	今日最低价
-- high	float	今日最高价
-- open	float	今日开盘价
-- close	float	今日收盘价
-- vol_ratio	int	量比
-- turnover_rate	float	换手率
-- pe	int	市盈率PE
-- pb	float	市净率PB
-- total_mv	float	总市值（元）
-- float_mv	float	流通市值（元）
-- rise	float	涨速
-- 5min	float	5分钟涨幅
-- 60day	float	60天涨幅
-- 1tyear	float	1年涨幅


-- 新浪数据输出参数

-- 名称	类型	描述
-- ts_code	str	股票代码
-- name	str	股票名称
-- price	float	当前价格
-- pct_change	float	涨跌幅
-- change	float	涨跌额
-- buy	float	买入价
-- sale	float	卖出价
-- close	float	今日收盘价
-- open	float	今日开盘价
-- high	float	今日最高价
-- low	float	今日最低价
-- volume	int	成交量（单位：股）
-- amount	int	成交金额（元）
-- time	str	当前时间