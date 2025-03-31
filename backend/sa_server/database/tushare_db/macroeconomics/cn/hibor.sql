-- HIBOR数据表 (香港银行同业拆借利率)

-- HIBOR（hibor）
CREATE TABLE hibor (
    date DATE PRIMARY KEY,    -- 日期
    on_rate FLOAT,            -- 隔夜
    w1_rate FLOAT,            -- 1周
    w2_rate FLOAT,            -- 2周
    m1_rate FLOAT,            -- 1个月
    m2_rate FLOAT,            -- 2个月
    m3_rate FLOAT,            -- 3个月
    m6_rate FLOAT,            -- 6个月
    m12_rate FLOAT            -- 12个月
);

-- 表注释
COMMENT ON TABLE hibor IS 'HIBOR利率数据(香港银行同业拆借利率)';

-- 列注释
COMMENT ON COLUMN hibor.date IS '日期';
COMMENT ON COLUMN hibor.on_rate IS '隔夜利率';
COMMENT ON COLUMN hibor.w1_rate IS '1周利率';
COMMENT ON COLUMN hibor.w2_rate IS '2周利率';
COMMENT ON COLUMN hibor.m1_rate IS '1个月利率';
COMMENT ON COLUMN hibor.m2_rate IS '2个月利率';
COMMENT ON COLUMN hibor.m3_rate IS '3个月利率';
COMMENT ON COLUMN hibor.m6_rate IS '6个月利率';
COMMENT ON COLUMN hibor.m12_rate IS '12个月利率';

-- 添加索引
CREATE INDEX idx_hibor_date ON hibor(date);


-- 名称	类型	默认显示	描述
-- date	str	Y	日期
-- on	float	Y	隔夜
-- 1w	float	Y	1周
-- 2w	float	Y	2周
-- 1m	float	Y	1个月
-- 2m	float	Y	2个月
-- 3m	float	Y	3个月
-- 6m	float	Y	6个月
-- 12m	float	Y	12个月