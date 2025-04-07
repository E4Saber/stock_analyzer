-- 香港交易日历表（hk_tradecal）
CREATE TABLE hk_tradecal (
    -- Primary key and identification fields
    id SERIAL PRIMARY KEY,
    cal_date DATE NOT NULL,
    is_open INTEGER NOT NULL,
    pretrade_date DATE,
    
    -- Add constraints
    CONSTRAINT hk_tradecal_cal_date_unique UNIQUE (cal_date)
);

-- Create indexes for frequently queried fields
CREATE INDEX idx_hk_tradecal_cal_date ON hk_tradecal(cal_date);
CREATE INDEX idx_hk_tradecal_is_open ON hk_tradecal(is_open);
CREATE INDEX idx_hk_tradecal_pretrade_date ON hk_tradecal(pretrade_date);

-- Add table comment
COMMENT ON TABLE hk_tradecal IS '香港交易日历';

-- Add column comments
COMMENT ON COLUMN hk_tradecal.cal_date IS '日历日期';
COMMENT ON COLUMN hk_tradecal.is_open IS '是否交易 0-休市 1-交易';
COMMENT ON COLUMN hk_tradecal.pretrade_date IS '上一个交易日';


-- 名称	类型	默认显示	描述
-- cal_date	str	Y	日历日期
-- is_open	int	Y	是否交易 '0'休市 '1'交易
-- pretrade_date	str	Y	上一个交易日