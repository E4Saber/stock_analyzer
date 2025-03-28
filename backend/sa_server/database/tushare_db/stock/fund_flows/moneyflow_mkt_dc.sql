-- 股票数据 - 资金流向

-- 大宗交易市场资金流向（moneyflow_mkt_dc）
CREATE TABLE moneyflow_mkt_dc (
    trade_date DATE NOT NULL PRIMARY KEY,     -- 交易日期
    close_sh FLOAT,                           -- 上证收盘价（点）
    pct_change_sh FLOAT,                      -- 上证涨跌幅(%)
    close_sz FLOAT,                           -- 深证收盘价（点）
    pct_change_sz FLOAT,                      -- 深证涨跌幅(%)
    net_amount FLOAT,                         -- 今日主力净流入 净额（元）
    net_amount_rate FLOAT,                    -- 今日主力净流入净占比%
    buy_elg_amount FLOAT,                     -- 今日超大单净流入 净额（元）
    buy_elg_amount_rate FLOAT,                -- 今日超大单净流入 净占比%
    buy_lg_amount FLOAT,                      -- 今日大单净流入 净额（元）
    buy_lg_amount_rate FLOAT,                 -- 今日大单净流入 净占比%
    buy_md_amount FLOAT,                      -- 今日中单净流入 净额（元）
    buy_md_amount_rate FLOAT,                 -- 今日中单净流入 净占比%
    buy_sm_amount FLOAT,                      -- 今日小单净流入 净额（元）
    buy_sm_amount_rate FLOAT                  -- 今日小单净流入 净占比%
);

-- 表注释
COMMENT ON TABLE moneyflow_mkt_dc IS '大宗交易市场资金流向';

-- 列注释
COMMENT ON COLUMN moneyflow_mkt_dc.trade_date IS '交易日期';
COMMENT ON COLUMN moneyflow_mkt_dc.close_sh IS '上证收盘价（点）';
COMMENT ON COLUMN moneyflow_mkt_dc.pct_change_sh IS '上证涨跌幅(%)';
COMMENT ON COLUMN moneyflow_mkt_dc.close_sz IS '深证收盘价（点）';
COMMENT ON COLUMN moneyflow_mkt_dc.pct_change_sz IS '深证涨跌幅(%)';
COMMENT ON COLUMN moneyflow_mkt_dc.net_amount IS '今日主力净流入 净额（元）';
COMMENT ON COLUMN moneyflow_mkt_dc.net_amount_rate IS '今日主力净流入净占比%';
COMMENT ON COLUMN moneyflow_mkt_dc.buy_elg_amount IS '今日超大单净流入 净额（元）';
COMMENT ON COLUMN moneyflow_mkt_dc.buy_elg_amount_rate IS '今日超大单净流入 净占比%';
COMMENT ON COLUMN moneyflow_mkt_dc.buy_lg_amount IS '今日大单净流入 净额（元）';
COMMENT ON COLUMN moneyflow_mkt_dc.buy_lg_amount_rate IS '今日大单净流入 净占比%';
COMMENT ON COLUMN moneyflow_mkt_dc.buy_md_amount IS '今日中单净流入 净额（元）';
COMMENT ON COLUMN moneyflow_mkt_dc.buy_md_amount_rate IS '今日中单净流入 净占比%';
COMMENT ON COLUMN moneyflow_mkt_dc.buy_sm_amount IS '今日小单净流入 净额（元）';
COMMENT ON COLUMN moneyflow_mkt_dc.buy_sm_amount_rate IS '今日小单净流入 净占比%';

-- 添加索引
CREATE INDEX idx_moneyflow_mkt_dc_pct_change_sh ON moneyflow_mkt_dc(pct_change_sh);
CREATE INDEX idx_moneyflow_mkt_dc_pct_change_sz ON moneyflow_mkt_dc(pct_change_sz);
CREATE INDEX idx_moneyflow_mkt_dc_net_amount ON moneyflow_mkt_dc(net_amount);