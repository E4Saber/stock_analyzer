-- 股票数据 - 行情数据

-- 复权因子（adj_factor）
CREATE TABLE adj_factor (
    id SERIAL PRIMARY KEY,                -- 自增主键
    ts_code VARCHAR(20) NOT NULL,         -- 股票代码
    trade_date DATE NOT NULL,             -- 交易日期
    adj_factor NUMERIC(16,6) NOT NULL,    -- 复权因子
    CONSTRAINT uk_adj_factor_ts_code_trade_date UNIQUE (ts_code, trade_date)
);

-- 表注释
COMMENT ON TABLE adj_factor IS '复权因子';

-- 列注释
COMMENT ON COLUMN adj_factor.id IS '自增主键';
COMMENT ON COLUMN adj_factor.ts_code IS '股票代码';
COMMENT ON COLUMN adj_factor.trade_date IS '交易日期';
COMMENT ON COLUMN adj_factor.adj_factor IS '复权因子';

-- 添加索引
CREATE INDEX idx_adj_factor_ts_code ON adj_factor(ts_code);
CREATE INDEX idx_adj_factor_trade_date ON adj_factor(trade_date);
CREATE INDEX idx_adj_factor_ts_code_trade_date ON adj_factor(ts_code, trade_date);

-- 添加外键关联到股票基本信息表
ALTER TABLE adj_factor 
ADD CONSTRAINT fk_adj_factor_stock_basic 
FOREIGN KEY (ts_code) 
REFERENCES stock_basic (ts_code);


-- 名称	类型	描述
-- ts_code	str	股票代码
-- trade_date	str	交易日期
-- adj_factor	float	复权因子