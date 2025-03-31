-- 温州民间融资指数数据表

-- 温州民间融资指数（wz_index）
CREATE TABLE wz_index (
    date DATE PRIMARY KEY,           -- 日期
    comp_rate FLOAT,                 -- 温州民间融资综合利率指数 (%)
    center_rate FLOAT,               -- 民间借贷服务中心利率
    micro_rate FLOAT,                -- 小额贷款公司放款利率
    cm_rate FLOAT,                   -- 民间资本管理公司融资价格
    sdb_rate FLOAT,                  -- 社会直接借贷利率
    om_rate FLOAT,                   -- 其他市场主体利率
    aa_rate FLOAT,                   -- 农村互助会互助金费率
    m1_rate FLOAT,                   -- 温州地区民间借贷分期限利率（一月期）
    m3_rate FLOAT,                   -- 温州地区民间借贷分期限利率（三月期）
    m6_rate FLOAT,                   -- 温州地区民间借贷分期限利率（六月期）
    m12_rate FLOAT,                  -- 温州地区民间借贷分期限利率（一年期）
    long_rate FLOAT                  -- 温州地区民间借贷分期限利率（长期）
);

-- 表注释
COMMENT ON TABLE wz_index IS '温州民间融资综合利率指数';

-- 列注释
COMMENT ON COLUMN wz_index.date IS '日期';
COMMENT ON COLUMN wz_index.comp_rate IS '温州民间融资综合利率指数 (%)';
COMMENT ON COLUMN wz_index.center_rate IS '民间借贷服务中心利率';
COMMENT ON COLUMN wz_index.micro_rate IS '小额贷款公司放款利率';
COMMENT ON COLUMN wz_index.cm_rate IS '民间资本管理公司融资价格';
COMMENT ON COLUMN wz_index.sdb_rate IS '社会直接借贷利率';
COMMENT ON COLUMN wz_index.om_rate IS '其他市场主体利率';
COMMENT ON COLUMN wz_index.aa_rate IS '农村互助会互助金费率';
COMMENT ON COLUMN wz_index.m1_rate IS '温州地区民间借贷分期限利率（一月期）';
COMMENT ON COLUMN wz_index.m3_rate IS '温州地区民间借贷分期限利率（三月期）';
COMMENT ON COLUMN wz_index.m6_rate IS '温州地区民间借贷分期限利率（六月期）';
COMMENT ON COLUMN wz_index.m12_rate IS '温州地区民间借贷分期限利率（一年期）';
COMMENT ON COLUMN wz_index.long_rate IS '温州地区民间借贷分期限利率（长期）';

-- 添加索引
CREATE INDEX idx_wz_index_date ON wz_index(date);


-- 名称	类型	默认显示	描述
-- date	str	Y	日期
-- comp_rate	float	Y	温州民间融资综合利率指数 (%，下同)
-- center_rate	float	Y	民间借贷服务中心利率
-- micro_rate	float	Y	小额贷款公司放款利率
-- cm_rate	float	Y	民间资本管理公司融资价格
-- sdb_rate	float	Y	社会直接借贷利率
-- om_rate	float	Y	其他市场主体利率
-- aa_rate	float	Y	农村互助会互助金费率
-- m1_rate	float	Y	温州地区民间借贷分期限利率（一月期）
-- m3_rate	float	Y	温州地区民间借贷分期限利率（三月期）
-- m6_rate	float	Y	温州地区民间借贷分期限利率（六月期）
-- m12_rate	float	Y	温州地区民间借贷分期限利率（一年期）
-- long_rate	float	Y	温州地区民间借贷分期限利率（长期）