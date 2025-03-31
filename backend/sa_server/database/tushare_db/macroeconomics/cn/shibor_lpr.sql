-- SHIBOR LPR数据表 (贷款基础利率)

-- SHIBOR LPR（shibor_lpr）
CREATE TABLE shibor_lpr (
    date DATE PRIMARY KEY,    -- 日期
    y1 FLOAT,                 -- 1年贷款利率
    y5 FLOAT                  -- 5年贷款利率
);

-- 表注释
COMMENT ON TABLE shibor_lpr IS 'SHIBOR贷款基础利率';

-- 列注释
COMMENT ON COLUMN shibor_lpr.date IS '日期';
COMMENT ON COLUMN shibor_lpr.y1 IS '1年贷款利率';
COMMENT ON COLUMN shibor_lpr.y5 IS '5年贷款利率';

-- 添加索引
CREATE INDEX idx_shibor_lpr_date ON shibor_lpr(date);


-- 名称	类型	默认显示	描述
-- date	str	Y	日期
-- 1y	float	Y	1年贷款利率
-- 5y	float	Y	5年贷款利率