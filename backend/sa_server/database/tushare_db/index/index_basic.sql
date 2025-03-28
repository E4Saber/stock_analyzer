-- 指数数据

-- 指数基本信息（index_basic）
CREATE TABLE index_basic (
    ts_code VARCHAR(20) PRIMARY KEY,     -- TS代码
    name VARCHAR(50) NOT NULL,           -- 简称
    fullname VARCHAR(100),               -- 指数全称
    market VARCHAR(30),                  -- 市场
    publisher VARCHAR(50),               -- 发布方
    index_type VARCHAR(30),              -- 指数风格
    category VARCHAR(30),                -- 指数类别
    base_date DATE,                      -- 基期
    base_point FLOAT,                    -- 基点
    list_date DATE,                      -- 发布日期
    weight_rule VARCHAR(30),             -- 加权方式
    description TEXT,                    -- 描述
    exp_date DATE                        -- 终止日期
);

-- 表注释
COMMENT ON TABLE index_basic IS '指数基本信息';

-- 列注释
COMMENT ON COLUMN index_basic.ts_code IS 'TS代码';
COMMENT ON COLUMN index_basic.name IS '简称';
COMMENT ON COLUMN index_basic.fullname IS '指数全称';
COMMENT ON COLUMN index_basic.market IS '市场';
COMMENT ON COLUMN index_basic.publisher IS '发布方';
COMMENT ON COLUMN index_basic.index_type IS '指数风格';
COMMENT ON COLUMN index_basic.category IS '指数类别';
COMMENT ON COLUMN index_basic.base_date IS '基期';
COMMENT ON COLUMN index_basic.base_point IS '基点';
COMMENT ON COLUMN index_basic.list_date IS '发布日期';
COMMENT ON COLUMN index_basic.weight_rule IS '加权方式';
COMMENT ON COLUMN index_basic.description IS '描述';
COMMENT ON COLUMN index_basic.exp_date IS '终止日期';

-- 添加索引
CREATE INDEX idx_index_basic_name ON index_basic(name);
CREATE INDEX idx_index_basic_market ON index_basic(market);
CREATE INDEX idx_index_basic_publisher ON index_basic(publisher);
CREATE INDEX idx_index_basic_category ON index_basic(category);
CREATE INDEX idx_index_basic_list_date ON index_basic(list_date);

-- 注意：原始定义中的desc字段被修改为description，因为desc是SQL关键字


-- 名称	类型	描述
-- ts_code	str	TS代码
-- name	str	简称
-- fullname	str	指数全称
-- market	str	市场
-- publisher	str	发布方
-- index_type	str	指数风格
-- category	str	指数类别
-- base_date	str	基期
-- base_point	float	基点
-- list_date	str	发布日期
-- weight_rule	str	加权方式
-- desc	str	描述
-- exp_date	str	终止日期