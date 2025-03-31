-- SHIBOR报价数据表

-- SHIBOR报价（shibor_quote）
CREATE TABLE shibor_quote (
    date DATE NOT NULL,               -- 日期
    bank VARCHAR(50) NOT NULL,        -- 报价银行
    on_b FLOAT,                       -- 隔夜_Bid
    on_a FLOAT,                       -- 隔夜_Ask
    w1_b FLOAT,                       -- 1周_Bid
    w1_a FLOAT,                       -- 1周_Ask
    w2_b FLOAT,                       -- 2周_Bid
    w2_a FLOAT,                       -- 2周_Ask
    m1_b FLOAT,                       -- 1月_Bid
    m1_a FLOAT,                       -- 1月_Ask
    m3_b FLOAT,                       -- 3月_Bid
    m3_a FLOAT,                       -- 3月_Ask
    m6_b FLOAT,                       -- 6月_Bid
    m6_a FLOAT,                       -- 6月_Ask
    m9_b FLOAT,                       -- 9月_Bid
    m9_a FLOAT,                       -- 9月_Ask
    y1_b FLOAT,                       -- 1年_Bid
    y1_a FLOAT,                       -- 1年_Ask
    PRIMARY KEY (date, bank)          -- 复合主键：日期+银行
);

-- 表注释
COMMENT ON TABLE shibor_quote IS 'SHIBOR报价数据';

-- 列注释
COMMENT ON COLUMN shibor_quote.date IS '日期';
COMMENT ON COLUMN shibor_quote.bank IS '报价银行';
COMMENT ON COLUMN shibor_quote.on_b IS '隔夜_Bid';
COMMENT ON COLUMN shibor_quote.on_a IS '隔夜_Ask';
COMMENT ON COLUMN shibor_quote.w1_b IS '1周_Bid';
COMMENT ON COLUMN shibor_quote.w1_a IS '1周_Ask';
COMMENT ON COLUMN shibor_quote.w2_b IS '2周_Bid';
COMMENT ON COLUMN shibor_quote.w2_a IS '2周_Ask';
COMMENT ON COLUMN shibor_quote.m1_b IS '1月_Bid';
COMMENT ON COLUMN shibor_quote.m1_a IS '1月_Ask';
COMMENT ON COLUMN shibor_quote.m3_b IS '3月_Bid';
COMMENT ON COLUMN shibor_quote.m3_a IS '3月_Ask';
COMMENT ON COLUMN shibor_quote.m6_b IS '6月_Bid';
COMMENT ON COLUMN shibor_quote.m6_a IS '6月_Ask';
COMMENT ON COLUMN shibor_quote.m9_b IS '9月_Bid';
COMMENT ON COLUMN shibor_quote.m9_a IS '9月_Ask';
COMMENT ON COLUMN shibor_quote.y1_b IS '1年_Bid';
COMMENT ON COLUMN shibor_quote.y1_a IS '1年_Ask';

-- 添加索引
CREATE INDEX idx_shibor_quote_date ON shibor_quote(date);
CREATE INDEX idx_shibor_quote_bank ON shibor_quote(bank);


-- 名称	类型	默认显示	描述
-- date	str	Y	日期
-- bank	str	Y	报价银行
-- on_b	float	Y	隔夜_Bid
-- on_a	float	Y	隔夜_Ask
-- 1w_b	float	Y	1周_Bid
-- 1w_a	float	Y	1周_Ask
-- 2w_b	float	Y	2周_Bid
-- 2w_a	float	Y	2周_Ask
-- 1m_b	float	Y	1月_Bid
-- 1m_a	float	Y	1月_Ask
-- 3m_b	float	Y	3月_Bid
-- 3m_a	float	Y	3月_Ask
-- 6m_b	float	Y	6月_Bid
-- 6m_a	float	Y	6月_Ask
-- 9m_b	float	Y	9月_Bid
-- 9m_a	float	Y	9月_Ask
-- 1y_b	float	Y	1年_Bid
-- 1y_a	float	Y	1年_Ask