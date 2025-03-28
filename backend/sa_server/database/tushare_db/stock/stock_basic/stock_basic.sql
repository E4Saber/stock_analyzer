-- 股票数据 - 基础数据

-- 股票列表（stock_basic）
CREATE TABLE stock_basic (
    ts_code VARCHAR(20) PRIMARY KEY,     -- TS代码
    symbol VARCHAR(20) NOT NULL,         -- 股票代码
    name VARCHAR(50) NOT NULL,           -- 股票名称
    area VARCHAR(30),                    -- 地域
    industry VARCHAR(50),                -- 所属行业
    fullname VARCHAR(100),               -- 股票全称
    enname VARCHAR(100),                 -- 英文全称
    cnspell VARCHAR(30),                 -- 拼音缩写
    market VARCHAR(30),                  -- 市场类型（主板/创业板/科创板/CDR）
    exchange VARCHAR(20),                -- 交易所代码
    curr_type VARCHAR(20),               -- 交易货币
    list_status VARCHAR(5),              -- 上市状态 L上市 D退市 P暂停上市
    list_date DATE,                      -- 上市日期
    delist_date DATE,                    -- 退市日期
    is_hs VARCHAR(5),                    -- 是否沪深港通标的，N否 H沪股通 S深股通
    act_name VARCHAR(100),               -- 实控人名称
    act_ent_type VARCHAR(50)             -- 实控人企业性质
);

-- 表注释
COMMENT ON TABLE stock_basic IS '股票列表';

-- 列注释
COMMENT ON COLUMN stock_basic.ts_code IS 'TS代码';
COMMENT ON COLUMN stock_basic.symbol IS '股票代码';
COMMENT ON COLUMN stock_basic.name IS '股票名称';
COMMENT ON COLUMN stock_basic.area IS '地域';
COMMENT ON COLUMN stock_basic.industry IS '所属行业';
COMMENT ON COLUMN stock_basic.fullname IS '股票全称';
COMMENT ON COLUMN stock_basic.enname IS '英文全称';
COMMENT ON COLUMN stock_basic.cnspell IS '拼音缩写';
COMMENT ON COLUMN stock_basic.market IS '市场类型（主板/创业板/科创板/CDR）';
COMMENT ON COLUMN stock_basic.exchange IS '交易所代码';
COMMENT ON COLUMN stock_basic.curr_type IS '交易货币';
COMMENT ON COLUMN stock_basic.list_status IS '上市状态 L上市 D退市 P暂停上市';
COMMENT ON COLUMN stock_basic.list_date IS '上市日期';
COMMENT ON COLUMN stock_basic.delist_date IS '退市日期';
COMMENT ON COLUMN stock_basic.is_hs IS '是否沪深港通标的，N否 H沪股通 S深股通';
COMMENT ON COLUMN stock_basic.act_name IS '实控人名称';
COMMENT ON COLUMN stock_basic.act_ent_type IS '实控人企业性质';

-- 添加索引
CREATE INDEX idx_stock_basic_symbol ON stock_basic(symbol);
CREATE INDEX idx_stock_basic_name ON stock_basic(name);
CREATE INDEX idx_stock_basic_industry ON stock_basic(industry);
CREATE INDEX idx_stock_basic_list_date ON stock_basic(list_date);


-- 名称	类型	默认显示	描述
-- ts_code	str	Y	TS代码
-- symbol	str	Y	股票代码
-- name	str	Y	股票名称
-- area	str	Y	地域
-- industry	str	Y	所属行业
-- fullname	str	N	股票全称
-- enname	str	N	英文全称
-- cnspell	str	Y	拼音缩写
-- market	str	Y	市场类型（主板/创业板/科创板/CDR）
-- exchange	str	N	交易所代码
-- curr_type	str	N	交易货币
-- list_status	str	N	上市状态 L上市 D退市 P暂停上市
-- list_date	str	Y	上市日期
-- delist_date	str	N	退市日期
-- is_hs	str	N	是否沪深港通标的，N否 H沪股通 S深股通
-- act_name	str	Y	实控人名称
-- act_ent_type	str	Y	实控人企业性质