-- 股票数据 - 行情数据

-- 每日停复牌信息（suspend_d）
CREATE TABLE suspend_d (
    id SERIAL PRIMARY KEY,                -- 自增主键
    ts_code VARCHAR(20) NOT NULL,         -- TS代码
    trade_date DATE NOT NULL,             -- 停复牌日期
    suspend_timing VARCHAR(50),           -- 日内停牌时间段
    suspend_type CHAR(1) NOT NULL,        -- 停复牌类型：S-停牌，R-复牌
    CONSTRAINT uk_suspend_d_ts_code_trade_date UNIQUE (ts_code, trade_date),
    CONSTRAINT ck_suspend_d_suspend_type CHECK (suspend_type IN ('S', 'R'))
);

-- 表注释
COMMENT ON TABLE suspend_d IS '停复牌信息';

-- 列注释
COMMENT ON COLUMN suspend_d.id IS '自增主键';
COMMENT ON COLUMN suspend_d.ts_code IS 'TS代码';
COMMENT ON COLUMN suspend_d.trade_date IS '停复牌日期';
COMMENT ON COLUMN suspend_d.suspend_timing IS '日内停牌时间段';
COMMENT ON COLUMN suspend_d.suspend_type IS '停复牌类型：S-停牌，R-复牌';

-- 添加索引
CREATE INDEX idx_suspend_d_ts_code ON suspend_d(ts_code);
CREATE INDEX idx_suspend_d_trade_date ON suspend_d(trade_date);
CREATE INDEX idx_suspend_d_suspend_type ON suspend_d(suspend_type);
CREATE INDEX idx_suspend_d_ts_code_trade_date ON suspend_d(ts_code, trade_date);

-- 添加外键关联到股票基本信息表
ALTER TABLE suspend_d 
ADD CONSTRAINT fk_suspend_d_stock_basic 
FOREIGN KEY (ts_code) 
REFERENCES stock_basic (ts_code);


-- 名称	类型	默认显示	描述
-- ts_code	str	Y	TS代码
-- trade_date	str	Y	停复牌日期
-- suspend_timing	str	Y	日内停牌时间段
-- suspend_type	str	Y	停复牌类型：S-停牌，R-复牌