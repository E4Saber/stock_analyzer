-- 股票数据 - 行情数据

-- 每日指标（daily_basic）
CREATE TABLE daily_basic (
    id SERIAL PRIMARY KEY,                -- 自增主键
    ts_code VARCHAR(20) NOT NULL,         -- TS股票代码
    trade_date DATE NOT NULL,             -- 交易日期
    close NUMERIC(12,4),                  -- 当日收盘价
    turnover_rate NUMERIC(10,4),          -- 换手率（%）
    turnover_rate_f NUMERIC(10,4),        -- 换手率（自由流通股）
    volume_ratio NUMERIC(10,4),           -- 量比
    pe NUMERIC(16,4),                     -- 市盈率（总市值/净利润， 亏损的PE为空）
    pe_ttm NUMERIC(16,4),                 -- 市盈率（TTM，亏损的PE为空）
    pb NUMERIC(10,4),                     -- 市净率（总市值/净资产）
    ps NUMERIC(10,4),                     -- 市销率
    ps_ttm NUMERIC(10,4),                 -- 市销率（TTM）
    dv_ratio NUMERIC(10,4),               -- 股息率 （%）
    dv_ttm NUMERIC(10,4),                 -- 股息率（TTM）（%）
    total_share NUMERIC(16,4),            -- 总股本 （万股）
    float_share NUMERIC(16,4),            -- 流通股本 （万股）
    free_share NUMERIC(16,4),             -- 自由流通股本 （万）
    total_mv NUMERIC(20,4),               -- 总市值 （万元）
    circ_mv NUMERIC(20,4),                -- 流通市值（万元）
    CONSTRAINT uk_daily_basic_ts_code_trade_date UNIQUE (ts_code, trade_date)
);

-- 表注释
COMMENT ON TABLE daily_basic IS '每日基本面指标';

-- 列注释
COMMENT ON COLUMN daily_basic.id IS '自增主键';
COMMENT ON COLUMN daily_basic.ts_code IS 'TS股票代码';
COMMENT ON COLUMN daily_basic.trade_date IS '交易日期';
COMMENT ON COLUMN daily_basic.close IS '当日收盘价';
COMMENT ON COLUMN daily_basic.turnover_rate IS '换手率（%）';
COMMENT ON COLUMN daily_basic.turnover_rate_f IS '换手率（自由流通股）';
COMMENT ON COLUMN daily_basic.volume_ratio IS '量比';
COMMENT ON COLUMN daily_basic.pe IS '市盈率（总市值/净利润， 亏损的PE为空）';
COMMENT ON COLUMN daily_basic.pe_ttm IS '市盈率（TTM，亏损的PE为空）';
COMMENT ON COLUMN daily_basic.pb IS '市净率（总市值/净资产）';
COMMENT ON COLUMN daily_basic.ps IS '市销率';
COMMENT ON COLUMN daily_basic.ps_ttm IS '市销率（TTM）';
COMMENT ON COLUMN daily_basic.dv_ratio IS '股息率 （%）';
COMMENT ON COLUMN daily_basic.dv_ttm IS '股息率（TTM）（%）';
COMMENT ON COLUMN daily_basic.total_share IS '总股本 （万股）';
COMMENT ON COLUMN daily_basic.float_share IS '流通股本 （万股）';
COMMENT ON COLUMN daily_basic.free_share IS '自由流通股本 （万）';
COMMENT ON COLUMN daily_basic.total_mv IS '总市值 （万元）';
COMMENT ON COLUMN daily_basic.circ_mv IS '流通市值（万元）';

-- 添加索引
CREATE INDEX idx_daily_basic_ts_code ON daily_basic(ts_code);
CREATE INDEX idx_daily_basic_trade_date ON daily_basic(trade_date);
CREATE INDEX idx_daily_basic_ts_code_trade_date ON daily_basic(ts_code, trade_date);

-- 添加外键关联到股票基本信息表
ALTER TABLE daily_basic 
ADD CONSTRAINT fk_daily_basic_stock_basic 
FOREIGN KEY (ts_code) 
REFERENCES stock_basic (ts_code);


-- 名称	类型	描述
-- ts_code	str	TS股票代码
-- trade_date	str	交易日期
-- close	float	当日收盘价
-- turnover_rate	float	换手率（%）
-- turnover_rate_f	float	换手率（自由流通股）
-- volume_ratio	float	量比
-- pe	float	市盈率（总市值/净利润， 亏损的PE为空）
-- pe_ttm	float	市盈率（TTM，亏损的PE为空）
-- pb	float	市净率（总市值/净资产）
-- ps	float	市销率
-- ps_ttm	float	市销率（TTM）
-- dv_ratio	float	股息率 （%）
-- dv_ttm	float	股息率（TTM）（%）
-- total_share	float	总股本 （万股）
-- float_share	float	流通股本 （万股）
-- free_share	float	自由流通股本 （万）
-- total_mv	float	总市值 （万元）
-- circ_mv	float	流通市值（万元）