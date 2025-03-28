-- 股票数据 - 基础数据

-- 交易日历（tarde_cal）
CREATE TABLE tarde_cal (
    exchange VARCHAR(10) NOT NULL,       -- 交易所代码
    cal_date DATE NOT NULL,              -- 日历日期
    is_open SMALLINT NOT NULL,           -- 是否交易日
    pretrade_date DATE,                  -- 上一个交易日
    
    PRIMARY KEY (exchange, cal_date)     -- 复合主键
);

-- 表注释
COMMENT ON TABLE tarde_cal IS '交易所交易日历';

-- 列注释
COMMENT ON COLUMN tarde_cal.exchange IS '交易所 SSE上交所 SZSE深交所';
COMMENT ON COLUMN tarde_cal.cal_date IS '日历日期';
COMMENT ON COLUMN tarde_cal.is_open IS '是否交易 0休市 1交易';
COMMENT ON COLUMN tarde_cal.pretrade_date IS '上一个交易日';

-- 添加索引
CREATE INDEX idx_tarde_cal_cal_date ON tarde_cal(cal_date);
CREATE INDEX idx_tarde_cal_is_open ON tarde_cal(is_open);


-- 名称	类型	默认显示	描述
-- exchange	str	Y	交易所 SSE上交所 SZSE深交所
-- cal_date	str	Y	日历日期
-- is_open	str	Y	是否交易 0休市 1交易
-- pretrade_date	str	Y	上一个交易日