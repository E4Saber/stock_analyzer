-- 股票数据 - 行情数据

-- 备用行情（bak_daily）
CREATE TABLE bak_daily (
    id SERIAL PRIMARY KEY,                -- 自增主键
    ts_code VARCHAR(20) NOT NULL,         -- 股票代码
    trade_date DATE NOT NULL,             -- 交易日期
    name VARCHAR(50) NOT NULL,            -- 股票名称
    pct_change NUMERIC(10,4),             -- 涨跌幅
    close NUMERIC(12,4),                  -- 收盘价
    change NUMERIC(12,4),                 -- 涨跌额
    open NUMERIC(12,4),                   -- 开盘价
    high NUMERIC(12,4),                   -- 最高价
    low NUMERIC(12,4),                    -- 最低价
    pre_close NUMERIC(12,4),              -- 昨收价
    vol_ratio NUMERIC(10,4),              -- 量比
    turn_over NUMERIC(10,4),              -- 换手率
    swing NUMERIC(10,4),                  -- 振幅
    vol NUMERIC(20,2),                    -- 成交量
    amount NUMERIC(20,4),                 -- 成交额
    selling NUMERIC(20,2),                -- 内盘（主动卖，手）
    buying NUMERIC(20,2),                 -- 外盘（主动买， 手）
    total_share NUMERIC(16,4),            -- 总股本(亿)
    float_share NUMERIC(16,4),            -- 流通股本(亿)
    pe NUMERIC(16,4),                     -- 市盈(动)
    industry VARCHAR(50),                 -- 所属行业
    area VARCHAR(50),                     -- 所属地域
    float_mv NUMERIC(20,4),               -- 流通市值
    total_mv NUMERIC(20,4),               -- 总市值
    avg_price NUMERIC(12,4),              -- 平均价
    strength NUMERIC(10,4),               -- 强弱度(%)
    activity NUMERIC(10,4),               -- 活跃度(%)
    avg_turnover NUMERIC(10,4),           -- 笔换手
    attack NUMERIC(10,4),                 -- 攻击波(%)
    interval_3 NUMERIC(10,4),             -- 近3月涨幅
    interval_6 NUMERIC(10,4),             -- 近6月涨幅
    CONSTRAINT uk_bak_daily_ts_code_trade_date UNIQUE (ts_code, trade_date)
);

-- 表注释
COMMENT ON TABLE bak_daily IS '日线行情备份';

-- 列注释
COMMENT ON COLUMN bak_daily.id IS '自增主键';
COMMENT ON COLUMN bak_daily.ts_code IS '股票代码';
COMMENT ON COLUMN bak_daily.trade_date IS '交易日期';
COMMENT ON COLUMN bak_daily.name IS '股票名称';
COMMENT ON COLUMN bak_daily.pct_change IS '涨跌幅';
COMMENT ON COLUMN bak_daily.close IS '收盘价';
COMMENT ON COLUMN bak_daily.change IS '涨跌额';
COMMENT ON COLUMN bak_daily.open IS '开盘价';
COMMENT ON COLUMN bak_daily.high IS '最高价';
COMMENT ON COLUMN bak_daily.low IS '最低价';
COMMENT ON COLUMN bak_daily.pre_close IS '昨收价';
COMMENT ON COLUMN bak_daily.vol_ratio IS '量比';
COMMENT ON COLUMN bak_daily.turn_over IS '换手率';
COMMENT ON COLUMN bak_daily.swing IS '振幅';
COMMENT ON COLUMN bak_daily.vol IS '成交量';
COMMENT ON COLUMN bak_daily.amount IS '成交额';
COMMENT ON COLUMN bak_daily.selling IS '内盘（主动卖，手）';
COMMENT ON COLUMN bak_daily.buying IS '外盘（主动买， 手）';
COMMENT ON COLUMN bak_daily.total_share IS '总股本(亿)';
COMMENT ON COLUMN bak_daily.float_share IS '流通股本(亿)';
COMMENT ON COLUMN bak_daily.pe IS '市盈(动)';
COMMENT ON COLUMN bak_daily.industry IS '所属行业';
COMMENT ON COLUMN bak_daily.area IS '所属地域';
COMMENT ON COLUMN bak_daily.float_mv IS '流通市值';
COMMENT ON COLUMN bak_daily.total_mv IS '总市值';
COMMENT ON COLUMN bak_daily.avg_price IS '平均价';
COMMENT ON COLUMN bak_daily.strength IS '强弱度(%)';
COMMENT ON COLUMN bak_daily.activity IS '活跃度(%)';
COMMENT ON COLUMN bak_daily.avg_turnover IS '笔换手';
COMMENT ON COLUMN bak_daily.attack IS '攻击波(%)';
COMMENT ON COLUMN bak_daily.interval_3 IS '近3月涨幅';
COMMENT ON COLUMN bak_daily.interval_6 IS '近6月涨幅';

-- 添加索引
CREATE INDEX idx_bak_daily_ts_code ON bak_daily(ts_code);
CREATE INDEX idx_bak_daily_trade_date ON bak_daily(trade_date);
CREATE INDEX idx_bak_daily_industry ON bak_daily(industry);
CREATE INDEX idx_bak_daily_area ON bak_daily(area);
CREATE INDEX idx_bak_daily_ts_code_trade_date ON bak_daily(ts_code, trade_date);

-- 添加外键关联到股票基本信息表
ALTER TABLE bak_daily 
ADD CONSTRAINT fk_bak_daily_stock_basic 
FOREIGN KEY (ts_code) 
REFERENCES stock_basic (ts_code);


-- 名称	类型	默认显示	描述
-- ts_code	str	Y	股票代码
-- trade_date	str	Y	交易日期
-- name	str	Y	股票名称
-- pct_change	float	Y	涨跌幅
-- close	float	Y	收盘价
-- change	float	Y	涨跌额
-- open	float	Y	开盘价
-- high	float	Y	最高价
-- low	float	Y	最低价
-- pre_close	float	Y	昨收价
-- vol_ratio	float	Y	量比
-- turn_over	float	Y	换手率
-- swing	float	Y	振幅
-- vol	float	Y	成交量
-- amount	float	Y	成交额
-- selling	float	Y	内盘（主动卖，手）
-- buying	float	Y	外盘（主动买， 手）
-- total_share	float	Y	总股本(亿)
-- float_share	float	Y	流通股本(亿)
-- pe	float	Y	市盈(动)
-- industry	str	Y	所属行业
-- area	str	Y	所属地域
-- float_mv	float	Y	流通市值
-- total_mv	float	Y	总市值
-- avg_price	float	Y	平均价
-- strength	float	Y	强弱度(%)
-- activity	float	Y	活跃度(%)
-- avg_turnover	float	Y	笔换手
-- attack	float	Y	攻击波(%)
-- interval_3	float	Y	近3月涨幅
-- interval_6	float	Y	近6月涨幅