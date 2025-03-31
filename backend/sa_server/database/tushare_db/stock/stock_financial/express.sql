-- 股票数据 - 业绩快报数据

-- 业绩快报表（express）
CREATE TABLE express (
    -- Primary key and identification fields
    id SERIAL PRIMARY KEY,
    ts_code VARCHAR(10) NOT NULL,
    ann_date DATE,
    end_date DATE,
    
    -- 业绩数据
    revenue NUMERIC(20,4),
    operate_profit NUMERIC(20,4),
    total_profit NUMERIC(20,4),
    n_income NUMERIC(20,4),
    total_assets NUMERIC(20,4),
    total_hldr_eqy_exc_min_int NUMERIC(20,4),
    diluted_eps NUMERIC(20,4),
    diluted_roe NUMERIC(20,4),
    yoy_net_profit NUMERIC(20,4),
    bps NUMERIC(20,4),
    
    -- 同比增长率
    yoy_sales NUMERIC(20,4),
    yoy_op NUMERIC(20,4),
    yoy_tp NUMERIC(20,4),
    yoy_dedu_np NUMERIC(20,4),
    yoy_eps NUMERIC(20,4),
    yoy_roe NUMERIC(20,4),
    growth_assets NUMERIC(20,4),
    yoy_equity NUMERIC(20,4),
    growth_bps NUMERIC(20,4),
    
    -- 去年同期数据
    or_last_year NUMERIC(20,4),
    op_last_year NUMERIC(20,4),
    tp_last_year NUMERIC(20,4),
    np_last_year NUMERIC(20,4),
    eps_last_year NUMERIC(20,4),
    
    -- 期初数据
    open_net_assets NUMERIC(20,4),
    open_bps NUMERIC(20,4),
    
    -- 其他信息
    perf_summary TEXT,
    is_audit INTEGER,
    remark TEXT
);

-- Create indexes for frequently queried fields
CREATE INDEX idx_express_ts_code ON express(ts_code);
CREATE INDEX idx_express_ann_date ON express(ann_date);
CREATE INDEX idx_express_end_date ON express(end_date);

-- Add unique constraint for upsert operations
ALTER TABLE express ADD CONSTRAINT express_ts_code_end_date_key 
UNIQUE (ts_code, end_date);

-- Add table comment
COMMENT ON TABLE express IS '业绩快报';

-- Add column comments
COMMENT ON COLUMN express.ts_code IS 'TS股票代码';
COMMENT ON COLUMN express.ann_date IS '公告日期';
COMMENT ON COLUMN express.end_date IS '报告期';
COMMENT ON COLUMN express.revenue IS '营业收入(元)';
COMMENT ON COLUMN express.operate_profit IS '营业利润(元)';
COMMENT ON COLUMN express.total_profit IS '利润总额(元)';
COMMENT ON COLUMN express.n_income IS '净利润(元)';
COMMENT ON COLUMN express.total_assets IS '总资产(元)';
COMMENT ON COLUMN express.total_hldr_eqy_exc_min_int IS '股东权益合计(不含少数股东权益)(元)';
COMMENT ON COLUMN express.diluted_eps IS '每股收益(摊薄)(元)';
COMMENT ON COLUMN express.diluted_roe IS '净资产收益率(摊薄)(%)';
COMMENT ON COLUMN express.yoy_net_profit IS '去年同期修正后净利润';
COMMENT ON COLUMN express.bps IS '每股净资产';
COMMENT ON COLUMN express.yoy_sales IS '同比增长率:营业收入';
COMMENT ON COLUMN express.yoy_op IS '同比增长率:营业利润';
COMMENT ON COLUMN express.yoy_tp IS '同比增长率:利润总额';
COMMENT ON COLUMN express.yoy_dedu_np IS '同比增长率:归属母公司股东的净利润';
COMMENT ON COLUMN express.yoy_eps IS '同比增长率:基本每股收益';
COMMENT ON COLUMN express.yoy_roe IS '同比增减:加权平均净资产收益率';
COMMENT ON COLUMN express.growth_assets IS '比年初增长率:总资产';
COMMENT ON COLUMN express.yoy_equity IS '比年初增长率:归属母公司的股东权益';
COMMENT ON COLUMN express.growth_bps IS '比年初增长率:归属于母公司股东的每股净资产';
COMMENT ON COLUMN express.or_last_year IS '去年同期营业收入';
COMMENT ON COLUMN express.op_last_year IS '去年同期营业利润';
COMMENT ON COLUMN express.tp_last_year IS '去年同期利润总额';
COMMENT ON COLUMN express.np_last_year IS '去年同期净利润';
COMMENT ON COLUMN express.eps_last_year IS '去年同期每股收益';
COMMENT ON COLUMN express.open_net_assets IS '期初净资产';
COMMENT ON COLUMN express.open_bps IS '期初每股净资产';
COMMENT ON COLUMN express.perf_summary IS '业绩简要说明';
COMMENT ON COLUMN express.is_audit IS '是否审计： 1是 0否';
COMMENT ON COLUMN express.remark IS '备注';


-- 名称	类型	描述
-- ts_code	str	TS股票代码
-- ann_date	str	公告日期
-- end_date	str	报告期
-- revenue	float	营业收入(元)
-- operate_profit	float	营业利润(元)
-- total_profit	float	利润总额(元)
-- n_income	float	净利润(元)
-- total_assets	float	总资产(元)
-- total_hldr_eqy_exc_min_int	float	股东权益合计(不含少数股东权益)(元)
-- diluted_eps	float	每股收益(摊薄)(元)
-- diluted_roe	float	净资产收益率(摊薄)(%)
-- yoy_net_profit	float	去年同期修正后净利润
-- bps	float	每股净资产
-- yoy_sales	float	同比增长率:营业收入
-- yoy_op	float	同比增长率:营业利润
-- yoy_tp	float	同比增长率:利润总额
-- yoy_dedu_np	float	同比增长率:归属母公司股东的净利润
-- yoy_eps	float	同比增长率:基本每股收益
-- yoy_roe	float	同比增减:加权平均净资产收益率
-- growth_assets	float	比年初增长率:总资产
-- yoy_equity	float	比年初增长率:归属母公司的股东权益
-- growth_bps	float	比年初增长率:归属于母公司股东的每股净资产
-- or_last_year	float	去年同期营业收入
-- op_last_year	float	去年同期营业利润
-- tp_last_year	float	去年同期利润总额
-- np_last_year	float	去年同期净利润
-- eps_last_year	float	去年同期每股收益
-- open_net_assets	float	期初净资产
-- open_bps	float	期初每股净资产
-- perf_summary	str	业绩简要说明
-- is_audit	int	是否审计： 1是 0否
-- remark	str	备注