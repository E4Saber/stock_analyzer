-- 股票数据 - 资金流向数据

-- 个股资金流向（moneyflow）
CREATE TABLE moneyflow (
    ts_code VARCHAR(20) NOT NULL,             -- TS代码
    trade_date DATE NOT NULL,                 -- 交易日期
    buy_sm_vol INT,                           -- 小单买入量（手）
    buy_sm_amount FLOAT,                      -- 小单买入金额（万元）
    sell_sm_vol INT,                          -- 小单卖出量（手）
    sell_sm_amount FLOAT,                     -- 小单卖出金额（万元）
    buy_md_vol INT,                           -- 中单买入量（手）
    buy_md_amount FLOAT,                      -- 中单买入金额（万元）
    sell_md_vol INT,                          -- 中单卖出量（手）
    sell_md_amount FLOAT,                     -- 中单卖出金额（万元）
    buy_lg_vol INT,                           -- 大单买入量（手）
    buy_lg_amount FLOAT,                      -- 大单买入金额（万元）
    sell_lg_vol INT,                          -- 大单卖出量（手）
    sell_lg_amount FLOAT,                     -- 大单卖出金额（万元）
    buy_elg_vol INT,                          -- 特大单买入量（手）
    buy_elg_amount FLOAT,                     -- 特大单买入金额（万元）
    sell_elg_vol INT,                         -- 特大单卖出量（手）
    sell_elg_amount FLOAT,                    -- 特大单卖出金额（万元）
    net_mf_vol INT,                           -- 净流入量（手）
    net_mf_amount FLOAT,                      -- 净流入额（万元）
    PRIMARY KEY (ts_code, trade_date)         -- 复合主键
);

-- 表注释
COMMENT ON TABLE moneyflow IS '股票资金流向';

-- 列注释
COMMENT ON COLUMN moneyflow.ts_code IS 'TS代码';
COMMENT ON COLUMN moneyflow.trade_date IS '交易日期';
COMMENT ON COLUMN moneyflow.buy_sm_vol IS '小单买入量（手）';
COMMENT ON COLUMN moneyflow.buy_sm_amount IS '小单买入金额（万元）';
COMMENT ON COLUMN moneyflow.sell_sm_vol IS '小单卖出量（手）';
COMMENT ON COLUMN moneyflow.sell_sm_amount IS '小单卖出金额（万元）';
COMMENT ON COLUMN moneyflow.buy_md_vol IS '中单买入量（手）';
COMMENT ON COLUMN moneyflow.buy_md_amount IS '中单买入金额（万元）';
COMMENT ON COLUMN moneyflow.sell_md_vol IS '中单卖出量（手）';
COMMENT ON COLUMN moneyflow.sell_md_amount IS '中单卖出金额（万元）';
COMMENT ON COLUMN moneyflow.buy_lg_vol IS '大单买入量（手）';
COMMENT ON COLUMN moneyflow.buy_lg_amount IS '大单买入金额（万元）';
COMMENT ON COLUMN moneyflow.sell_lg_vol IS '大单卖出量（手）';
COMMENT ON COLUMN moneyflow.sell_lg_amount IS '大单卖出金额（万元）';
COMMENT ON COLUMN moneyflow.buy_elg_vol IS '特大单买入量（手）';
COMMENT ON COLUMN moneyflow.buy_elg_amount IS '特大单买入金额（万元）';
COMMENT ON COLUMN moneyflow.sell_elg_vol IS '特大单卖出量（手）';
COMMENT ON COLUMN moneyflow.sell_elg_amount IS '特大单卖出金额（万元）';
COMMENT ON COLUMN moneyflow.net_mf_vol IS '净流入量（手）';
COMMENT ON COLUMN moneyflow.net_mf_amount IS '净流入额（万元）';

-- 添加索引
CREATE INDEX idx_moneyflow_ts_code ON moneyflow(ts_code);
CREATE INDEX idx_moneyflow_trade_date ON moneyflow(trade_date);


-- 名称	类型	默认显示	描述
-- ts_code	str	Y	TS代码
-- trade_date	str	Y	交易日期
-- buy_sm_vol	int	Y	小单买入量（手）
-- buy_sm_amount	float	Y	小单买入金额（万元）
-- sell_sm_vol	int	Y	小单卖出量（手）
-- sell_sm_amount	float	Y	小单卖出金额（万元）
-- buy_md_vol	int	Y	中单买入量（手）
-- buy_md_amount	float	Y	中单买入金额（万元）
-- sell_md_vol	int	Y	中单卖出量（手）
-- sell_md_amount	float	Y	中单卖出金额（万元）
-- buy_lg_vol	int	Y	大单买入量（手）
-- buy_lg_amount	float	Y	大单买入金额（万元）
-- sell_lg_vol	int	Y	大单卖出量（手）
-- sell_lg_amount	float	Y	大单卖出金额（万元）
-- buy_elg_vol	int	Y	特大单买入量（手）
-- buy_elg_amount	float	Y	特大单买入金额（万元）
-- sell_elg_vol	int	Y	特大单卖出量（手）
-- sell_elg_amount	float	Y	特大单卖出金额（万元）
-- net_mf_vol	int	Y	净流入量（手）
-- net_mf_amount	float	Y	净流入额（万元）

-- 各类别统计规则如下：
-- 小单：5万以下 中单：5万～20万 大单：20万～100万 特大单：成交额>=100万 ，数据基于主动买卖单统计