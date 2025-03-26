-- 股票数据 - 资金流向

-- 同花顺板块资金流向（moneyflow_cnt_ths）
CREATE TABLE moneyflow_cnt_ths (
    ts_code VARCHAR(20) NOT NULL,             -- 板块代码
    trade_date DATE NOT NULL,                 -- 交易日期
    name VARCHAR(50) NOT NULL,                -- 板块名称
    lead_stock VARCHAR(50),                   -- 领涨股票名称
    close_price FLOAT,                        -- 最新价
    pct_change FLOAT,                         -- 行业涨跌幅
    index_close FLOAT,                        -- 板块指数
    company_num INT,                          -- 公司数量
    pct_change_stock FLOAT,                   -- 领涨股涨跌幅
    net_buy_amount FLOAT,                     -- 流入资金(元)
    net_sell_amount FLOAT,                    -- 流出资金(元)
    net_amount FLOAT,                         -- 净额(元)
    PRIMARY KEY (ts_code, trade_date)         -- 复合主键
);

-- 表注释
COMMENT ON TABLE moneyflow_cnt_ths IS '同花顺板块资金流向';

-- 列注释
COMMENT ON COLUMN moneyflow_cnt_ths.ts_code IS '板块代码';
COMMENT ON COLUMN moneyflow_cnt_ths.trade_date IS '交易日期';
COMMENT ON COLUMN moneyflow_cnt_ths.name IS '板块名称';
COMMENT ON COLUMN moneyflow_cnt_ths.lead_stock IS '领涨股票名称';
COMMENT ON COLUMN moneyflow_cnt_ths.close_price IS '最新价';
COMMENT ON COLUMN moneyflow_cnt_ths.pct_change IS '行业涨跌幅';
COMMENT ON COLUMN moneyflow_cnt_ths.index_close IS '板块指数';
COMMENT ON COLUMN moneyflow_cnt_ths.company_num IS '公司数量';
COMMENT ON COLUMN moneyflow_cnt_ths.pct_change_stock IS '领涨股涨跌幅';
COMMENT ON COLUMN moneyflow_cnt_ths.net_buy_amount IS '流入资金(元)';
COMMENT ON COLUMN moneyflow_cnt_ths.net_sell_amount IS '流出资金(元)';
COMMENT ON COLUMN moneyflow_cnt_ths.net_amount IS '净额(元)';

-- 添加索引
CREATE INDEX idx_moneyflow_cnt_ths_ts_code ON moneyflow_cnt_ths(ts_code);
CREATE INDEX idx_moneyflow_cnt_ths_trade_date ON moneyflow_cnt_ths(trade_date);
CREATE INDEX idx_moneyflow_cnt_ths_net_amount ON moneyflow_cnt_ths(net_amount);