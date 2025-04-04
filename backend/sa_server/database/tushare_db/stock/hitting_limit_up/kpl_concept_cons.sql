-- 题材概念成分表（kpl_concept_cons）
CREATE TABLE kpl_concept_cons (
    -- Primary key and identification fields
    id SERIAL PRIMARY KEY,
    trade_date DATE NOT NULL,
    ts_code VARCHAR(12) NOT NULL,
    name VARCHAR(100) NOT NULL,
    con_code VARCHAR(12) NOT NULL,
    con_name VARCHAR(100) NOT NULL,
    
    -- Additional fields
    desc TEXT,
    hot_num INTEGER
);

-- Create indexes for frequently queried fields
CREATE INDEX idx_kpl_concept_cons_trade_date ON kpl_concept_cons(trade_date);
CREATE INDEX idx_kpl_concept_cons_ts_code ON kpl_concept_cons(ts_code);
CREATE INDEX idx_kpl_concept_cons_con_code ON kpl_concept_cons(con_code);
CREATE INDEX idx_kpl_concept_cons_name ON kpl_concept_cons(name);
CREATE INDEX idx_kpl_concept_cons_con_name ON kpl_concept_cons(con_name);

-- Add unique constraint for upsert operations
ALTER TABLE kpl_concept_cons ADD CONSTRAINT kpl_concept_cons_unique_key 
UNIQUE (trade_date, ts_code, con_code);

-- Add table comment
COMMENT ON TABLE kpl_concept_cons IS '题材概念成分';

-- Add column comments
COMMENT ON COLUMN kpl_concept_cons.trade_date IS '交易日期';
COMMENT ON COLUMN kpl_concept_cons.ts_code IS '题材代码';
COMMENT ON COLUMN kpl_concept_cons.name IS '题材名称';
COMMENT ON COLUMN kpl_concept_cons.con_code IS '股票代码';
COMMENT ON COLUMN kpl_concept_cons.con_name IS '股票名称';
COMMENT ON COLUMN kpl_concept_cons.desc IS '描述';
COMMENT ON COLUMN kpl_concept_cons.hot_num IS '人气值';

-- 名称	类型	描述
-- trade_date	str	交易日期
-- ts_code	str	题材ID
-- name	str	题材名称
-- con_code	str	股票代码
-- con_name	str	股票名称
-- desc	str	描述
-- hot_num	int	人气值