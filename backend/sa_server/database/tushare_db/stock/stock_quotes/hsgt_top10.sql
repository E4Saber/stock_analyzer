-- 股票数据 - 行情数据

-- 沪深股通十大成交股（hsgt_top10）
CREATE TABLE hsgt_top10 (
    id SERIAL PRIMARY KEY,                -- 自增主键
    trade_date DATE NOT NULL,             -- 交易日期
    ts_code VARCHAR(20) NOT NULL,         -- 股票代码
    name VARCHAR(50) NOT NULL,            -- 股票名称
    close NUMERIC(12,4),                  -- 收盘价
    change NUMERIC(12,4),                 -- 涨跌额
    rank SMALLINT NOT NULL,               -- 资金排名
    market_type CHAR(1) NOT NULL,         -- 市场类型（1：沪市 3：深市）
    amount NUMERIC(20,4),                 -- 成交金额（元）
    net_amount NUMERIC(20,4),             -- 净成交金额（元）
    buy NUMERIC(20,4),                    -- 买入金额（元）
    sell NUMERIC(20,4),                   -- 卖出金额（元）
    CONSTRAINT uk_hsgt_top10_trade_date_market_type_rank UNIQUE (trade_date, market_type, rank),
    CONSTRAINT ck_hsgt_top10_market_type CHECK (market_type IN ('1', '3')),
    CONSTRAINT ck_hsgt_top10_rank CHECK (rank BETWEEN 1 AND 10)
);

-- 表注释
COMMENT ON TABLE hsgt_top10 IS '沪深港通十大成交股';

-- 列注释
COMMENT ON COLUMN hsgt_top10.id IS '自增主键';
COMMENT ON COLUMN hsgt_top10.trade_date IS '交易日期';
COMMENT ON COLUMN hsgt_top10.ts_code IS '股票代码';
COMMENT ON COLUMN hsgt_top10.name IS '股票名称';
COMMENT ON COLUMN hsgt_top10.close IS '收盘价';
COMMENT ON COLUMN hsgt_top10.change IS '涨跌额';
COMMENT ON COLUMN hsgt_top10.rank IS '资金排名';
COMMENT ON COLUMN hsgt_top10.market_type IS '市场类型（1：沪市 3：深市）';
COMMENT ON COLUMN hsgt_top10.amount IS '成交金额（元）';
COMMENT ON COLUMN hsgt_top10.net_amount IS '净成交金额（元）';
COMMENT ON COLUMN hsgt_top10.buy IS '买入金额（元）';
COMMENT ON COLUMN hsgt_top10.sell IS '卖出金额（元）';

-- 添加索引
CREATE INDEX idx_hsgt_top10_ts_code ON hsgt_top10(ts_code);
CREATE INDEX idx_hsgt_top10_trade_date ON hsgt_top10(trade_date);
CREATE INDEX idx_hsgt_top10_market_type ON hsgt_top10(market_type);
CREATE INDEX idx_hsgt_top10_rank ON hsgt_top10(rank);
CREATE INDEX idx_hsgt_top10_trade_date_market_type ON hsgt_top10(trade_date, market_type);

-- 添加外键关联到股票基本信息表
ALTER TABLE hsgt_top10 
ADD CONSTRAINT fk_hsgt_top10_stock_basic 
FOREIGN KEY (ts_code) 
REFERENCES stock_basic (ts_code);


-- 名称	类型	描述
-- trade_date	str	交易日期
-- ts_code	str	股票代码
-- name	str	股票名称
-- close	float	收盘价
-- change	float	涨跌额
-- rank	int	资金排名
-- market_type	str	市场类型（1：沪市 3：深市）
-- amount	float	成交金额（元）
-- net_amount	float	净成交金额（元）
-- buy	float	买入金额（元）
-- sell	float	卖出金额（元）