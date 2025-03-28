-- 股票数据 - 资金流向

-- 同花顺行业资金流向（moneyflow_ind_ths）
CREATE TABLE moneyflow_ind_ths (
    ts_code VARCHAR(20) NOT NULL,             -- 板块代码
    trade_date DATE NOT NULL,                 -- 交易日期
    industry VARCHAR(50) NOT NULL,            -- 板块名称
    lead_stock VARCHAR(50),                   -- 领涨股票名称
    close FLOAT,                              -- 收盘指数
    pct_change FLOAT,                         -- 指数涨跌幅
    company_num INT,                          -- 公司数量
    pct_change_stock FLOAT,                   -- 领涨股涨跌幅
    close_price FLOAT,                        -- 领涨股最新价
    net_buy_amount FLOAT,                     -- 流入资金(亿元)
    net_sell_amount FLOAT,                    -- 流出资金(亿元)
    net_amount FLOAT,                         -- 净额(元)
    PRIMARY KEY (ts_code, trade_date)         -- 复合主键
);

-- 表注释
COMMENT ON TABLE moneyflow_ind_ths IS '同花顺行业资金流向';

-- 列注释
COMMENT ON COLUMN moneyflow_ind_ths.ts_code IS '板块代码';
COMMENT ON COLUMN moneyflow_ind_ths.trade_date IS '交易日期';
COMMENT ON COLUMN moneyflow_ind_ths.industry IS '板块名称';
COMMENT ON COLUMN moneyflow_ind_ths.lead_stock IS '领涨股票名称';
COMMENT ON COLUMN moneyflow_ind_ths.close IS '收盘指数';
COMMENT ON COLUMN moneyflow_ind_ths.pct_change IS '指数涨跌幅';
COMMENT ON COLUMN moneyflow_ind_ths.company_num IS '公司数量';
COMMENT ON COLUMN moneyflow_ind_ths.pct_change_stock IS '领涨股涨跌幅';
COMMENT ON COLUMN moneyflow_ind_ths.close_price IS '领涨股最新价';
COMMENT ON COLUMN moneyflow_ind_ths.net_buy_amount IS '流入资金(亿元)';
COMMENT ON COLUMN moneyflow_ind_ths.net_sell_amount IS '流出资金(亿元)';
COMMENT ON COLUMN moneyflow_ind_ths.net_amount IS '净额(元)';

-- 添加索引
CREATE INDEX idx_moneyflow_ind_ths_ts_code ON moneyflow_ind_ths(ts_code);
CREATE INDEX idx_moneyflow_ind_ths_trade_date ON moneyflow_ind_ths(trade_date);
CREATE INDEX idx_moneyflow_ind_ths_net_amount ON moneyflow_ind_ths(net_amount);
CREATE INDEX idx_moneyflow_ind_ths_pct_change ON moneyflow_ind_ths(pct_change);