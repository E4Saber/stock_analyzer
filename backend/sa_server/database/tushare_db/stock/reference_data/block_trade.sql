-- 股票数据 - 参考数据

-- 大宗交易表（block_trade）
CREATE TABLE block_trade (
    -- Primary key and identification fields
    id SERIAL PRIMARY KEY,
    ts_code VARCHAR(10) NOT NULL,
    trade_date DATE NOT NULL,
    
    -- Transaction information
    price NUMERIC(20,4),          -- 成交价
    vol NUMERIC(20,4),            -- 成交量（万股）
    amount NUMERIC(20,4),         -- 成交金额
    buyer VARCHAR(100),           -- 买方营业部
    seller VARCHAR(100)           -- 卖方营业部
);

-- Create indexes for frequently queried fields
CREATE INDEX idx_block_trade_ts_code ON block_trade(ts_code);
CREATE INDEX idx_block_trade_trade_date ON block_trade(trade_date);
CREATE INDEX idx_block_trade_buyer ON block_trade(buyer);
CREATE INDEX idx_block_trade_seller ON block_trade(seller);

-- Add unique constraint for upsert operations
ALTER TABLE block_trade ADD CONSTRAINT block_trade_unique_key 
UNIQUE (ts_code, trade_date, buyer, seller, price, vol);

-- Add table comment
COMMENT ON TABLE block_trade IS '大宗交易';

-- Add column comments
COMMENT ON COLUMN block_trade.ts_code IS 'TS股票代码';
COMMENT ON COLUMN block_trade.trade_date IS '交易日历';
COMMENT ON COLUMN block_trade.price IS '成交价';
COMMENT ON COLUMN block_trade.vol IS '成交量（万股）';
COMMENT ON COLUMN block_trade.amount IS '成交金额';
COMMENT ON COLUMN block_trade.buyer IS '买方营业部';
COMMENT ON COLUMN block_trade.seller IS '卖方营业部';

-- 名称	类型	描述
-- ts_code	str	TS代码
-- trade_date	str	交易日历
-- price	float	成交价
-- vol	float	成交量（万股）
-- amount	float	成交金额
-- buyer	str	买方营业部
-- seller	str	卖方营业部