-- 股票数据 - 财务数据

-- 分红送股（dividend）
CREATE TABLE dividend (
    -- Primary key and identification fields
    id SERIAL PRIMARY KEY,
    ts_code VARCHAR(10) NOT NULL COMMENT 'TS代码',
    end_date DATE COMMENT '分红年度',
    
    -- Announcement dates
    ann_date DATE COMMENT '预案公告日',
    imp_ann_date DATE COMMENT '实施公告日',
    
    -- Status
    div_proc VARCHAR(30) COMMENT '实施进度',
    
    -- Stock allocation rates
    stk_div NUMERIC(10,4) COMMENT '每股送转',
    stk_bo_rate NUMERIC(10,4) COMMENT '每股送股比例',
    stk_co_rate NUMERIC(10,4) COMMENT '每股转增比例',
    
    -- Cash dividend
    cash_div NUMERIC(10,4) COMMENT '每股分红（税后）',
    cash_div_tax NUMERIC(10,4) COMMENT '每股分红（税前）',
    
    -- Important dates
    record_date DATE COMMENT '股权登记日',
    ex_date DATE COMMENT '除权除息日',
    pay_date DATE COMMENT '派息日',
    div_listdate DATE COMMENT '红股上市日',
    
    -- Base information
    base_date DATE COMMENT '基准日',
    base_share NUMERIC(20,4) COMMENT '基准股本（万）',
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for frequently queried fields
CREATE INDEX idx_dividend_ts_code ON dividend(ts_code);
CREATE INDEX idx_dividend_end_date ON dividend(end_date);
CREATE INDEX idx_dividend_ann_date ON dividend(ann_date);
CREATE INDEX idx_dividend_ex_date ON dividend(ex_date);
CREATE INDEX idx_dividend_div_proc ON dividend(div_proc);

-- Add table comment
COMMENT ON TABLE dividend IS '分红送股数据';


-- 名称	类型	默认显示	描述
-- ts_code	str	Y	TS代码
-- end_date	str	Y	分红年度
-- ann_date	str	Y	预案公告日
-- div_proc	str	Y	实施进度
-- stk_div	float	Y	每股送转
-- stk_bo_rate	float	Y	每股送股比例
-- stk_co_rate	float	Y	每股转增比例
-- cash_div	float	Y	每股分红（税后）
-- cash_div_tax	float	Y	每股分红（税前）
-- record_date	str	Y	股权登记日
-- ex_date	str	Y	除权除息日
-- pay_date	str	Y	派息日
-- div_listdate	str	Y	红股上市日
-- imp_ann_date	str	Y	实施公告日
-- base_date	str	N	基准日
-- base_share	float	N	基准股本（万）
