-- 股票数据 - 资金流向

-- 大宗交易资金流向（moneyflow_dc）
CREATE TABLE moneyflow_dc (
    ts_code VARCHAR(20) NOT NULL,             -- 股票代码
    trade_date DATE NOT NULL,                 -- 交易日期
    name VARCHAR(50) NOT NULL,                -- 股票名称
    pct_change FLOAT,                         -- 涨跌幅
    close FLOAT,                              -- 最新价
    net_amount FLOAT,                         -- 今日主力净流入额（万元）
    net_amount_rate FLOAT,                    -- 今日主力净流入净占比（%）
    buy_elg_amount FLOAT,                     -- 今日超大单净流入额（万元）
    buy_elg_amount_rate FLOAT,                -- 今日超大单净流入占比（%）
    buy_lg_amount FLOAT,                      -- 今日大单净流入额（万元）
    buy_lg_amount_rate FLOAT,                 -- 今日大单净流入占比（%）
    buy_md_amount FLOAT,                      -- 今日中单净流入额（万元）
    buy_md_amount_rate FLOAT,                 -- 今日中单净流入占比（%）
    buy_sm_amount FLOAT,                      -- 今日小单净流入额（万元）
    buy_sm_amount_rate FLOAT,                 -- 今日小单净流入占比（%）
    PRIMARY KEY (ts_code, trade_date)         -- 复合主键
);

-- 表注释
COMMENT ON TABLE moneyflow_dc IS '大宗交易股票资金流向';

-- 列注释
COMMENT ON COLUMN moneyflow_dc.ts_code IS '股票代码';
COMMENT ON COLUMN moneyflow_dc.trade_date IS '交易日期';
COMMENT ON COLUMN moneyflow_dc.name IS '股票名称';
COMMENT ON COLUMN moneyflow_dc.pct_change IS '涨跌幅';
COMMENT ON COLUMN moneyflow_dc.close IS '最新价';
COMMENT ON COLUMN moneyflow_dc.net_amount IS '今日主力净流入额（万元）';
COMMENT ON COLUMN moneyflow_dc.net_amount_rate IS '今日主力净流入净占比（%）';
COMMENT ON COLUMN moneyflow_dc.buy_elg_amount IS '今日超大单净流入额（万元）';
COMMENT ON COLUMN moneyflow_dc.buy_elg_amount_rate IS '今日超大单净流入占比（%）';
COMMENT ON COLUMN moneyflow_dc.buy_lg_amount IS '今日大单净流入额（万元）';
COMMENT ON COLUMN moneyflow_dc.buy_lg_amount_rate IS '今日大单净流入占比（%）';
COMMENT ON COLUMN moneyflow_dc.buy_md_amount IS '今日中单净流入额（万元）';
COMMENT ON COLUMN moneyflow_dc.buy_md_amount_rate IS '今日中单净流入占比（%）';
COMMENT ON COLUMN moneyflow_dc.buy_sm_amount IS '今日小单净流入额（万元）';
COMMENT ON COLUMN moneyflow_dc.buy_sm_amount_rate IS '今日小单净流入占比（%）';

-- 添加索引
CREATE INDEX idx_moneyflow_dc_ts_code ON moneyflow_dc(ts_code);
CREATE INDEX idx_moneyflow_dc_trade_date ON moneyflow_dc(trade_date);
CREATE INDEX idx_moneyflow_dc_net_amount ON moneyflow_dc(net_amount);