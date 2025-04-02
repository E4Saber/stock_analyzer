-- 股票数据 - 主营业务构成数据

-- 主营业务构成表（fina_mainbz）
CREATE TABLE fina_mainbz (
    -- Primary key and identification fields
    id SERIAL PRIMARY KEY,
    ts_code VARCHAR(10) NOT NULL,
    end_date DATE,
    
    -- 主营业务构成字段
    bz_item VARCHAR(100),
    bz_sales NUMERIC(20,2),
    bz_profit NUMERIC(20,2),
    bz_cost NUMERIC(20,2),
    curr_type VARCHAR(10),
    
    -- 类型区分
    type VARCHAR(1),
    
    -- 更新标识
    update_flag VARCHAR(10)
);

-- Create indexes for frequently queried fields
CREATE INDEX idx_fina_mainbz_ts_code ON fina_mainbz(ts_code);
CREATE INDEX idx_fina_mainbz_end_date ON fina_mainbz(end_date);
CREATE INDEX idx_fina_mainbz_type ON fina_mainbz(type);
CREATE INDEX idx_fina_mainbz_bz_item ON fina_mainbz(bz_item);

-- Add unique constraint for upsert operations
ALTER TABLE fina_mainbz ADD CONSTRAINT fina_mainbz_ts_code_end_date_bz_item_key 
UNIQUE (ts_code, end_date, bz_item);

-- Add table comment
COMMENT ON TABLE fina_mainbz IS '主营业务构成表';

-- Add column comments
COMMENT ON COLUMN fina_mainbz.ts_code IS 'TS代码';
COMMENT ON COLUMN fina_mainbz.end_date IS '报告期';
COMMENT ON COLUMN fina_mainbz.bz_item IS '主营业务来源';
COMMENT ON COLUMN fina_mainbz.bz_sales IS '主营业务收入(元)';
COMMENT ON COLUMN fina_mainbz.bz_profit IS '主营业务利润(元)';
COMMENT ON COLUMN fina_mainbz.bz_cost IS '主营业务成本(元)';
COMMENT ON COLUMN fina_mainbz.curr_type IS '货币代码';
COMMENT ON COLUMN fina_mainbz.type IS '类型（P按产品 D按地区 I按行业）';
COMMENT ON COLUMN fina_mainbz.update_flag IS '是否更新';


-- 名称	类型	描述
-- ts_code	str	TS代码
-- end_date	str	报告期
-- bz_item	str	主营业务来源
-- bz_sales	float	主营业务收入(元)
-- bz_profit	float	主营业务利润(元)
-- bz_cost	float	主营业务成本(元)
-- curr_type	str	货币代码
-- update_flag	str	是否更新
