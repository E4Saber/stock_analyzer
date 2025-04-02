-- 股票数据 - 分红送股数据

-- 分红送股表（dividend）
CREATE TABLE dividend (
    -- Primary key and identification fields
    id SERIAL PRIMARY KEY,
    ts_code VARCHAR(10) NOT NULL,
    end_date DATE,
    ann_date DATE,
    
    -- Dividend process and status
    div_proc VARCHAR(20),
    
    -- Stock dividend related fields
    stk_div NUMERIC(20,4),
    stk_bo_rate NUMERIC(20,4),
    stk_co_rate NUMERIC(20,4),
    
    -- Cash dividend related fields
    cash_div NUMERIC(20,4),
    cash_div_tax NUMERIC(20,4),
    
    -- Important dates
    record_date DATE,
    ex_date DATE,
    pay_date DATE,
    div_listdate DATE,
    imp_ann_date DATE,
    
    -- Additional fields
    base_date DATE,
    base_share NUMERIC(20,4)
);

-- Create indexes for frequently queried fields
CREATE INDEX idx_dividend_ts_code ON dividend(ts_code);
CREATE INDEX idx_dividend_end_date ON dividend(end_date);
CREATE INDEX idx_dividend_ex_date ON dividend(ex_date);
CREATE INDEX idx_dividend_record_date ON dividend(record_date);

-- Add unique constraint for upsert operations
ALTER TABLE dividend ADD CONSTRAINT dividend_ts_code_end_date_ann_date_key 
UNIQUE (ts_code, end_date, ann_date);

-- Add table comment
COMMENT ON TABLE dividend IS '分红送股表';

-- Add column comments
COMMENT ON COLUMN dividend.ts_code IS 'TS代码';
COMMENT ON COLUMN dividend.end_date IS '分红年度';
COMMENT ON COLUMN dividend.ann_date IS '预案公告日';
COMMENT ON COLUMN dividend.div_proc IS '实施进度';
COMMENT ON COLUMN dividend.stk_div IS '每股送转';
COMMENT ON COLUMN dividend.stk_bo_rate IS '每股送股比例';
COMMENT ON COLUMN dividend.stk_co_rate IS '每股转增比例';
COMMENT ON COLUMN dividend.cash_div IS '每股分红（税后）';
COMMENT ON COLUMN dividend.cash_div_tax IS '每股分红（税前）';
COMMENT ON COLUMN dividend.record_date IS '股权登记日';
COMMENT ON COLUMN dividend.ex_date IS '除权除息日';
COMMENT ON COLUMN dividend.pay_date IS '派息日';
COMMENT ON COLUMN dividend.div_listdate IS '红股上市日';
COMMENT ON COLUMN dividend.imp_ann_date IS '实施公告日';
COMMENT ON COLUMN dividend.base_date IS '基准日';
COMMENT ON COLUMN dividend.base_share IS '基准股本（万）';


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