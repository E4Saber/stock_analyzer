-- 中国GDP数据表

-- 季度GDP数据表（cn_gdp）
CREATE TABLE cn_gdp (
    quarter VARCHAR(20) PRIMARY KEY,  -- 季度
    gdp FLOAT,                        -- GDP累计值（亿元）
    gdp_yoy FLOAT,                    -- 当季同比增速（%）
    pi FLOAT,                         -- 第一产业累计值（亿元）
    pi_yoy FLOAT,                     -- 第一产业同比增速（%）
    si FLOAT,                         -- 第二产业累计值（亿元）
    si_yoy FLOAT,                     -- 第二产业同比增速（%）
    ti FLOAT,                         -- 第三产业累计值（亿元）
    ti_yoy FLOAT                      -- 第三产业同比增速（%）
);

-- 表注释
COMMENT ON TABLE cn_gdp IS '中国季度GDP数据';

-- 列注释
COMMENT ON COLUMN cn_gdp.quarter IS '季度';
COMMENT ON COLUMN cn_gdp.gdp IS 'GDP累计值（亿元）';
COMMENT ON COLUMN cn_gdp.gdp_yoy IS '当季同比增速（%）';
COMMENT ON COLUMN cn_gdp.pi IS '第一产业累计值（亿元）';
COMMENT ON COLUMN cn_gdp.pi_yoy IS '第一产业同比增速（%）';
COMMENT ON COLUMN cn_gdp.si IS '第二产业累计值（亿元）';
COMMENT ON COLUMN cn_gdp.si_yoy IS '第二产业同比增速（%）';
COMMENT ON COLUMN cn_gdp.ti IS '第三产业累计值（亿元）';
COMMENT ON COLUMN cn_gdp.ti_yoy IS '第三产业同比增速（%）';

-- 添加索引
CREATE INDEX idx_cn_gdp_quarter ON cn_gdp(quarter);


-- 名称	类型	默认显示	描述
-- quarter	str	Y	季度
-- gdp	float	Y	GDP累计值（亿元）
-- gdp_yoy	float	Y	当季同比增速（%）
-- pi	float	Y	第一产业累计值（亿元）
-- pi_yoy	float	Y	第一产业同比增速（%）
-- si	float	Y	第二产业累计值（亿元）
-- si_yoy	float	Y	第二产业同比增速（%）
-- ti	float	Y	第三产业累计值（亿元）
-- ti_yoy	float	Y	第三产业同比增速（%）