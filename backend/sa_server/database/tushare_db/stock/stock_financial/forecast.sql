-- 股票数据 - 业绩预告数据

-- 业绩预告表（forecast）
CREATE TABLE forecast (
    -- Primary key and identification fields
    id SERIAL PRIMARY KEY,
    ts_code VARCHAR(10) NOT NULL,
    ann_date DATE,
    end_date DATE,
    type VARCHAR(20),
    
    -- 预告净利润变动幅度
    p_change_min NUMERIC(20,4),
    p_change_max NUMERIC(20,4),
    
    -- 预告净利润金额
    net_profit_min NUMERIC(20,4),
    net_profit_max NUMERIC(20,4),
    
    -- 上年同期数据
    last_parent_net NUMERIC(20,4),
    
    -- 公告信息
    first_ann_date DATE,
    summary TEXT,
    change_reason TEXT
);

-- Create indexes for frequently queried fields
CREATE INDEX idx_forecast_ts_code ON forecast(ts_code);
CREATE INDEX idx_forecast_ann_date ON forecast(ann_date);
CREATE INDEX idx_forecast_end_date ON forecast(end_date);
CREATE INDEX idx_forecast_type ON forecast(type);

-- Add unique constraint for upsert operations
ALTER TABLE forecast ADD CONSTRAINT forecast_ts_code_end_date_key 
UNIQUE (ts_code, end_date);

-- Add table comment
COMMENT ON TABLE forecast IS '业绩预告';

-- Add column comments
COMMENT ON COLUMN forecast.ts_code IS 'TS股票代码';
COMMENT ON COLUMN forecast.ann_date IS '公告日期';
COMMENT ON COLUMN forecast.end_date IS '报告期';
COMMENT ON COLUMN forecast.type IS '业绩预告类型(预增/预减/扭亏/首亏/续亏/续盈/略增/略减)';
COMMENT ON COLUMN forecast.p_change_min IS '预告净利润变动幅度下限（%）';
COMMENT ON COLUMN forecast.p_change_max IS '预告净利润变动幅度上限（%）';
COMMENT ON COLUMN forecast.net_profit_min IS '预告净利润下限（万元）';
COMMENT ON COLUMN forecast.net_profit_max IS '预告净利润上限（万元）';
COMMENT ON COLUMN forecast.last_parent_net IS '上年同期归属母公司净利润（万元）';
COMMENT ON COLUMN forecast.first_ann_date IS '首次公告日';
COMMENT ON COLUMN forecast.summary IS '业绩预告摘要';
COMMENT ON COLUMN forecast.change_reason IS '业绩变动原因';


-- 名称	类型	描述
-- ts_code	str	TS股票代码
-- ann_date	str	公告日期
-- end_date	str	报告期
-- type	str	业绩预告类型(预增/预减/扭亏/首亏/续亏/续盈/略增/略减)
-- p_change_min	float	预告净利润变动幅度下限（%）
-- p_change_max	float	预告净利润变动幅度上限（%）
-- net_profit_min	float	预告净利润下限（万元）
-- net_profit_max	float	预告净利润上限（万元）
-- last_parent_net	float	上年同期归属母公司净利润
-- first_ann_date	str	首次公告日
-- summary	str	业绩预告摘要
-- change_reason	str	业绩变动原因