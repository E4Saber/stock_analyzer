-- 股票数据 - 基础数据

-- 管理层薪酬和持股（stk_rewards）
CREATE TABLE stk_rewards (
    id SERIAL,                         -- 自增主键
    ts_code VARCHAR(20) NOT NULL,      -- TS股票代码
    ann_date DATE,                     -- 公告日期
    end_date DATE,                     -- 截止日期
    name VARCHAR(50) NOT NULL,         -- 姓名
    title VARCHAR(50),                 -- 职务
    reward NUMERIC(20,2),              -- 报酬
    hold_vol NUMERIC(20,2),            -- 持股数
    
    PRIMARY KEY (id),
    UNIQUE (ts_code, name, end_date)   -- 唯一约束
);

-- 添加外键约束
ALTER TABLE stk_rewards
ADD CONSTRAINT fk_stk_rewards_stock_basic
FOREIGN KEY (ts_code) REFERENCES stock_basic(ts_code);

-- 添加索引
CREATE INDEX idx_stk_rewards_ts_code ON stk_rewards(ts_code);
CREATE INDEX idx_stk_rewards_name ON stk_rewards(name);
CREATE INDEX idx_stk_rewards_end_date ON stk_rewards(end_date);


-- 名称	类型	默认显示	描述
-- ts_code	str	Y	TS股票代码
-- ann_date	str	Y	公告日期
-- end_date	str	Y	截止日期
-- name	str	Y	姓名
-- title	str	Y	职务
-- reward	float	Y	报酬
-- hold_vol	float	Y	持股数