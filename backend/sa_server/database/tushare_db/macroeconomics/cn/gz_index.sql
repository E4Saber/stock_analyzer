-- 贵州小额贷款市场利率指数数据表

-- 贵州小额贷款市场利率指数（gz_index）
CREATE TABLE gz_index (
    date DATE PRIMARY KEY,           -- 日期
    d10_rate FLOAT,                  -- 小额贷市场平均利率（十天）（单位：%）
    m1_rate FLOAT,                   -- 小额贷市场平均利率（一月期）
    m3_rate FLOAT,                   -- 小额贷市场平均利率（三月期）
    m6_rate FLOAT,                   -- 小额贷市场平均利率（六月期）
    m12_rate FLOAT,                  -- 小额贷市场平均利率（一年期）
    long_rate FLOAT                  -- 小额贷市场平均利率（长期）
);

-- 表注释
COMMENT ON TABLE gz_index IS '贵州小额贷款市场利率指数';

-- 列注释
COMMENT ON COLUMN gz_index.date IS '日期';
COMMENT ON COLUMN gz_index.d10_rate IS '小额贷市场平均利率（十天）（单位：%）';
COMMENT ON COLUMN gz_index.m1_rate IS '小额贷市场平均利率（一月期）';
COMMENT ON COLUMN gz_index.m3_rate IS '小额贷市场平均利率（三月期）';
COMMENT ON COLUMN gz_index.m6_rate IS '小额贷市场平均利率（六月期）';
COMMENT ON COLUMN gz_index.m12_rate IS '小额贷市场平均利率（一年期）';
COMMENT ON COLUMN gz_index.long_rate IS '小额贷市场平均利率（长期）';

-- 添加索引
CREATE INDEX idx_gz_index_date ON gz_index(date);


-- 名称	类型	默认显示	描述
-- date	str	Y	日期
-- d10_rate	float	Y	小额贷市场平均利率（十天） （单位：%，下同）
-- m1_rate	float	Y	小额贷市场平均利率（一月期）
-- m3_rate	float	Y	小额贷市场平均利率（三月期）
-- m6_rate	float	Y	小额贷市场平均利率（六月期）
-- m12_rate	float	Y	小额贷市场平均利率（一年期）
-- long_rate	float	Y	小额贷市场平均利率（长期）