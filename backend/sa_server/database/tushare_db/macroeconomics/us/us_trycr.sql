-- 美国国债实际收益率曲线数据表

-- 美国国债实际收益率曲线（us_trycr）
CREATE TABLE us_trycr (
    date DATE PRIMARY KEY,           -- 日期
    y5 FLOAT,                        -- 5年期
    y7 FLOAT,                        -- 7年期
    y10 FLOAT,                       -- 10年期
    y20 FLOAT,                       -- 20年期
    y30 FLOAT                        -- 30年期
);

-- 表注释
COMMENT ON TABLE us_trycr IS '美国国债实际收益率曲线';

-- 列注释
COMMENT ON COLUMN us_trycr.date IS '日期';
COMMENT ON COLUMN us_trycr.y5 IS '5年期';
COMMENT ON COLUMN us_trycr.y7 IS '7年期';
COMMENT ON COLUMN us_trycr.y10 IS '10年期';
COMMENT ON COLUMN us_trycr.y20 IS '20年期';
COMMENT ON COLUMN us_trycr.y30 IS '30年期';

-- 添加索引
CREATE INDEX idx_us_trycr_date ON us_trycr(date);


-- 名称	类型	默认显示	描述
-- date	str	Y	日期
-- y5	float	Y	5年期
-- y7	float	Y	7年期
-- y10	float	Y	10年期
-- y20	float	Y	20年期
-- y30	float	Y	30年期