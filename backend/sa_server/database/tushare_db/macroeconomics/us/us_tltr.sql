-- 美国长期国债利率数据表

-- 美国长期国债利率（us_tltr）
CREATE TABLE us_tltr (
    date DATE PRIMARY KEY,           -- 日期
    ltc FLOAT,                       -- 收益率 LT COMPOSITE (>10 Yrs)
    cmt FLOAT,                       -- 20年期CMT利率(TREASURY 20-Yr CMT)
    e_factor FLOAT                   -- 外推因子EXTRAPOLATION FACTOR
);

-- 表注释
COMMENT ON TABLE us_tltr IS '美国长期国债利率';

-- 列注释
COMMENT ON COLUMN us_tltr.date IS '日期';
COMMENT ON COLUMN us_tltr.ltc IS '收益率 LT COMPOSITE (>10 Yrs)';
COMMENT ON COLUMN us_tltr.cmt IS '20年期CMT利率(TREASURY 20-Yr CMT)';
COMMENT ON COLUMN us_tltr.e_factor IS '外推因子EXTRAPOLATION FACTOR';

-- 添加索引
CREATE INDEX idx_us_tltr_date ON us_tltr(date);


-- 名称	类型	默认显示	描述
-- date	str	Y	日期
-- ltc	float	Y	收益率 LT COMPOSITE (>10 Yrs)
-- cmt	float	Y	20年期CMT利率(TREASURY 20-Yr CMT)
-- e_factor	float	Y	外推因子EXTRAPOLATION FACTOR