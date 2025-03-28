-- 股票数据 - 基础数据

-- 股票曾用名（namechange）
CREATE TABLE namechange (
    id SERIAL,                         -- 自增主键
    ts_code VARCHAR(20) NOT NULL,      -- TS代码
    name VARCHAR(50) NOT NULL,         -- 证券名称
    start_date DATE NOT NULL,          -- 开始日期
    end_date DATE,                     -- 结束日期
    ann_date DATE,                     -- 公告日期
    change_reason VARCHAR(200),        -- 变更原因
    
    PRIMARY KEY (id),
    UNIQUE (ts_code, start_date)       -- 唯一约束：同一股票在同一开始日期只能有一个名称
);

-- 表注释
COMMENT ON TABLE namechange IS '股票名称变更记录';

-- 列注释
COMMENT ON COLUMN namechange.id IS '记录ID';
COMMENT ON COLUMN namechange.ts_code IS 'TS代码';
COMMENT ON COLUMN namechange.name IS '证券名称';
COMMENT ON COLUMN namechange.start_date IS '开始日期';
COMMENT ON COLUMN namechange.end_date IS '结束日期';
COMMENT ON COLUMN namechange.ann_date IS '公告日期';
COMMENT ON COLUMN namechange.change_reason IS '变更原因';

-- 添加索引
CREATE INDEX idx_namechange_ts_code ON namechange(ts_code);
CREATE INDEX idx_namechange_dates ON namechange(start_date, end_date);
CREATE INDEX idx_namechange_ann_date ON namechange(ann_date);

-- 添加外键约束 (如果与stock_basic表关联)
ALTER TABLE namechange
ADD CONSTRAINT fk_namechange_stock_basic
FOREIGN KEY (ts_code) REFERENCES stock_basic(ts_code);


-- 名称	类型	默认输出	描述
-- ts_code	str	Y	TS代码
-- name	str	Y	证券名称
-- start_date	str	Y	开始日期
-- end_date	str	Y	结束日期
-- ann_date	str	Y	公告日期
-- change_reason	str	Y	变更原因