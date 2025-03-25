-- 股票数据 - 基础数据

-- IPO新股列表（new_share）
CREATE TABLE new_share (
    ts_code VARCHAR(20) PRIMARY KEY,      -- TS股票代码
    sub_code VARCHAR(20),                 -- 申购代码
    name VARCHAR(50) NOT NULL,            -- 名称
    ipo_date DATE,                        -- 上网发行日期
    issue_date DATE,                      -- 上市日期
    amount NUMERIC(20,2),                 -- 发行总量（万股）
    market_amount NUMERIC(20,2),          -- 上网发行总量（万股）
    price NUMERIC(10,2),                  -- 发行价格
    pe NUMERIC(10,2),                     -- 市盈率
    limit_amount NUMERIC(10,2),           -- 个人申购上限（万股）
    funds NUMERIC(10,2),                  -- 募集资金（亿元）
    ballot NUMERIC(10,4),                 -- 中签率
    
    CONSTRAINT fk_new_share_stock_basic
    FOREIGN KEY (ts_code) REFERENCES stock_basic(ts_code)
);

-- 添加表注释
COMMENT ON TABLE new_share IS 'IPO新股发行信息';

-- 添加字段注释
COMMENT ON COLUMN new_share.ts_code IS 'TS股票代码';
COMMENT ON COLUMN new_share.sub_code IS '申购代码';
COMMENT ON COLUMN new_share.name IS '股票名称';
COMMENT ON COLUMN new_share.ipo_date IS '上网发行日期';
COMMENT ON COLUMN new_share.issue_date IS '上市日期';
COMMENT ON COLUMN new_share.amount IS '发行总量（万股）';
COMMENT ON COLUMN new_share.market_amount IS '上网发行总量（万股）';
COMMENT ON COLUMN new_share.price IS '发行价格（元）';
COMMENT ON COLUMN new_share.pe IS '市盈率';
COMMENT ON COLUMN new_share.limit_amount IS '个人申购上限（万股）';
COMMENT ON COLUMN new_share.funds IS '募集资金（亿元）';
COMMENT ON COLUMN new_share.ballot IS '中签率';

-- 添加索引
CREATE INDEX idx_new_share_sub_code ON new_share(sub_code);
CREATE INDEX idx_new_share_ipo_date ON new_share(ipo_date);
CREATE INDEX idx_new_share_issue_date ON new_share(issue_date);


-- 名称	类型	默认显示	描述
-- ts_code	str	Y	TS股票代码
-- sub_code	str	Y	申购代码
-- name	str	Y	名称
-- ipo_date	str	Y	上网发行日期
-- issue_date	str	Y	上市日期
-- amount	float	Y	发行总量（万股）
-- market_amount	float	Y	上网发行总量（万股）
-- price	float	Y	发行价格
-- pe	float	Y	市盈率
-- limit_amount	float	Y	个人申购上限（万股）
-- funds	float	Y	募集资金（亿元）
-- ballot	float	Y	中签率