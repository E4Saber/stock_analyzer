-- 股票数据 - 行情数据

-- 港股通十大成交股（ggt_top10）
CREATE TABLE ggt_top10 (
    id SERIAL PRIMARY KEY,                -- 自增主键
    trade_date DATE NOT NULL,             -- 交易日期
    ts_code VARCHAR(20) NOT NULL,         -- 股票代码
    name VARCHAR(100) NOT NULL,           -- 股票名称
    close NUMERIC(12,4),                  -- 收盘价
    p_change NUMERIC(10,4),               -- 涨跌幅
    rank SMALLINT NOT NULL,               -- 资金排名
    market_type CHAR(1) NOT NULL,         -- 市场类型 2：港股通（沪） 4：港股通（深）
    amount NUMERIC(20,4),                 -- 累计成交金额（元）
    net_amount NUMERIC(20,4),             -- 净买入金额（元）
    sh_amount NUMERIC(20,4),              -- 沪市成交金额（元）
    sh_net_amount NUMERIC(20,4),          -- 沪市净买入金额（元）
    sh_buy NUMERIC(20,4),                 -- 沪市买入金额（元）
    sh_sell NUMERIC(20,4),                -- 沪市卖出金额
    sz_amount NUMERIC(20,4),              -- 深市成交金额（元）
    sz_net_amount NUMERIC(20,4),          -- 深市净买入金额（元）
    sz_buy NUMERIC(20,4),                 -- 深市买入金额（元）
    sz_sell NUMERIC(20,4),                -- 深市卖出金额（元）
    CONSTRAINT uk_ggt_top10_trade_date_market_type_rank UNIQUE (trade_date, market_type, rank),
    CONSTRAINT ck_ggt_top10_market_type CHECK (market_type IN ('2', '4')),
    CONSTRAINT ck_ggt_top10_rank CHECK (rank BETWEEN 1 AND 10)
);

-- 表注释
COMMENT ON TABLE ggt_top10 IS '港股通十大成交股';

-- 列注释
COMMENT ON COLUMN ggt_top10.id IS '自增主键';
COMMENT ON COLUMN ggt_top10.trade_date IS '交易日期';
COMMENT ON COLUMN ggt_top10.ts_code IS '股票代码';
COMMENT ON COLUMN ggt_top10.name IS '股票名称';
COMMENT ON COLUMN ggt_top10.close IS '收盘价';
COMMENT ON COLUMN ggt_top10.p_change IS '涨跌幅';
COMMENT ON COLUMN ggt_top10.rank IS '资金排名';
COMMENT ON COLUMN ggt_top10.market_type IS '市场类型 2：港股通（沪） 4：港股通（深）';
COMMENT ON COLUMN ggt_top10.amount IS '累计成交金额（元）';
COMMENT ON COLUMN ggt_top10.net_amount IS '净买入金额（元）';
COMMENT ON COLUMN ggt_top10.sh_amount IS '沪市成交金额（元）';
COMMENT ON COLUMN ggt_top10.sh_net_amount IS '沪市净买入金额（元）';
COMMENT ON COLUMN ggt_top10.sh_buy IS '沪市买入金额（元）';
COMMENT ON COLUMN ggt_top10.sh_sell IS '沪市卖出金额';
COMMENT ON COLUMN ggt_top10.sz_amount IS '深市成交金额（元）';
COMMENT ON COLUMN ggt_top10.sz_net_amount IS '深市净买入金额（元）';
COMMENT ON COLUMN ggt_top10.sz_buy IS '深市买入金额（元）';
COMMENT ON COLUMN ggt_top10.sz_sell IS '深市卖出金额（元）';

-- 添加索引
CREATE INDEX idx_ggt_top10_ts_code ON ggt_top10(ts_code);
CREATE INDEX idx_ggt_top10_trade_date ON ggt_top10(trade_date);
CREATE INDEX idx_ggt_top10_market_type ON ggt_top10(market_type);
CREATE INDEX idx_ggt_top10_rank ON ggt_top10(rank);
CREATE INDEX idx_ggt_top10_trade_date_market_type ON ggt_top10(trade_date, market_type);

-- 注意：由于这是港股数据，可能不需要外键约束到 stock_basic 表
-- 如果有港股基础信息表，可以添加相应的外键约束


-- 名称	类型	描述
-- trade_date	str	交易日期
-- ts_code	str	股票代码
-- name	str	股票名称
-- close	float	收盘价
-- p_change	float	涨跌幅
-- rank	str	资金排名
-- market_type	str	市场类型 2：港股通（沪） 4：港股通（深）
-- amount	float	累计成交金额（元）
-- net_amount	float	净买入金额（元）
-- sh_amount	float	沪市成交金额（元）
-- sh_net_amount	float	沪市净买入金额（元）
-- sh_buy	float	沪市买入金额（元）
-- sh_sell	float	沪市卖出金额
-- sz_amount	float	深市成交金额（元）
-- sz_net_amount	float	深市净买入金额（元）
-- sz_buy	float	深市买入金额（元）
-- sz_sell	float	深市卖出金额（元）