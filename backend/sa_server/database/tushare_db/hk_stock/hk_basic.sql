-- 香港股票基本信息表（hk_basic）
CREATE TABLE hk_basic (
    -- Primary key and identification fields
    id SERIAL PRIMARY KEY,
    ts_code VARCHAR(12) NOT NULL,
    
    -- Basic information
    name VARCHAR(100),
    fullname VARCHAR(200),
    enname VARCHAR(200),
    cn_spell VARCHAR(50),
    market VARCHAR(20),
    list_status VARCHAR(1),
    list_date DATE,
    delist_date DATE,
    trade_unit FLOAT,
    isin VARCHAR(20),
    curr_type VARCHAR(10)
);

-- Create indexes for frequently queried fields
CREATE INDEX idx_hk_basic_ts_code ON hk_basic(ts_code);
CREATE INDEX idx_hk_basic_list_status ON hk_basic(list_status);
CREATE INDEX idx_hk_basic_list_date ON hk_basic(list_date);

-- Add unique constraint for upsert operations
ALTER TABLE hk_basic ADD CONSTRAINT hk_basic_unique_key 
UNIQUE (ts_code);

-- Add table comment
COMMENT ON TABLE hk_basic IS '香港股票基本信息';

-- Add column comments
COMMENT ON COLUMN hk_basic.ts_code IS 'TS代码';
COMMENT ON COLUMN hk_basic.name IS '股票简称';
COMMENT ON COLUMN hk_basic.fullname IS '公司全称';
COMMENT ON COLUMN hk_basic.enname IS '英文名称';
COMMENT ON COLUMN hk_basic.cn_spell IS '拼音';
COMMENT ON COLUMN hk_basic.market IS '市场类别';
COMMENT ON COLUMN hk_basic.list_status IS '上市状态 L上市 D退市 P暂停上市';
COMMENT ON COLUMN hk_basic.list_date IS '上市日期';
COMMENT ON COLUMN hk_basic.delist_date IS '退市日期';
COMMENT ON COLUMN hk_basic.trade_unit IS '交易单位';
COMMENT ON COLUMN hk_basic.isin IS 'ISIN代码';
COMMENT ON COLUMN hk_basic.curr_type IS '货币代码';


-- 名称	类型	默认显示	描述
-- ts_code	str	Y	
-- name	str	Y	股票简称
-- fullname	str	Y	公司全称
-- enname	str	Y	英文名称
-- cn_spell	str	Y	拼音
-- market	str	Y	市场类别
-- list_status	str	Y	上市状态
-- list_date	str	Y	上市日期
-- delist_date	str	Y	退市日期
-- trade_unit	float	Y	交易单位
-- isin	str	Y	ISIN代码
-- curr_type	str	Y	货币代码