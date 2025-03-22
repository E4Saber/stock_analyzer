-- 股票数据 - 基础数据

-- 上市公司基本信息（stock_company）
CREATE TABLE stock_company (
    ts_code VARCHAR(20) PRIMARY KEY,       -- 股票代码
    com_name VARCHAR(100) NOT NULL,        -- 公司全称
    com_id VARCHAR(30),                    -- 统一社会信用代码
    exchange VARCHAR(20),                  -- 交易所代码
    chairman VARCHAR(50),                  -- 法人代表
    manager VARCHAR(50),                   -- 总经理
    secretary VARCHAR(50),                 -- 董秘
    reg_capital NUMERIC(20,2),             -- 注册资本(万元)
    setup_date DATE,                       -- 注册日期
    province VARCHAR(30),                  -- 所在省份
    city VARCHAR(30),                      -- 所在城市
    introduction TEXT,                     -- 公司介绍
    website VARCHAR(100),                  -- 公司主页
    email VARCHAR(100),                    -- 电子邮件
    office VARCHAR(150),                   -- 办公室
    employees INTEGER,                     -- 员工人数
    main_business TEXT,                    -- 主要业务及产品
    business_scope TEXT                    -- 经营范围
);

-- 添加外键约束
ALTER TABLE stock_company
ADD CONSTRAINT fk_stock_company_stock_basic
FOREIGN KEY (ts_code) REFERENCES stock_basic(ts_code);

-- 添加索引
CREATE INDEX idx_stock_company_com_id ON stock_company(com_id);
CREATE INDEX idx_stock_company_province ON stock_company(province);


-- 名称	类型	默认显示	描述
-- ts_code	str	Y	股票代码
-- com_name	str	Y	公司全称
-- com_id	str	Y	统一社会信用代码
-- exchange	str	Y	交易所代码
-- chairman	str	Y	法人代表
-- manager	str	Y	总经理
-- secretary	str	Y	董秘
-- reg_capital	float	Y	注册资本(万元)
-- setup_date	str	Y	注册日期
-- province	str	Y	所在省份
-- city	str	Y	所在城市
-- introduction	str	N	公司介绍
-- website	str	Y	公司主页
-- email	str	Y	电子邮件
-- office	str	N	办公室
-- employees	int	Y	员工人数
-- main_business	str	N	主要业务及产品
-- business_scope	str	N	经营范围