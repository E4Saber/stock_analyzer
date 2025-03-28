-- 股票数据 - 财务数据

-- 业绩预告（forecast）
CREATE TABLE forecast (
    -- Primary key and identification fields
    id SERIAL PRIMARY KEY,
    ts_code VARCHAR(10) NOT NULL COMMENT 'TS股票代码',
    ann_date DATE COMMENT '公告日期',
    end_date DATE COMMENT '报告期',
    
    -- Forecast type and summary
    type VARCHAR(20) COMMENT '业绩预告类型(预增/预减/扭亏/首亏/续亏/续盈/略增/略减)',
    summary TEXT COMMENT '业绩预告摘要',
    
    -- Change percentage range
    p_change_min NUMERIC(20,4) COMMENT '预告净利润变动幅度下限（%）',
    p_change_max NUMERIC(20,4) COMMENT '预告净利润变动幅度上限（%）',
    
    -- Profit forecast range
    net_profit_min NUMERIC(20,4) COMMENT '预告净利润下限（万元）',
    net_profit_max NUMERIC(20,4) COMMENT '预告净利润上限（万元）',
    
    -- Previous period comparison
    last_parent_net NUMERIC(20,4) COMMENT '上年同期归属母公司净利润',
    
    -- Additional info
    first_ann_date DATE COMMENT '首次公告日',
    change_reason TEXT COMMENT '业绩变动原因',
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for frequently queried fields
CREATE INDEX idx_forecast_ts_code ON forecast(ts_code);
CREATE INDEX idx_forecast_ann_date ON forecast(ann_date);
CREATE INDEX idx_forecast_end_date ON forecast(end_date);
CREATE INDEX idx_forecast_type ON forecast(type);

-- Add table comment
COMMENT ON TABLE forecast IS '业绩预告数据';


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
