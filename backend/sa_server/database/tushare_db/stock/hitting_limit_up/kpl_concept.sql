-- 股票数据 - 打板专题

-- 题材概念表（kpl_concept）
CREATE TABLE kpl_concept (
    -- Primary key and identification fields
    id SERIAL PRIMARY KEY,
    trade_date DATE NOT NULL,
    ts_code VARCHAR(12) NOT NULL,
    name VARCHAR(100) NOT NULL,
    
    -- Concept information
    z_t_num INTEGER,
    up_num INTEGER
);

-- Create indexes for frequently queried fields
CREATE INDEX idx_kpl_concept_trade_date ON kpl_concept(trade_date);
CREATE INDEX idx_kpl_concept_ts_code ON kpl_concept(ts_code);
CREATE INDEX idx_kpl_concept_name ON kpl_concept(name);

-- Add unique constraint for upsert operations
ALTER TABLE kpl_concept ADD CONSTRAINT kpl_concept_unique_key 
UNIQUE (trade_date, ts_code);

-- Add table comment
COMMENT ON TABLE kpl_concept IS '题材概念';

-- Add column comments
COMMENT ON COLUMN kpl_concept.trade_date IS '交易日期';
COMMENT ON COLUMN kpl_concept.ts_code IS '题材代码';
COMMENT ON COLUMN kpl_concept.name IS '题材名称';
COMMENT ON COLUMN kpl_concept.z_t_num IS '涨停数量';
COMMENT ON COLUMN kpl_concept.up_num IS '排名上升位数';

-- 名称	类型	描述
-- trade_date	str	交易日期
-- ts_code	str	题材代码
-- name	str	题材名称
-- z_t_num	int	涨停数量
-- up_num	int	排名上升位数