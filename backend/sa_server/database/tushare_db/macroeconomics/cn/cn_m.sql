-- 中国货币供应量数据表

-- 月度货币供应量数据表（cn_m）
CREATE TABLE cn_m (
    month VARCHAR(20) PRIMARY KEY,  -- 月份，格式YYYYMM
    m0 FLOAT,                       -- M0货币供应量（亿元）
    m0_yoy FLOAT,                   -- M0同比增长率（%）
    m0_mom FLOAT,                   -- M0环比增长率（%）
    m1 FLOAT,                       -- M1货币供应量（亿元）
    m1_yoy FLOAT,                   -- M1同比增长率（%）
    m1_mom FLOAT,                   -- M1环比增长率（%）
    m2 FLOAT,                       -- M2货币供应量（亿元）
    m2_yoy FLOAT,                   -- M2同比增长率（%）
    m2_mom FLOAT                    -- M2环比增长率（%）
);

-- 表注释
COMMENT ON TABLE cn_m IS '中国月度货币供应量数据';

-- 列注释
COMMENT ON COLUMN cn_m.month IS '月份，格式YYYYMM';
COMMENT ON COLUMN cn_m.m0 IS 'M0货币供应量（亿元）';
COMMENT ON COLUMN cn_m.m0_yoy IS 'M0同比增长率（%）';
COMMENT ON COLUMN cn_m.m0_mom IS 'M0环比增长率（%）';
COMMENT ON COLUMN cn_m.m1 IS 'M1货币供应量（亿元）';
COMMENT ON COLUMN cn_m.m1_yoy IS 'M1同比增长率（%）';
COMMENT ON COLUMN cn_m.m1_mom IS 'M1环比增长率（%）';
COMMENT ON COLUMN cn_m.m2 IS 'M2货币供应量（亿元）';
COMMENT ON COLUMN cn_m.m2_yoy IS 'M2同比增长率（%）';
COMMENT ON COLUMN cn_m.m2_mom IS 'M2环比增长率（%）';

-- 添加索引
CREATE INDEX idx_cn_m_month ON cn_m(month);

-- 字段说明
-- 名称    类型   默认显示  描述
-- month   str    Y        月份YYYYMM
-- m0      float  Y        M0（亿元）
-- m0_yoy  float  Y        M0同比（%）
-- m0_mom  float  Y        M0环比（%）
-- m1      float  Y        M1（亿元）
-- m1_yoy  float  Y        M1同比（%）
-- m1_mom  float  Y        M1环比（%）
-- m2      float  Y        M2（亿元）
-- m2_yoy  float  Y        M2同比（%）
-- m2_mom  float  Y        M2环比（%）