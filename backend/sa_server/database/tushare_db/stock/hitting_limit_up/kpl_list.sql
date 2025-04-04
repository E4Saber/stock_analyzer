-- 涨停板列表表（kpl_list）
CREATE TABLE kpl_list (
    -- Primary key and identification fields
    id SERIAL PRIMARY KEY,
    ts_code VARCHAR(12) NOT NULL,
    name VARCHAR(100) NOT NULL,
    trade_date DATE NOT NULL,
    
    -- Time fields
    lu_time VARCHAR(10),
    ld_time VARCHAR(10),
    open_time VARCHAR(10),
    last_time VARCHAR(10),
    
    -- Description and category fields
    lu_desc TEXT,
    tag VARCHAR(20),
    theme VARCHAR(100),
    status VARCHAR(20),
    
    -- Numeric fields
    net_change NUMERIC(20, 2),
    bid_amount NUMERIC(20, 2),
    bid_change NUMERIC(20, 2),
    bid_turnover NUMERIC(10, 4),
    lu_bid_vol NUMERIC(20, 2),
    pct_chg NUMERIC(10, 4),
    bid_pct_chg NUMERIC(10, 4),
    rt_pct_chg NUMERIC(10, 4),
    limit_order NUMERIC(20, 2),
    amount NUMERIC(20, 2),
    turnover_rate NUMERIC(10, 4),
    free_float NUMERIC(20, 2),
    lu_limit_order NUMERIC(20, 2)
);

-- Create indexes for frequently queried fields
CREATE INDEX idx_kpl_list_ts_code ON kpl_list(ts_code);
CREATE INDEX idx_kpl_list_trade_date ON kpl_list(trade_date);
CREATE INDEX idx_kpl_list_tag ON kpl_list(tag);
CREATE INDEX idx_kpl_list_status ON kpl_list(status);
CREATE INDEX idx_kpl_list_theme ON kpl_list(theme);

-- Add unique constraint for upsert operations
ALTER TABLE kpl_list ADD CONSTRAINT kpl_list_unique_key 
UNIQUE (ts_code, trade_date);

-- Add table comment
COMMENT ON TABLE kpl_list IS '涨停板列表';

-- Add column comments
COMMENT ON COLUMN kpl_list.ts_code IS '代码';
COMMENT ON COLUMN kpl_list.name IS '名称';
COMMENT ON COLUMN kpl_list.trade_date IS '交易时间';
COMMENT ON COLUMN kpl_list.lu_time IS '涨停时间';
COMMENT ON COLUMN kpl_list.ld_time IS '跌停时间';
COMMENT ON COLUMN kpl_list.open_time IS '开板时间';
COMMENT ON COLUMN kpl_list.last_time IS '最后涨停时间';
COMMENT ON COLUMN kpl_list.lu_desc IS '涨停原因';
COMMENT ON COLUMN kpl_list.tag IS '标签';
COMMENT ON COLUMN kpl_list.theme IS '板块';
COMMENT ON COLUMN kpl_list.net_change IS '主力净额(元)';
COMMENT ON COLUMN kpl_list.bid_amount IS '竞价成交额(元)';
COMMENT ON COLUMN kpl_list.status IS '状态（N连板）';
COMMENT ON COLUMN kpl_list.bid_change IS '竞价净额';
COMMENT ON COLUMN kpl_list.bid_turnover IS '竞价换手%';
COMMENT ON COLUMN kpl_list.lu_bid_vol IS '涨停委买额';
COMMENT ON COLUMN kpl_list.pct_chg IS '涨跌幅%';
COMMENT ON COLUMN kpl_list.bid_pct_chg IS '竞价涨幅%';
COMMENT ON COLUMN kpl_list.rt_pct_chg IS '实时涨幅%';
COMMENT ON COLUMN kpl_list.limit_order IS '封单';
COMMENT ON COLUMN kpl_list.amount IS '成交额';
COMMENT ON COLUMN kpl_list.turnover_rate IS '换手率%';
COMMENT ON COLUMN kpl_list.free_float IS '实际流通';
COMMENT ON COLUMN kpl_list.lu_limit_order IS '最大封单';


-- 名称	类型	默认显示	描述
-- ts_code	str	Y	代码
-- name	str	Y	名称
-- trade_date	str	Y	交易时间
-- lu_time	str	Y	涨停时间
-- ld_time	str	Y	跌停时间
-- open_time	str	Y	开板时间
-- last_time	str	Y	最后涨停时间
-- lu_desc	str	Y	涨停原因
-- tag	str	Y	标签
-- theme	str	Y	板块
-- net_change	float	Y	主力净额(元)
-- bid_amount	float	Y	竞价成交额(元)
-- status	str	Y	状态（N连板）
-- bid_change	float	Y	竞价净额
-- bid_turnover	float	Y	竞价换手%
-- lu_bid_vol	float	Y	涨停委买额
-- pct_chg	float	Y	涨跌幅%
-- bid_pct_chg	float	Y	竞价涨幅%
-- rt_pct_chg	float	Y	实时涨幅%
-- limit_order	float	Y	封单
-- amount	float	Y	成交额
-- turnover_rate	float	Y	换手率%
-- free_float	float	Y	实际流通
-- lu_limit_order	float	Y	最大封单