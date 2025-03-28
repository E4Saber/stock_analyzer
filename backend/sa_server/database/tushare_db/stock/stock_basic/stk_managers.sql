-- 股票数据 - 基础数据

-- 上市公司管理层（stk_managers）
CREATE TABLE stk_managers (
    id SERIAL,                           -- 自增主键
    ts_code VARCHAR(20) NOT NULL,        -- TS股票代码
    ann_date DATE,                       -- 公告日期
    name VARCHAR(50) NOT NULL,           -- 姓名
    gender VARCHAR(2),                   -- 性别
    lev VARCHAR(30),                     -- 岗位类别
    title VARCHAR(50),                   -- 岗位
    edu VARCHAR(30),                     -- 学历
    national VARCHAR(30),                -- 国籍
    birthday VARCHAR(20),                -- 出生年月
    begin_date DATE,                     -- 上任日期
    end_date DATE,                       -- 离任日期
    resume TEXT,                         -- 个人简历
    
    PRIMARY KEY (id),
    UNIQUE (ts_code, name, begin_date)   -- 唯一约束
);

-- 添加表注释
COMMENT ON TABLE stk_managers IS '上市公司管理层信息';

-- 添加字段注释
COMMENT ON COLUMN stk_managers.id IS '自增主键';
COMMENT ON COLUMN stk_managers.ts_code IS 'TS股票代码';
COMMENT ON COLUMN stk_managers.ann_date IS '公告日期';
COMMENT ON COLUMN stk_managers.name IS '姓名';
COMMENT ON COLUMN stk_managers.gender IS '性别';
COMMENT ON COLUMN stk_managers.lev IS '岗位类别';
COMMENT ON COLUMN stk_managers.title IS '岗位';
COMMENT ON COLUMN stk_managers.edu IS '学历';
COMMENT ON COLUMN stk_managers.national IS '国籍';
COMMENT ON COLUMN stk_managers.birthday IS '出生年月';
COMMENT ON COLUMN stk_managers.begin_date IS '上任日期';
COMMENT ON COLUMN stk_managers.end_date IS '离任日期';
COMMENT ON COLUMN stk_managers.resume IS '个人简历';

-- 添加外键约束
ALTER TABLE stk_managers
ADD CONSTRAINT fk_stk_managers_stock_basic
FOREIGN KEY (ts_code) REFERENCES stock_basic(ts_code);

-- 添加索引
CREATE INDEX idx_stk_managers_ts_code ON stk_managers(ts_code);
CREATE INDEX idx_stk_managers_name ON stk_managers(name);
CREATE INDEX idx_stk_managers_dates ON stk_managers(begin_date, end_date);


-- 名称	类型	默认显示	描述
-- ts_code	str	Y	TS股票代码
-- ann_date	str	Y	公告日期
-- name	str	Y	姓名
-- gender	str	Y	性别
-- lev	str	Y	岗位类别
-- title	str	Y	岗位
-- edu	str	Y	学历
-- national	str	Y	国籍
-- birthday	str	Y	出生年月
-- begin_date	str	Y	上任日期
-- end_date	str	Y	离任日期
-- resume	str	N	个人简历