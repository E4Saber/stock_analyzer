-- 中美经济指标数据库表结构
-- China-US Economic Indicators Database Schema

-- 创建指标级别枚举类型
CREATE TYPE indicator_level AS ENUM ('核心', '次级', '交叉');

-- 创建指标表
CREATE TABLE economic_indicators (
    indicator_id SERIAL PRIMARY KEY,
    category_cn VARCHAR(50) NOT NULL,                -- 指标类别(中文)
    category_en VARCHAR(50) NOT NULL,                -- 指标类别(英文)
    us_indicator_name_cn VARCHAR(100),               -- 美国(US)指标名称(中文)
    us_indicator_name_en VARCHAR(100),               -- 美国(US)指标名称(英文)
    china_indicator_name_cn VARCHAR(100),            -- 中国(CHINA)指标名称(中文)
    china_indicator_name_en VARCHAR(100),            -- 中国(CHINA)指标名称(英文)
    us_data_source VARCHAR(200),                     -- 美国数据来源
    us_data_url VARCHAR(255),                        -- 美国数据来源URL
    china_data_source VARCHAR(200),                  -- 中国数据来源
    china_data_url VARCHAR(255),                     -- 中国数据来源URL
    indicator_type VARCHAR(50),                      -- 指标性质(先行/同步/滞后)
    publication_frequency VARCHAR(50),               -- 发布频率
    importance VARCHAR(10),                          -- 重要性(星级)
    level indicator_level NOT NULL,                  -- 指标级别(核心/次级/交叉)
    notes TEXT,                                      -- 备注
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,  -- 创建时间
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP   -- 更新时间
);

-- 创建索引
CREATE INDEX idx_indicator_level ON economic_indicators(level);
CREATE INDEX idx_indicator_category_cn ON economic_indicators(category_cn);
CREATE INDEX idx_indicator_category_en ON economic_indicators(category_en);
CREATE INDEX idx_indicator_importance ON economic_indicators(importance);

-- 示例数据插入 (部分核心指标)
INSERT INTO economic_indicators (
    category_cn, category_en,
    us_indicator_name_cn, us_indicator_name_en,
    china_indicator_name_cn, china_indicator_name_en,
    us_data_source, us_data_url,
    china_data_source, china_data_url,
    indicator_type, publication_frequency, importance, level
) VALUES
    ('经济增长', 'Economic Growth', 
     'GDP增长率', 'GDP Growth Rate',
     'GDP增长率', 'GDP Growth Rate',
     'BEA Official Website', 'https://www.bea.gov/data/gdp/gross-domestic-product',
     'National Bureau of Statistics', 'http://www.stats.gov.cn/sj/',
     '同步指标', '季度/年度', '★★★★★', '核心'),
    
    ('就业市场', 'Labor Market', 
     '非农就业人口变化', 'Non-farm Payroll Change',
     '城镇调查失业率', 'Urban Surveyed Unemployment Rate',
     'U.S. Bureau of Labor Statistics', 'https://www.bls.gov/news.release/empsit.toc.htm',
     'National Bureau of Statistics', 'http://www.stats.gov.cn/was5/web/search?channelid=288041',
     '滞后指标', '月度', '★★★★★', '核心'),
     
    ('物价水平', 'Price Level', 
     '消费者价格指数 (CPI)', 'Consumer Price Index (CPI)',
     '居民消费价格指数 (CPI)', 'Consumer Price Index (CPI)',
     'U.S. Bureau of Labor Statistics', 'https://www.bls.gov/cpi/',
     'National Bureau of Statistics', 'http://www.stats.gov.cn/was5/web/search?channelid=288041',
     '滞后指标', '月度', '★★★★★', '核心');

-- 示例数据插入 (部分次级指标)
INSERT INTO economic_indicators (
    category_cn, category_en,
    us_indicator_name_cn, us_indicator_name_en,
    china_indicator_name_cn, china_indicator_name_en,
    us_data_source, us_data_url,
    china_data_source, china_data_url,
    indicator_type, publication_frequency, importance, level
) VALUES
    ('制造业', 'Manufacturing', 
     '耐用品订单', 'Durable Goods Orders',
     NULL, NULL,
     'U.S. Census Bureau', 'https://www.census.gov/manufacturing/m3/index.html',
     '', '',
     '先行指标', '月度', '★★★☆☆', '次级'),
     
    ('货币供应', 'Money Supply', 
     NULL, NULL,
     '广义货币供应量(M2)', 'Broad Money Supply (M2)',
     '', '',
     'People\'s Bank of China', 'http://www.pbc.gov.cn/diaochatongjisi/116219/index.html',
     '先行指标', '月度', '★★★★☆', '次级');

-- 示例数据插入 (部分交叉指标)
INSERT INTO economic_indicators (
    category_cn, category_en,
    us_indicator_name_cn, us_indicator_name_en,
    china_indicator_name_cn, china_indicator_name_en,
    us_data_source, us_data_url,
    china_data_source, china_data_url,
    indicator_type, publication_frequency, importance, level
) VALUES
    ('双边贸易', 'Bilateral Trade', 
     '美中贸易平衡', 'US-China Trade Balance',
     '中美贸易总额', 'China-US Trade Volume',
     'U.S. Census Bureau', 'https://www.census.gov/foreign-trade/balance/c5700.html',
     'China Customs', 'http://www.customs.gov.cn/',
     '同步指标', '月度', '★★★★★', '交叉'),
     
    ('汇率', 'Exchange Rate', 
     '人民币兑美元汇率', 'Chinese Yuan to U.S. Dollar',
     '人民币兑美元汇率', 'RMB to USD Exchange Rate',
     'Federal Reserve', 'https://www.federalreserve.gov/releases/h10/current/',
     'China Foreign Exchange Trade System', 'https://www.chinamoney.com.cn/',
     '先行指标', '每日', '★★★★★', '交叉');

-- 创建视图: 核心经济指标
CREATE VIEW core_economic_indicators AS
SELECT * FROM economic_indicators WHERE level = '核心';

-- 创建视图: 次级经济指标
CREATE VIEW secondary_economic_indicators AS
SELECT * FROM economic_indicators WHERE level = '次级';

-- 创建视图: 中美交叉经济指标
CREATE VIEW cross_economic_indicators AS
SELECT * FROM economic_indicators WHERE level = '交叉';

-- 创建视图: 美国经济指标
CREATE VIEW us_economic_indicators AS
SELECT * FROM economic_indicators WHERE us_indicator_name_cn IS NOT NULL;

-- 创建视图: 中国经济指标
CREATE VIEW china_economic_indicators AS
SELECT * FROM economic_indicators WHERE china_indicator_name_cn IS NOT NULL;