-- 股票数据 - 资金流向

-- 同花顺资金流向（moneyflow_ths）
CREATE TABLE moneyflow_ths (
    ts_code VARCHAR(20) NOT NULL,             -- 股票代码
    trade_date DATE NOT NULL,                 -- 交易日期
    name VARCHAR(50) NOT NULL,                -- 股票名称
    pct_change FLOAT,                         -- 涨跌幅
    latest FLOAT,                             -- 最新价
    net_amount FLOAT,                         -- 资金净流入(万元)
    net_d5_amount FLOAT,                      -- 5日主力净额(万元)
    buy_lg_amount FLOAT,                      -- 今日大单净流入额(万元)
    buy_lg_amount_rate FLOAT,                 -- 今日大单净流入占比(%)
    buy_md_amount FLOAT,                      -- 今日中单净流入额(万元)
    buy_md_amount_rate FLOAT,                 -- 今日中单净流入占比(%)
    buy_sm_amount FLOAT,                      -- 今日小单净流入额(万元)
    buy_sm_amount_rate FLOAT,                 -- 今日小单净流入占比(%)
    PRIMARY KEY (ts_code, trade_date)         -- 复合主键
);

-- 表注释
COMMENT ON TABLE moneyflow_ths IS '同花顺股票资金流向';

-- 列注释
COMMENT ON COLUMN moneyflow_ths.ts_code IS '股票代码';
COMMENT ON COLUMN moneyflow_ths.trade_date IS '交易日期';
COMMENT ON COLUMN moneyflow_ths.name IS '股票名称';
COMMENT ON COLUMN moneyflow_ths.pct_change IS '涨跌幅';
COMMENT ON COLUMN moneyflow_ths.latest IS '最新价';
COMMENT ON COLUMN moneyflow_ths.net_amount IS '资金净流入(万元)';
COMMENT ON COLUMN moneyflow_ths.net_d5_amount IS '5日主力净额(万元)';
COMMENT ON COLUMN moneyflow_ths.buy_lg_amount IS '今日大单净流入额(万元)';
COMMENT ON COLUMN moneyflow_ths.buy_lg_amount_rate IS '今日大单净流入占比(%)';
COMMENT ON COLUMN moneyflow_ths.buy_md_amount IS '今日中单净流入额(万元)';
COMMENT ON COLUMN moneyflow_ths.buy_md_amount_rate IS '今日中单净流入占比(%)';
COMMENT ON COLUMN moneyflow_ths.buy_sm_amount IS '今日小单净流入额(万元)';
COMMENT ON COLUMN moneyflow_ths.buy_sm_amount_rate IS '今日小单净流入占比(%)';

-- 添加索引
CREATE INDEX idx_moneyflow_ths_ts_code ON moneyflow_ths(ts_code);
CREATE INDEX idx_moneyflow_ths_trade_date ON moneyflow_ths(trade_date);
CREATE INDEX idx_moneyflow_ths_net_amount ON moneyflow_ths(net_amount);