-- 美国国债收益率曲线数据表

-- 美国国债收益率曲线（us_tycr）
CREATE TABLE us_tycr (
    date DATE PRIMARY KEY,           -- 日期
    m1 FLOAT,                        -- 1月期
    m2 FLOAT,                        -- 2月期
    m3 FLOAT,                        -- 3月期
    m4 FLOAT,                        -- 4月期（数据从20221019开始）
    m6 FLOAT,                        -- 6月期
    y1 FLOAT,                        -- 1年期
    y2 FLOAT,                        -- 2年期
    y3 FLOAT,                        -- 3年期
    y5 FLOAT,                        -- 5年期
    y7 FLOAT,                        -- 7年期
    y10 FLOAT,                       -- 10年期
    y20 FLOAT,                       -- 20年期
    y30 FLOAT                        -- 30年期
);

-- 表注释
COMMENT ON TABLE us_tycr IS '美国国债收益率曲线';

-- 列注释
COMMENT ON COLUMN us_tycr.date IS '日期';
COMMENT ON COLUMN us_tycr.m1 IS '1月期';
COMMENT ON COLUMN us_tycr.m2 IS '2月期';
COMMENT ON COLUMN us_tycr.m3 IS '3月期';
COMMENT ON COLUMN us_tycr.m4 IS '4月期（数据从20221019开始）';
COMMENT ON COLUMN us_tycr.m6 IS '6月期';
COMMENT ON COLUMN us_tycr.y1 IS '1年期';
COMMENT ON COLUMN us_tycr.y2 IS '2年期';
COMMENT ON COLUMN us_tycr.y3 IS '3年期';
COMMENT ON COLUMN us_tycr.y5 IS '5年期';
COMMENT ON COLUMN us_tycr.y7 IS '7年期';
COMMENT ON COLUMN us_tycr.y10 IS '10年期';
COMMENT ON COLUMN us_tycr.y20 IS '20年期';
COMMENT ON COLUMN us_tycr.y30 IS '30年期';

-- 添加索引
CREATE INDEX idx_us_tycr_date ON us_tycr(date);


-- 名称	类型	默认显示	描述
-- date	str	Y	日期
-- m1	float	Y	1月期
-- m2	float	Y	2月期
-- m3	float	Y	3月期
-- m4	float	Y	4月期（数据从20221019开始）
-- m6	float	Y	6月期
-- y1	float	Y	1年期
-- y2	float	Y	2年期
-- y3	float	Y	3年期
-- y5	float	Y	5年期
-- y7	float	Y	7年期
-- y10	float	Y	10年期
-- y20	float	Y	20年期
-- y30	float	Y	30年期