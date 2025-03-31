-- 中国PPI数据表

-- 月度PPI数据表（cn_ppi）
CREATE TABLE cn_ppi (
    month VARCHAR(20) PRIMARY KEY,         -- 月份，格式YYYYMM
    ppi_yoy FLOAT,                         -- PPI：全部工业品：当月同比
    ppi_mp_yoy FLOAT,                      -- PPI：生产资料：当月同比
    ppi_mp_qm_yoy FLOAT,                   -- PPI：生产资料：采掘业：当月同比
    ppi_mp_rm_yoy FLOAT,                   -- PPI：生产资料：原料业：当月同比
    ppi_mp_p_yoy FLOAT,                    -- PPI：生产资料：加工业：当月同比
    ppi_cg_yoy FLOAT,                      -- PPI：生活资料：当月同比
    ppi_cg_f_yoy FLOAT,                    -- PPI：生活资料：食品类：当月同比
    ppi_cg_c_yoy FLOAT,                    -- PPI：生活资料：衣着类：当月同比
    ppi_cg_adu_yoy FLOAT,                  -- PPI：生活资料：一般日用品类：当月同比
    ppi_cg_dcg_yoy FLOAT,                  -- PPI：生活资料：耐用消费品类：当月同比
    ppi_mom FLOAT,                         -- PPI：全部工业品：环比
    ppi_mp_mom FLOAT,                      -- PPI：生产资料：环比
    ppi_mp_qm_mom FLOAT,                   -- PPI：生产资料：采掘业：环比
    ppi_mp_rm_mom FLOAT,                   -- PPI：生产资料：原料业：环比
    ppi_mp_p_mom FLOAT,                    -- PPI：生产资料：加工业：环比
    ppi_cg_mom FLOAT,                      -- PPI：生活资料：环比
    ppi_cg_f_mom FLOAT,                    -- PPI：生活资料：食品类：环比
    ppi_cg_c_mom FLOAT,                    -- PPI：生活资料：衣着类：环比
    ppi_cg_adu_mom FLOAT,                  -- PPI：生活资料：一般日用品类：环比
    ppi_cg_dcg_mom FLOAT,                  -- PPI：生活资料：耐用消费品类：环比
    ppi_accu FLOAT,                        -- PPI：全部工业品：累计同比
    ppi_mp_accu FLOAT,                     -- PPI：生产资料：累计同比
    ppi_mp_qm_accu FLOAT,                  -- PPI：生产资料：采掘业：累计同比
    ppi_mp_rm_accu FLOAT,                  -- PPI：生产资料：原料业：累计同比
    ppi_mp_p_accu FLOAT,                   -- PPI：生产资料：加工业：累计同比
    ppi_cg_accu FLOAT,                     -- PPI：生活资料：累计同比
    ppi_cg_f_accu FLOAT,                   -- PPI：生活资料：食品类：累计同比
    ppi_cg_c_accu FLOAT,                   -- PPI：生活资料：衣着类：累计同比
    ppi_cg_adu_accu FLOAT,                 -- PPI：生活资料：一般日用品类：累计同比
    ppi_cg_dcg_accu FLOAT                  -- PPI：生活资料：耐用消费品类：累计同比
);

-- 表注释
COMMENT ON TABLE cn_ppi IS '中国月度PPI数据';

-- 列注释
COMMENT ON COLUMN cn_ppi.month IS '月份，格式YYYYMM';
COMMENT ON COLUMN cn_ppi.ppi_yoy IS 'PPI：全部工业品：当月同比';
COMMENT ON COLUMN cn_ppi.ppi_mp_yoy IS 'PPI：生产资料：当月同比';
COMMENT ON COLUMN cn_ppi.ppi_mp_qm_yoy IS 'PPI：生产资料：采掘业：当月同比';
COMMENT ON COLUMN cn_ppi.ppi_mp_rm_yoy IS 'PPI：生产资料：原料业：当月同比';
COMMENT ON COLUMN cn_ppi.ppi_mp_p_yoy IS 'PPI：生产资料：加工业：当月同比';
COMMENT ON COLUMN cn_ppi.ppi_cg_yoy IS 'PPI：生活资料：当月同比';
COMMENT ON COLUMN cn_ppi.ppi_cg_f_yoy IS 'PPI：生活资料：食品类：当月同比';
COMMENT ON COLUMN cn_ppi.ppi_cg_c_yoy IS 'PPI：生活资料：衣着类：当月同比';
COMMENT ON COLUMN cn_ppi.ppi_cg_adu_yoy IS 'PPI：生活资料：一般日用品类：当月同比';
COMMENT ON COLUMN cn_ppi.ppi_cg_dcg_yoy IS 'PPI：生活资料：耐用消费品类：当月同比';
COMMENT ON COLUMN cn_ppi.ppi_mom IS 'PPI：全部工业品：环比';
COMMENT ON COLUMN cn_ppi.ppi_mp_mom IS 'PPI：生产资料：环比';
COMMENT ON COLUMN cn_ppi.ppi_mp_qm_mom IS 'PPI：生产资料：采掘业：环比';
COMMENT ON COLUMN cn_ppi.ppi_mp_rm_mom IS 'PPI：生产资料：原料业：环比';
COMMENT ON COLUMN cn_ppi.ppi_mp_p_mom IS 'PPI：生产资料：加工业：环比';
COMMENT ON COLUMN cn_ppi.ppi_cg_mom IS 'PPI：生活资料：环比';
COMMENT ON COLUMN cn_ppi.ppi_cg_f_mom IS 'PPI：生活资料：食品类：环比';
COMMENT ON COLUMN cn_ppi.ppi_cg_c_mom IS 'PPI：生活资料：衣着类：环比';
COMMENT ON COLUMN cn_ppi.ppi_cg_adu_mom IS 'PPI：生活资料：一般日用品类：环比';
COMMENT ON COLUMN cn_ppi.ppi_cg_dcg_mom IS 'PPI：生活资料：耐用消费品类：环比';
COMMENT ON COLUMN cn_ppi.ppi_accu IS 'PPI：全部工业品：累计同比';
COMMENT ON COLUMN cn_ppi.ppi_mp_accu IS 'PPI：生产资料：累计同比';
COMMENT ON COLUMN cn_ppi.ppi_mp_qm_accu IS 'PPI：生产资料：采掘业：累计同比';
COMMENT ON COLUMN cn_ppi.ppi_mp_rm_accu IS 'PPI：生产资料：原料业：累计同比';
COMMENT ON COLUMN cn_ppi.ppi_mp_p_accu IS 'PPI：生产资料：加工业：累计同比';
COMMENT ON COLUMN cn_ppi.ppi_cg_accu IS 'PPI：生活资料：累计同比';
COMMENT ON COLUMN cn_ppi.ppi_cg_f_accu IS 'PPI：生活资料：食品类：累计同比';
COMMENT ON COLUMN cn_ppi.ppi_cg_c_accu IS 'PPI：生活资料：衣着类：累计同比';
COMMENT ON COLUMN cn_ppi.ppi_cg_adu_accu IS 'PPI：生活资料：一般日用品类：累计同比';
COMMENT ON COLUMN cn_ppi.ppi_cg_dcg_accu IS 'PPI：生活资料：耐用消费品类：累计同比';

-- 添加索引
CREATE INDEX idx_cn_ppi_month ON cn_ppi(month);

-- 字段说明
-- 名称             类型   默认显示  描述
-- month           str    Y        月份YYYYMM
-- ppi_yoy         float  Y        PPI：全部工业品：当月同比
-- ppi_mp_yoy      float  Y        PPI：生产资料：当月同比
-- ppi_mp_qm_yoy   float  Y        PPI：生产资料：采掘业：当月同比
-- ppi_mp_rm_yoy   float  Y        PPI：生产资料：原料业：当月同比
-- ppi_mp_p_yoy    float  Y        PPI：生产资料：加工业：当月同比
-- ppi_cg_yoy      float  Y        PPI：生活资料：当月同比
-- ppi_cg_f_yoy    float  Y        PPI：生活资料：食品类：当月同比
-- ppi_cg_c_yoy    float  Y        PPI：生活资料：衣着类：当月同比
-- ppi_cg_adu_yoy  float  Y        PPI：生活资料：一般日用品类：当月同比
-- ppi_cg_dcg_yoy  float  Y        PPI：生活资料：耐用消费品类：当月同比
-- ppi_mom         float  Y        PPI：全部工业品：环比
-- ppi_mp_mom      float  Y        PPI：生产资料：环比
-- ppi_mp_qm_mom   float  Y        PPI：生产资料：采掘业：环比
-- ppi_mp_rm_mom   float  Y        PPI：生产资料：原料业：环比
-- ppi_mp_p_mom    float  Y        PPI：生产资料：加工业：环比
-- ppi_cg_mom      float  Y        PPI：生活资料：环比
-- ppi_cg_f_mom    float  Y        PPI：生活资料：食品类：环比
-- ppi_cg_c_mom    float  Y        PPI：生活资料：衣着类：环比
-- ppi_cg_adu_mom  float  Y        PPI：生活资料：一般日用品类：环比
-- ppi_cg_dcg_mom  float  Y        PPI：生活资料：耐用消费品类：环比
-- ppi_accu        float  Y        PPI：全部工业品：累计同比
-- ppi_mp_accu     float  Y        PPI：生产资料：累计同比
-- ppi_mp_qm_accu  float  Y        PPI：生产资料：采掘业：累计同比
-- ppi_mp_rm_accu  float  Y        PPI：生产资料：原料业：累计同比
-- ppi_mp_p_accu   float  Y        PPI：生产资料：加工业：累计同比
-- ppi_cg_accu     float  Y        PPI：生活资料：累计同比
-- ppi_cg_f_accu   float  Y        PPI：生活资料：食品类：累计同比
-- ppi_cg_c_accu   float  Y        PPI：生活资料：衣着类：累计同比
-- ppi_cg_adu_accu float  Y        PPI：生活资料：一般日用品类：累计同比
-- ppi_cg_dcg_accu float  Y        PPI：生活资料：耐用消费品类：累计同比