-- 股票数据 - 参考数据

-- 股票回购表（repurchase）
CREATE TABLE repurchase (
    -- Primary key and identification fields
    id SERIAL PRIMARY KEY,
    ts_code VARCHAR(10) NOT NULL,
    ann_date DATE,
    end_date DATE,
    
    -- Repurchase information
    proc VARCHAR(100),          -- 进度
    exp_date DATE,              -- 过期日期
    vol NUMERIC(20,4),          -- 回购数量
    amount NUMERIC(20,4),       -- 回购金额
    high_limit NUMERIC(20,4),   -- 回购最高价
    low_limit NUMERIC(20,4)     -- 回购最低价
);

-- Create indexes for frequently queried fields
CREATE INDEX idx_repurchase_ts_code ON repurchase(ts_code);
CREATE INDEX idx_repurchase_ann_date ON repurchase(ann_date);
CREATE INDEX idx_repurchase_end_date ON repurchase(end_date);
CREATE INDEX idx_repurchase_exp_date ON repurchase(exp_date);

-- Add unique constraint for upsert operations
ALTER TABLE repurchase ADD CONSTRAINT repurchase_unique_key 
UNIQUE (ts_code, ann_date, end_date);

-- Add table comment
COMMENT ON TABLE repurchase IS '股票回购';

-- Add column comments
COMMENT ON COLUMN repurchase.ts_code IS 'TS股票代码';
COMMENT ON COLUMN repurchase.ann_date IS '公告日期';
COMMENT ON COLUMN repurchase.end_date IS '截止日期';
COMMENT ON COLUMN repurchase.proc IS '进度';
COMMENT ON COLUMN repurchase.exp_date IS '过期日期';
COMMENT ON COLUMN repurchase.vol IS '回购数量';
COMMENT ON COLUMN repurchase.amount IS '回购金额';
COMMENT ON COLUMN repurchase.high_limit IS '回购最高价';
COMMENT ON COLUMN repurchase.low_limit IS '回购最低价';

-- 名称	类型	描述
-- ts_code	str	TS代码
-- ann_date	str	公告日期
-- end_date	str	截止日期
-- proc	str	进度
-- exp_date	str	过期日期
-- vol	float	回购数量
-- amount	float	回购金额
-- high_limit	float	回购最高价
-- low_limit	float	回购最低价