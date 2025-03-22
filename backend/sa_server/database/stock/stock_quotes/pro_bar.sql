-- 股票数据 - 行情数据

-- A股复权行情（pro_bar）
CREATE TABLE pro_bar (
    id SERIAL PRIMARY KEY,                -- 自增主键
    ts_code VARCHAR(20) NOT NULL,         -- 证券代码
    start_date VARCHAR(8),                -- 开始日期 (格式：YYYYMMDD)
    end_date VARCHAR(8),                  -- 结束日期 (格式：YYYYMMDD)
    asset VARCHAR(2) NOT NULL,            -- 资产类别：E股票 I沪深指数 C数字货币 FT期货 FD基金 O期权，默认E
    adj VARCHAR(4),                       -- 复权类型(只针对股票)：None未复权 qfq前复权 hfq后复权 , 默认None
    freq VARCHAR(5) NOT NULL,             -- 数据频度 ：1MIN表示1分钟（1/5/15/30/60分钟） D日线 ，默认D
    ma VARCHAR(100),                      -- 均线，支持任意周期的均价和均量，输入任意合理int数值
    request_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, -- 请求时间
    CONSTRAINT ck_pro_bar_asset CHECK (asset IN ('E', 'I', 'C', 'FT', 'FD', 'O')),
    CONSTRAINT ck_pro_bar_adj CHECK (adj IS NULL OR adj IN ('None', 'qfq', 'hfq')),
    CONSTRAINT ck_pro_bar_freq CHECK (freq IN ('1MIN', '5MIN', '15MIN', '30MIN', '60MIN', 'D', 'W', 'M'))
);

-- 表注释
COMMENT ON TABLE pro_bar IS '通用K线参数';

-- 列注释
COMMENT ON COLUMN pro_bar.id IS '自增主键';
COMMENT ON COLUMN pro_bar.ts_code IS '证券代码';
COMMENT ON COLUMN pro_bar.start_date IS '开始日期 (格式：YYYYMMDD)';
COMMENT ON COLUMN pro_bar.end_date IS '结束日期 (格式：YYYYMMDD)';
COMMENT ON COLUMN pro_bar.asset IS '资产类别：E股票 I沪深指数 C数字货币 FT期货 FD基金 O期权，默认E';
COMMENT ON COLUMN pro_bar.adj IS '复权类型(只针对股票)：None未复权 qfq前复权 hfq后复权 , 默认None';
COMMENT ON COLUMN pro_bar.freq IS '数据频度 ：1MIN表示1分钟（1/5/15/30/60分钟） D日线 ，默认D';
COMMENT ON COLUMN pro_bar.ma IS '均线，支持任意周期的均价和均量，输入任意合理int数值';
COMMENT ON COLUMN pro_bar.request_time IS '请求时间';

-- 添加索引
CREATE INDEX idx_pro_bar_ts_code ON pro_bar(ts_code);
CREATE INDEX idx_pro_bar_request_time ON pro_bar(request_time);
CREATE INDEX idx_pro_bar_asset_freq ON pro_bar(asset, freq);

-- 添加外键（可选，取决于是否所有证券代码都在stock_basic表中）
-- 注意：由于这是一个参数表，可能包含不同类型的证券代码，
-- 所以可能不适合添加外键约束到stock_basic表
-- 如果只处理股票，则可以添加以下外键
/*
ALTER TABLE pro_bar 
ADD CONSTRAINT fk_pro_bar_stock_basic 
FOREIGN KEY (ts_code) 
REFERENCES stock_basic (ts_code)
WHERE asset = 'E';
*/


-- 名称	类型	必选	描述
-- ts_code	str	Y	证券代码
-- start_date	str	N	开始日期 (格式：YYYYMMDD)
-- end_date	str	N	结束日期 (格式：YYYYMMDD)
-- asset	str	Y	资产类别：E股票 I沪深指数 C数字货币 FT期货 FD基金 O期权，默认E
-- adj	str	N	复权类型(只针对股票)：None未复权 qfq前复权 hfq后复权 , 默认None
-- freq	str	Y	数据频度 ：1MIN表示1分钟（1/5/15/30/60分钟） D日线 ，默认D
-- ma	list	N	均线，支持任意周期的均价和均量，输入任意合理int数值