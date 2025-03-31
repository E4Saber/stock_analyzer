-- Shibor数据 - 上海银行间同业拆放利率

-- Shibor利率表（shibor）
CREATE TABLE shibor (
    date DATE PRIMARY KEY,     -- 日期
    on_rate FLOAT,             -- 隔夜利率
    w1_rate FLOAT,             -- 1周利率
    w2_rate FLOAT,             -- 2周利率
    m1_rate FLOAT,             -- 1个月利率
    m3_rate FLOAT,             -- 3个月利率
    m6_rate FLOAT,             -- 6个月利率
    m9_rate FLOAT,             -- 9个月利率
    y1_rate FLOAT              -- 1年利率
);

-- 表注释
COMMENT ON TABLE shibor IS '上海银行间同业拆放利率';

-- 列注释
COMMENT ON COLUMN shibor.date IS '日期';
COMMENT ON COLUMN shibor.on_rate IS '隔夜利率';
COMMENT ON COLUMN shibor.w1_rate IS '1周利率';
COMMENT ON COLUMN shibor.w2_rate IS '2周利率';
COMMENT ON COLUMN shibor.m1_rate IS '1个月利率';
COMMENT ON COLUMN shibor.m3_rate IS '3个月利率';
COMMENT ON COLUMN shibor.m6_rate IS '6个月利率';
COMMENT ON COLUMN shibor.m9_rate IS '9个月利率';
COMMENT ON COLUMN shibor.y1_rate IS '1年利率';

-- 添加索引
CREATE INDEX idx_shibor_date ON shibor(date);


-- 名称	类型	默认显示	描述
-- date	str	Y	日期
-- on	float	Y	隔夜
-- 1w	float	Y	1周
-- 2w	float	Y	2周
-- 1m	float	Y	1个月
-- 3m	float	Y	3个月
-- 6m	float	Y	6个月
-- 9m	float	Y	9个月
-- 1y	float	Y	1年