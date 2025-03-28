-- 股票数据 - 资金流向

-- 沪深港通资金流向（moneyflow_hsgt）
CREATE TABLE moneyflow_hsgt (
    trade_date DATE NOT NULL PRIMARY KEY,     -- 交易日期
    ggt_ss FLOAT,                             -- 港股通（上海）
    ggt_sz FLOAT,                             -- 港股通（深圳）
    hgt FLOAT,                                -- 沪股通（百万元）
    sgt FLOAT,                                -- 深股通（百万元）
    north_money FLOAT,                        -- 北向资金（百万元）
    south_money FLOAT                         -- 南向资金（百万元）
);

-- 表注释
COMMENT ON TABLE moneyflow_hsgt IS '沪深港通资金流向';

-- 列注释
COMMENT ON COLUMN moneyflow_hsgt.trade_date IS '交易日期';
COMMENT ON COLUMN moneyflow_hsgt.ggt_ss IS '港股通（上海）';
COMMENT ON COLUMN moneyflow_hsgt.ggt_sz IS '港股通（深圳）';
COMMENT ON COLUMN moneyflow_hsgt.hgt IS '沪股通（百万元）';
COMMENT ON COLUMN moneyflow_hsgt.sgt IS '深股通（百万元）';
COMMENT ON COLUMN moneyflow_hsgt.north_money IS '北向资金（百万元）';
COMMENT ON COLUMN moneyflow_hsgt.south_money IS '南向资金（百万元）';

-- 添加索引
CREATE INDEX idx_moneyflow_hsgt_north_money ON moneyflow_hsgt(north_money);
CREATE INDEX idx_moneyflow_hsgt_south_money ON moneyflow_hsgt(south_money);