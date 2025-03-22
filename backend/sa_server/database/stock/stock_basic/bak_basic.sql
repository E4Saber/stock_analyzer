-- 股票数据 - 基础数据

-- 股票历史列表（历史每天股票列表）（bak_basic）
CREATE TABLE bak_basic (
    trade_date DATE NOT NULL,             -- 交易日期
    ts_code VARCHAR(20) NOT NULL,         -- TS股票代码
    name VARCHAR(50) NOT NULL,            -- 股票名称
    industry VARCHAR(50),                 -- 行业
    area VARCHAR(30),                     -- 地域
    pe NUMERIC(10,2),                     -- 市盈率（动）
    float_share NUMERIC(20,4),            -- 流通股本（亿）
    total_share NUMERIC(20,4),            -- 总股本（亿）
    total_assets NUMERIC(20,2),           -- 总资产（亿）
    liquid_assets NUMERIC(20,2),          -- 流动资产（亿）
    fixed_assets NUMERIC(20,2),           -- 固定资产（亿）
    reserved NUMERIC(20,2),               -- 公积金
    reserved_pershare NUMERIC(10,4),      -- 每股公积金
    eps NUMERIC(10,4),                    -- 每股收益
    bvps NUMERIC(10,4),                   -- 每股净资产
    pb NUMERIC(10,2),                     -- 市净率
    list_date DATE,                       -- 上市日期
    undp NUMERIC(20,2),                   -- 未分配利润
    per_undp NUMERIC(10,4),               -- 每股未分配利润
    rev_yoy NUMERIC(10,2),                -- 收入同比（%）
    profit_yoy NUMERIC(10,2),             -- 利润同比（%）
    gpr NUMERIC(10,2),                    -- 毛利率（%）
    npr NUMERIC(10,2),                    -- 净利润率（%）
    holder_num INTEGER,                   -- 股东人数
    
    PRIMARY KEY (trade_date, ts_code)     -- 复合主键
);

-- 添加外键约束
ALTER TABLE bak_basic
ADD CONSTRAINT fk_bak_basic_stock_basic
FOREIGN KEY (ts_code) REFERENCES stock_basic(ts_code);

-- 添加索引
CREATE INDEX idx_bak_basic_ts_code ON bak_basic(ts_code);
CREATE INDEX idx_bak_basic_trade_date ON bak_basic(trade_date);
CREATE INDEX idx_bak_basic_industry ON bak_basic(industry);


-- 名称	类型	默认显示	描述
-- trade_date	str	Y	交易日期
-- ts_code	str	Y	TS股票代码
-- name	str	Y	股票名称
-- industry	str	Y	行业
-- area	str	Y	地域
-- pe	float	Y	市盈率（动）
-- float_share	float	Y	流通股本（亿）
-- total_share	float	Y	总股本（亿）
-- total_assets	float	Y	总资产（亿）
-- liquid_assets	float	Y	流动资产（亿）
-- fixed_assets	float	Y	固定资产（亿）
-- reserved	float	Y	公积金
-- reserved_pershare	float	Y	每股公积金
-- eps	float	Y	每股收益
-- bvps	float	Y	每股净资产
-- pb	float	Y	市净率
-- list_date	str	Y	上市日期
-- undp	float	Y	未分配利润
-- per_undp	float	Y	每股未分配利润
-- rev_yoy	float	Y	收入同比（%）
-- profit_yoy	float	Y	利润同比（%）
-- gpr	float	Y	毛利率（%）
-- npr	float	Y	净利润率（%）
-- holder_num	int	Y	股东人数