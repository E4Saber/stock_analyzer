-- 美国国库券利率数据表

-- 美国国库券利率（us_tbr）
CREATE TABLE us_tbr (
    date DATE PRIMARY KEY,           -- 日期
    w4_bd FLOAT,                     -- 4周银行折现收益率
    w4_ce FLOAT,                     -- 4周票面利率
    w8_bd FLOAT,                     -- 8周银行折现收益率
    w8_ce FLOAT,                     -- 8周票面利率
    w13_bd FLOAT,                    -- 13周银行折现收益率
    w13_ce FLOAT,                    -- 13周票面利率
    w17_bd FLOAT,                    -- 17周银行折现收益率（数据从20221019开始）
    w17_ce FLOAT,                    -- 17周票面利率（数据从20221019开始）
    w26_bd FLOAT,                    -- 26周银行折现收益率
    w26_ce FLOAT,                    -- 26周票面利率
    w52_bd FLOAT,                    -- 52周银行折现收益率
    w52_ce FLOAT                     -- 52周票面利率
);

-- 表注释
COMMENT ON TABLE us_tbr IS '美国国库券利率';

-- 列注释
COMMENT ON COLUMN us_tbr.date IS '日期';
COMMENT ON COLUMN us_tbr.w4_bd IS '4周银行折现收益率';
COMMENT ON COLUMN us_tbr.w4_ce IS '4周票面利率';
COMMENT ON COLUMN us_tbr.w8_bd IS '8周银行折现收益率';
COMMENT ON COLUMN us_tbr.w8_ce IS '8周票面利率';
COMMENT ON COLUMN us_tbr.w13_bd IS '13周银行折现收益率';
COMMENT ON COLUMN us_tbr.w13_ce IS '13周票面利率';
COMMENT ON COLUMN us_tbr.w17_bd IS '17周银行折现收益率（数据从20221019开始）';
COMMENT ON COLUMN us_tbr.w17_ce IS '17周票面利率（数据从20221019开始）';
COMMENT ON COLUMN us_tbr.w26_bd IS '26周银行折现收益率';
COMMENT ON COLUMN us_tbr.w26_ce IS '26周票面利率';
COMMENT ON COLUMN us_tbr.w52_bd IS '52周银行折现收益率';
COMMENT ON COLUMN us_tbr.w52_ce IS '52周票面利率';

-- 添加索引
CREATE INDEX idx_us_tbr_date ON us_tbr(date);


-- 名称	类型	默认显示	描述
-- date	str	Y	日期
-- w4_bd	float	Y	4周银行折现收益率
-- w4_ce	float	Y	4周票面利率
-- w8_bd	float	Y	8周银行折现收益率
-- w8_ce	float	Y	8周票面利率
-- w13_bd	float	Y	13周银行折现收益率
-- w13_ce	float	Y	13周票面利率
-- w17_bd	float	Y	17周银行折现收益率（数据从20221019开始）
-- w17_ce	float	Y	17周票面利率（数据从20221019开始）
-- w26_bd	float	Y	26周银行折现收益率
-- w26_ce	float	Y	26周票面利率
-- w52_bd	float	Y	52周银行折现收益率
-- w52_ce	float	Y	52周票面利率