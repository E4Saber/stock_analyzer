-- 股票数据 - 财务数据

-- 主营业务构成（fina_mainbz）
CREATE TABLE fina_mainbz (
    -- Primary key and identification fields
    id SERIAL PRIMARY KEY,
    ts_code VARCHAR(10) NOT NULL COMMENT 'TS代码',
    end_date DATE COMMENT '报告期',
    
    -- Business composition information
    bz_item VARCHAR(200) COMMENT '主营业务来源',
    bz_sales NUMERIC(20,2) COMMENT '主营业务收入(元)',
    bz_profit NUMERIC(20,2) COMMENT '主营业务利润(元)',
    bz_cost NUMERIC(20,2) COMMENT '主营业务成本(元)',
    
    -- Additional information
    curr_type VARCHAR(10) COMMENT '货币代码',
    update_flag VARCHAR(10) COMMENT '是否更新',
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for frequently queried fields
CREATE INDEX idx_fina_mainbz_ts_code ON fina_mainbz(ts_code);
CREATE INDEX idx_fina_mainbz_end_date ON fina_mainbz(end_date);
CREATE INDEX idx_fina_mainbz_bz_item ON fina_mainbz(bz_item);
CREATE INDEX idx_fina_mainbz_curr_type ON fina_mainbz(curr_type);

-- Add table comment
COMMENT ON TABLE fina_mainbz IS '营业务构成数据';


-- 名称	类型	描述
-- ts_code	str	TS代码
-- end_date	str	报告期
-- bz_item	str	主营业务来源
-- bz_sales	float	主营业务收入(元)
-- bz_profit	float	主营业务利润(元)
-- bz_cost	float	主营业务成本(元)
-- curr_type	str	货币代码
-- update_flag	str	是否更新