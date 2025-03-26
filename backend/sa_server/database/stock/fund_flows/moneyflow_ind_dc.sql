-- 股票数据 - 资金流向

-- 大宗交易板块资金流向（moneyflow_ind_dc）
CREATE TABLE moneyflow_ind_dc (
    ts_code VARCHAR(20) NOT NULL,             -- DC板块代码
    trade_date DATE NOT NULL,                 -- 交易日期
    content_type VARCHAR(20) NOT NULL,        -- 数据类型（行业、概念、地域）
    name VARCHAR(50) NOT NULL,                -- 板块名称
    pct_change FLOAT,                         -- 板块涨跌幅（%）
    close FLOAT,                              -- 板块最新指数
    net_amount FLOAT,                         -- 今日主力净流入 净额（元）
    net_amount_rate FLOAT,                    -- 今日主力净流入净占比%
    buy_elg_amount FLOAT,                     -- 今日超大单净流入 净额（元）
    buy_elg_amount_rate FLOAT,                -- 今日超大单净流入 净占比%
    buy_lg_amount FLOAT,                      -- 今日大单净流入 净额（元）
    buy_lg_amount_rate FLOAT,                 -- 今日大单净流入 净占比%
    buy_md_amount FLOAT,                      -- 今日中单净流入 净额（元）
    buy_md_amount_rate FLOAT,                 -- 今日中单净流入 净占比%
    buy_sm_amount FLOAT,                      -- 今日小单净流入 净额（元）
    buy_sm_amount_rate FLOAT,                 -- 今日小单净流入 净占比%
    buy_sm_amount_stock VARCHAR(50),          -- 今日主力净流入最大股
    rank INT,                                 -- 序号
    PRIMARY KEY (ts_code, trade_date, content_type) -- 复合主键
);

-- 表注释
COMMENT ON TABLE moneyflow_ind_dc IS '大宗交易板块资金流向';

-- 列注释
COMMENT ON COLUMN moneyflow_ind_dc.ts_code IS 'DC板块代码';
COMMENT ON COLUMN moneyflow_ind_dc.trade_date IS '交易日期';
COMMENT ON COLUMN moneyflow_ind_dc.content_type IS '数据类型（行业、概念、地域）';
COMMENT ON COLUMN moneyflow_ind_dc.name IS '板块名称';
COMMENT ON COLUMN moneyflow_ind_dc.pct_change IS '板块涨跌幅（%）';
COMMENT ON COLUMN moneyflow_ind_dc.close IS '板块最新指数';
COMMENT ON COLUMN moneyflow_ind_dc.net_amount IS '今日主力净流入 净额（元）';
COMMENT ON COLUMN moneyflow_ind_dc.net_amount_rate IS '今日主力净流入净占比%';
COMMENT ON COLUMN moneyflow_ind_dc.buy_elg_amount IS '今日超大单净流入 净额（元）';
COMMENT ON COLUMN moneyflow_ind_dc.buy_elg_amount_rate IS '今日超大单净流入 净占比%';
COMMENT ON COLUMN moneyflow_ind_dc.buy_lg_amount IS '今日大单净流入 净额（元）';
COMMENT ON COLUMN moneyflow_ind_dc.buy_lg_amount_rate IS '今日大单净流入 净占比%';
COMMENT ON COLUMN moneyflow_ind_dc.buy_md_amount IS '今日中单净流入 净额（元）';
COMMENT ON COLUMN moneyflow_ind_dc.buy_md_amount_rate IS '今日中单净流入 净占比%';
COMMENT ON COLUMN moneyflow_ind_dc.buy_sm_amount IS '今日小单净流入 净额（元）';
COMMENT ON COLUMN moneyflow_ind_dc.buy_sm_amount_rate IS '今日小单净流入 净占比%';
COMMENT ON COLUMN moneyflow_ind_dc.buy_sm_amount_stock IS '今日主力净流入最大股';
COMMENT ON COLUMN moneyflow_ind_dc.rank IS '序号';

-- 添加索引
CREATE INDEX idx_moneyflow_ind_dc_ts_code ON moneyflow_ind_dc(ts_code);
CREATE INDEX idx_moneyflow_ind_dc_trade_date ON moneyflow_ind_dc(trade_date);
CREATE INDEX idx_moneyflow_ind_dc_content_type ON moneyflow_ind_dc(content_type);
CREATE INDEX idx_moneyflow_ind_dc_net_amount ON moneyflow_ind_dc(net_amount);
CREATE INDEX idx_moneyflow_ind_dc_pct_change ON moneyflow_ind_dc(pct_change);