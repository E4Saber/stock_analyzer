-- 美国国债实际长期利率数据表

-- 美国国债实际长期利率（us_trltr）
CREATE TABLE us_trltr (
    date DATE PRIMARY KEY,           -- 日期
    ltr_avg FLOAT                    -- 实际平均利率LT Real Average (10> Yrs)
);

-- 表注释
COMMENT ON TABLE us_trltr IS '美国国债实际长期利率';

-- 列注释
COMMENT ON COLUMN us_trltr.date IS '日期';
COMMENT ON COLUMN us_trltr.ltr_avg IS '实际平均利率LT Real Average (10> Yrs)';

-- 添加索引
CREATE INDEX idx_us_trltr_date ON us_trltr(date);


-- 名称	类型	默认显示	描述
-- date	str	Y	日期
-- ltr_avg	float	Y	实际平均利率LT Real Average (10> Yrs)