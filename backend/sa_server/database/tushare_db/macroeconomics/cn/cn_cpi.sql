-- 中国CPI数据表

-- 月度CPI数据表（cn_cpi）
CREATE TABLE cn_cpi (
    month VARCHAR(20) PRIMARY KEY,  -- 月份，格式YYYYMM
    nt_val FLOAT,                   -- 全国当月值
    nt_yoy FLOAT,                   -- 全国同比（%）
    nt_mom FLOAT,                   -- 全国环比（%）
    nt_accu FLOAT,                  -- 全国累计值
    town_val FLOAT,                 -- 城市当月值
    town_yoy FLOAT,                 -- 城市同比（%）
    town_mom FLOAT,                 -- 城市环比（%）
    town_accu FLOAT,                -- 城市累计值
    cnt_val FLOAT,                  -- 农村当月值
    cnt_yoy FLOAT,                  -- 农村同比（%）
    cnt_mom FLOAT,                  -- 农村环比（%）
    cnt_accu FLOAT                  -- 农村累计值
);

-- 表注释
COMMENT ON TABLE cn_cpi IS '中国月度CPI数据';

-- 列注释
COMMENT ON COLUMN cn_cpi.month IS '月份，格式YYYYMM';
COMMENT ON COLUMN cn_cpi.nt_val IS '全国当月值';
COMMENT ON COLUMN cn_cpi.nt_yoy IS '全国同比（%）';
COMMENT ON COLUMN cn_cpi.nt_mom IS '全国环比（%）';
COMMENT ON COLUMN cn_cpi.nt_accu IS '全国累计值';
COMMENT ON COLUMN cn_cpi.town_val IS '城市当月值';
COMMENT ON COLUMN cn_cpi.town_yoy IS '城市同比（%）';
COMMENT ON COLUMN cn_cpi.town_mom IS '城市环比（%）';
COMMENT ON COLUMN cn_cpi.town_accu IS '城市累计值';
COMMENT ON COLUMN cn_cpi.cnt_val IS '农村当月值';
COMMENT ON COLUMN cn_cpi.cnt_yoy IS '农村同比（%）';
COMMENT ON COLUMN cn_cpi.cnt_mom IS '农村环比（%）';
COMMENT ON COLUMN cn_cpi.cnt_accu IS '农村累计值';

-- 添加索引
CREATE INDEX idx_cn_cpi_month ON cn_cpi(month);

-- 字段说明
-- 名称        类型    默认显示    描述
-- month       str     Y          月份YYYYMM
-- nt_val      float   Y          全国当月值
-- nt_yoy      float   Y          全国同比（%）
-- nt_mom      float   Y          全国环比（%）
-- nt_accu     float   Y          全国累计值
-- town_val    float   Y          城市当月值
-- town_yoy    float   Y          城市同比（%）
-- town_mom    float   Y          城市环比（%）
-- town_accu   float   Y          城市累计值
-- cnt_val     float   Y          农村当月值
-- cnt_yoy     float   Y          农村同比（%）
-- cnt_mom     float   Y          农村环比（%）
-- cnt_accu    float   Y          农村累计值