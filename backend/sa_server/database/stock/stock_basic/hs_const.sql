-- 股票数据 - 基础数据

-- 沪深股通成份股（hs_const）
CREATE TABLE hs_const (
    id SERIAL,                       -- 自增主键
    ts_code VARCHAR(20) NOT NULL,    -- TS代码
    hs_type VARCHAR(2) NOT NULL,     -- 沪深港通类型
    in_date DATE NOT NULL,           -- 纳入日期
    out_date DATE,                   -- 剔除日期
    is_new CHAR(1) NOT NULL,         -- 是否最新
    
    PRIMARY KEY (id),
    UNIQUE (ts_code, hs_type, in_date) -- 唯一约束
);

-- 表注释
COMMENT ON TABLE hs_const IS '沪深港通成分股';

-- 列注释
COMMENT ON COLUMN hs_const.id IS '记录ID';
COMMENT ON COLUMN hs_const.ts_code IS 'TS代码';
COMMENT ON COLUMN hs_const.hs_type IS '沪深港通类型 SH沪 SZ深';
COMMENT ON COLUMN hs_const.in_date IS '纳入日期';
COMMENT ON COLUMN hs_const.out_date IS '剔除日期';
COMMENT ON COLUMN hs_const.is_new IS '是否最新 1是 0否';

-- 添加索引
CREATE INDEX idx_hs_const_ts_code ON hs_const(ts_code);
CREATE INDEX idx_hs_const_hs_type ON hs_const(hs_type);
CREATE INDEX idx_hs_const_in_date ON hs_const(in_date);
CREATE INDEX idx_hs_const_is_new ON hs_const(is_new);

-- 添加外键约束 (如果与stock_basic表关联)
ALTER TABLE hs_const
ADD CONSTRAINT fk_hs_const_stock_basic
FOREIGN KEY (ts_code) REFERENCES stock_basic(ts_code);


-- 名称	类型	默认显示	描述
-- ts_code	str	Y	TS代码
-- hs_type	str	Y	沪深港通类型SH沪SZ深
-- in_date	str	Y	纳入日期
-- out_date	str	Y	剔除日期
-- is_new	str	Y	是否最新 1是 0否
