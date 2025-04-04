-- 股票数据 - 参考数据

-- 股东增减持表（stk_holdertrade）
CREATE TABLE stk_holdertrade (
    -- Primary key and identification fields
    id SERIAL PRIMARY KEY,
    ts_code VARCHAR(10) NOT NULL,
    ann_date DATE,
    
    -- Holder information
    holder_name VARCHAR(100) NOT NULL,
    holder_type VARCHAR(1),  -- G高管P个人C公司
    
    -- Trade information
    in_de VARCHAR(2),        -- 类型IN增持DE减持
    change_vol NUMERIC(20,4), -- 变动数量
    change_ratio NUMERIC(10,4), -- 占流通比例（%）
    after_share NUMERIC(20,4), -- 变动后持股
    after_ratio NUMERIC(10,4), -- 变动后占流通比例（%）
    avg_price NUMERIC(10,4),  -- 平均价格
    total_share NUMERIC(20,4), -- 持股总数
    
    -- Trade period
    begin_date DATE,         -- 增减持开始日期
    close_date DATE          -- 增减持结束日期
);

-- Create indexes for frequently queried fields
CREATE INDEX idx_stk_holdertrade_ts_code ON stk_holdertrade(ts_code);
CREATE INDEX idx_stk_holdertrade_ann_date ON stk_holdertrade(ann_date);
CREATE INDEX idx_stk_holdertrade_holder_name ON stk_holdertrade(holder_name);
CREATE INDEX idx_stk_holdertrade_holder_type ON stk_holdertrade(holder_type);
CREATE INDEX idx_stk_holdertrade_in_de ON stk_holdertrade(in_de);
CREATE INDEX idx_stk_holdertrade_period ON stk_holdertrade(begin_date, close_date);

-- Add unique constraint for upsert operations
ALTER TABLE stk_holdertrade ADD CONSTRAINT stk_holdertrade_unique_key 
UNIQUE (ts_code, ann_date, holder_name, in_de);

-- Add table comment
COMMENT ON TABLE stk_holdertrade IS '股东增减持';

-- Add column comments
COMMENT ON COLUMN stk_holdertrade.ts_code IS 'TS股票代码';
COMMENT ON COLUMN stk_holdertrade.ann_date IS '公告日期';
COMMENT ON COLUMN stk_holdertrade.holder_name IS '股东名称';
COMMENT ON COLUMN stk_holdertrade.holder_type IS '股东类型G高管P个人C公司';
COMMENT ON COLUMN stk_holdertrade.in_de IS '类型IN增持DE减持';
COMMENT ON COLUMN stk_holdertrade.change_vol IS '变动数量';
COMMENT ON COLUMN stk_holdertrade.change_ratio IS '占流通比例（%）';
COMMENT ON COLUMN stk_holdertrade.after_share IS '变动后持股';
COMMENT ON COLUMN stk_holdertrade.after_ratio IS '变动后占流通比例（%）';
COMMENT ON COLUMN stk_holdertrade.avg_price IS '平均价格';
COMMENT ON COLUMN stk_holdertrade.total_share IS '持股总数';
COMMENT ON COLUMN stk_holdertrade.begin_date IS '增减持开始日期';
COMMENT ON COLUMN stk_holdertrade.close_date IS '增减持结束日期';


-- 名称	类型	默认显示	描述
-- ts_code	str	Y	TS代码
-- ann_date	str	Y	公告日期
-- holder_name	str	Y	股东名称
-- holder_type	str	Y	股东类型G高管P个人C公司
-- in_de	str	Y	类型IN增持DE减持
-- change_vol	float	Y	变动数量
-- change_ratio	float	Y	占流通比例（%）
-- after_share	float	Y	变动后持股
-- after_ratio	float	Y	变动后占流通比例（%）
-- avg_price	float	Y	平均价格
-- total_share	float	Y	持股总数
-- begin_date	str	N	增减持开始日期
-- close_date	str	N	增减持结束日期