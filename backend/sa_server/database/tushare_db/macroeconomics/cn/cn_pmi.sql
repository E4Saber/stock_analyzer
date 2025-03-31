-- 中国PMI指数数据表

-- PMI指数表（cn_pmi）
CREATE TABLE cn_pmi (
    month VARCHAR(6) PRIMARY KEY,         -- 月份，格式YYYYMM
    pmi010000 FLOAT,                      -- 制造业PMI
    pmi010100 FLOAT,                      -- 制造业PMI:企业规模/大型企业
    pmi010200 FLOAT,                      -- 制造业PMI:企业规模/中型企业
    pmi010300 FLOAT,                      -- 制造业PMI:企业规模/小型企业
    pmi010400 FLOAT,                      -- 制造业PMI:构成指数/生产指数
    pmi010401 FLOAT,                      -- 制造业PMI:构成指数/生产指数:企业规模/大型企业
    pmi010402 FLOAT,                      -- 制造业PMI:构成指数/生产指数:企业规模/中型企业
    pmi010403 FLOAT,                      -- 制造业PMI:构成指数/生产指数:企业规模/小型企业
    pmi010500 FLOAT,                      -- 制造业PMI:构成指数/新订单指数
    pmi010501 FLOAT,                      -- 制造业PMI:构成指数/新订单指数:企业规模/大型企业
    pmi010502 FLOAT,                      -- 制造业PMI:构成指数/新订单指数:企业规模/中型企业
    pmi010503 FLOAT,                      -- 制造业PMI:构成指数/新订单指数:企业规模/小型企业
    pmi010600 FLOAT,                      -- 制造业PMI:构成指数/供应商配送时间指数
    pmi010601 FLOAT,                      -- 制造业PMI:构成指数/供应商配送时间指数:企业规模/大型企业
    pmi010602 FLOAT,                      -- 制造业PMI:构成指数/供应商配送时间指数:企业规模/中型企业
    pmi010603 FLOAT,                      -- 制造业PMI:构成指数/供应商配送时间指数:企业规模/小型企业
    pmi010700 FLOAT,                      -- 制造业PMI:构成指数/原材料库存指数
    pmi010701 FLOAT,                      -- 制造业PMI:构成指数/原材料库存指数:企业规模/大型企业
    pmi010702 FLOAT,                      -- 制造业PMI:构成指数/原材料库存指数:企业规模/中型企业
    pmi010703 FLOAT,                      -- 制造业PMI:构成指数/原材料库存指数:企业规模/小型企业
    pmi010800 FLOAT,                      -- 制造业PMI:构成指数/从业人员指数
    pmi010801 FLOAT,                      -- 制造业PMI:构成指数/从业人员指数:企业规模/大型企业
    pmi010802 FLOAT,                      -- 制造业PMI:构成指数/从业人员指数:企业规模/中型企业
    pmi010803 FLOAT,                      -- 制造业PMI:构成指数/从业人员指数:企业规模/小型企业
    pmi010900 FLOAT,                      -- 制造业PMI:其他/新出口订单
    pmi011000 FLOAT,                      -- 制造业PMI:其他/进口
    pmi011100 FLOAT,                      -- 制造业PMI:其他/采购量
    pmi011200 FLOAT,                      -- 制造业PMI:其他/主要原材料购进价格
    pmi011300 FLOAT,                      -- 制造业PMI:其他/出厂价格
    pmi011400 FLOAT,                      -- 制造业PMI:其他/产成品库存
    pmi011500 FLOAT,                      -- 制造业PMI:其他/在手订单
    pmi011600 FLOAT,                      -- 制造业PMI:其他/生产经营活动预期
    pmi011700 FLOAT,                      -- 制造业PMI:分行业/装备制造业
    pmi011800 FLOAT,                      -- 制造业PMI:分行业/高技术制造业
    pmi011900 FLOAT,                      -- 制造业PMI:分行业/基础原材料制造业
    pmi012000 FLOAT,                      -- 制造业PMI:分行业/消费品制造业
    pmi020100 FLOAT,                      -- 非制造业PMI:商务活动
    pmi020101 FLOAT,                      -- 非制造业PMI:商务活动:分行业/建筑业
    pmi020102 FLOAT,                      -- 非制造业PMI:商务活动:分行业/服务业
    pmi020200 FLOAT,                      -- 非制造业PMI:新订单指数
    pmi020201 FLOAT,                      -- 非制造业PMI:新订单指数:分行业/建筑业
    pmi020202 FLOAT,                      -- 非制造业PMI:新订单指数:分行业/服务业
    pmi020300 FLOAT,                      -- 非制造业PMI:投入品价格指数
    pmi020301 FLOAT,                      -- 非制造业PMI:投入品价格指数:分行业/建筑业
    pmi020302 FLOAT,                      -- 非制造业PMI:投入品价格指数:分行业/服务业
    pmi020400 FLOAT,                      -- 非制造业PMI:销售价格指数
    pmi020401 FLOAT,                      -- 非制造业PMI:销售价格指数:分行业/建筑业
    pmi020402 FLOAT,                      -- 非制造业PMI:销售价格指数:分行业/服务业
    pmi020500 FLOAT,                      -- 非制造业PMI:从业人员指数
    pmi020501 FLOAT,                      -- 非制造业PMI:从业人员指数:分行业/建筑业
    pmi020502 FLOAT,                      -- 非制造业PMI:从业人员指数:分行业/服务业
    pmi020600 FLOAT,                      -- 非制造业PMI:业务活动预期指数
    pmi020601 FLOAT,                      -- 非制造业PMI:业务活动预期指数:分行业/建筑业
    pmi020602 FLOAT,                      -- 非制造业PMI:业务活动预期指数:分行业/服务业
    pmi020700 FLOAT,                      -- 非制造业PMI:新出口订单
    pmi020800 FLOAT,                      -- 非制造业PMI:在手订单
    pmi020900 FLOAT,                      -- 非制造业PMI:存货
    pmi021000 FLOAT,                      -- 非制造业PMI:供应商配送时间
    pmi030000 FLOAT                       -- 中国综合PMI:产出指数
);

-- 表注释
COMMENT ON TABLE cn_pmi IS '中国PMI数据';

-- 列注释
COMMENT ON COLUMN cn_pmi.month IS '月份，格式YYYYMM';
COMMENT ON COLUMN cn_pmi.pmi010000 IS '制造业PMI';
COMMENT ON COLUMN cn_pmi.pmi010100 IS '制造业PMI:企业规模/大型企业';
COMMENT ON COLUMN cn_pmi.pmi010200 IS '制造业PMI:企业规模/中型企业';
COMMENT ON COLUMN cn_pmi.pmi010300 IS '制造业PMI:企业规模/小型企业';
COMMENT ON COLUMN cn_pmi.pmi010400 IS '制造业PMI:构成指数/生产指数';
COMMENT ON COLUMN cn_pmi.pmi010401 IS '制造业PMI:构成指数/生产指数:企业规模/大型企业';
COMMENT ON COLUMN cn_pmi.pmi010402 IS '制造业PMI:构成指数/生产指数:企业规模/中型企业';
COMMENT ON COLUMN cn_pmi.pmi010403 IS '制造业PMI:构成指数/生产指数:企业规模/小型企业';
COMMENT ON COLUMN cn_pmi.pmi010500 IS '制造业PMI:构成指数/新订单指数';
COMMENT ON COLUMN cn_pmi.pmi010501 IS '制造业PMI:构成指数/新订单指数:企业规模/大型企业';
COMMENT ON COLUMN cn_pmi.pmi010502 IS '制造业PMI:构成指数/新订单指数:企业规模/中型企业';
COMMENT ON COLUMN cn_pmi.pmi010503 IS '制造业PMI:构成指数/新订单指数:企业规模/小型企业';
COMMENT ON COLUMN cn_pmi.pmi010600 IS '制造业PMI:构成指数/供应商配送时间指数';
COMMENT ON COLUMN cn_pmi.pmi010601 IS '制造业PMI:构成指数/供应商配送时间指数:企业规模/大型企业';
COMMENT ON COLUMN cn_pmi.pmi010602 IS '制造业PMI:构成指数/供应商配送时间指数:企业规模/中型企业';
COMMENT ON COLUMN cn_pmi.pmi010603 IS '制造业PMI:构成指数/供应商配送时间指数:企业规模/小型企业';
COMMENT ON COLUMN cn_pmi.pmi010700 IS '制造业PMI:构成指数/原材料库存指数';
COMMENT ON COLUMN cn_pmi.pmi010701 IS '制造业PMI:构成指数/原材料库存指数:企业规模/大型企业';
COMMENT ON COLUMN cn_pmi.pmi010702 IS '制造业PMI:构成指数/原材料库存指数:企业规模/中型企业';
COMMENT ON COLUMN cn_pmi.pmi010703 IS '制造业PMI:构成指数/原材料库存指数:企业规模/小型企业';
COMMENT ON COLUMN cn_pmi.pmi010800 IS '制造业PMI:构成指数/从业人员指数';
COMMENT ON COLUMN cn_pmi.pmi010801 IS '制造业PMI:构成指数/从业人员指数:企业规模/大型企业';
COMMENT ON COLUMN cn_pmi.pmi010802 IS '制造业PMI:构成指数/从业人员指数:企业规模/中型企业';
COMMENT ON COLUMN cn_pmi.pmi010803 IS '制造业PMI:构成指数/从业人员指数:企业规模/小型企业';
COMMENT ON COLUMN cn_pmi.pmi010900 IS '制造业PMI:其他/新出口订单';
COMMENT ON COLUMN cn_pmi.pmi011000 IS '制造业PMI:其他/进口';
COMMENT ON COLUMN cn_pmi.pmi011100 IS '制造业PMI:其他/采购量';
COMMENT ON COLUMN cn_pmi.pmi011200 IS '制造业PMI:其他/主要原材料购进价格';
COMMENT ON COLUMN cn_pmi.pmi011300 IS '制造业PMI:其他/出厂价格';
COMMENT ON COLUMN cn_pmi.pmi011400 IS '制造业PMI:其他/产成品库存';
COMMENT ON COLUMN cn_pmi.pmi011500 IS '制造业PMI:其他/在手订单';
COMMENT ON COLUMN cn_pmi.pmi011600 IS '制造业PMI:其他/生产经营活动预期';
COMMENT ON COLUMN cn_pmi.pmi011700 IS '制造业PMI:分行业/装备制造业';
COMMENT ON COLUMN cn_pmi.pmi011800 IS '制造业PMI:分行业/高技术制造业';
COMMENT ON COLUMN cn_pmi.pmi011900 IS '制造业PMI:分行业/基础原材料制造业';
COMMENT ON COLUMN cn_pmi.pmi012000 IS '制造业PMI:分行业/消费品制造业';
COMMENT ON COLUMN cn_pmi.pmi020100 IS '非制造业PMI:商务活动';
COMMENT ON COLUMN cn_pmi.pmi020101 IS '非制造业PMI:商务活动:分行业/建筑业';
COMMENT ON COLUMN cn_pmi.pmi020102 IS '非制造业PMI:商务活动:分行业/服务业';
COMMENT ON COLUMN cn_pmi.pmi020200 IS '非制造业PMI:新订单指数';
COMMENT ON COLUMN cn_pmi.pmi020201 IS '非制造业PMI:新订单指数:分行业/建筑业';
COMMENT ON COLUMN cn_pmi.pmi020202 IS '非制造业PMI:新订单指数:分行业/服务业';
COMMENT ON COLUMN cn_pmi.pmi020300 IS '非制造业PMI:投入品价格指数';
COMMENT ON COLUMN cn_pmi.pmi020301 IS '非制造业PMI:投入品价格指数:分行业/建筑业';
COMMENT ON COLUMN cn_pmi.pmi020302 IS '非制造业PMI:投入品价格指数:分行业/服务业';
COMMENT ON COLUMN cn_pmi.pmi020400 IS '非制造业PMI:销售价格指数';
COMMENT ON COLUMN cn_pmi.pmi020401 IS '非制造业PMI:销售价格指数:分行业/建筑业';
COMMENT ON COLUMN cn_pmi.pmi020402 IS '非制造业PMI:销售价格指数:分行业/服务业';
COMMENT ON COLUMN cn_pmi.pmi020500 IS '非制造业PMI:从业人员指数';
COMMENT ON COLUMN cn_pmi.pmi020501 IS '非制造业PMI:从业人员指数:分行业/建筑业';
COMMENT ON COLUMN cn_pmi.pmi020502 IS '非制造业PMI:从业人员指数:分行业/服务业';
COMMENT ON COLUMN cn_pmi.pmi020600 IS '非制造业PMI:业务活动预期指数';
COMMENT ON COLUMN cn_pmi.pmi020601 IS '非制造业PMI:业务活动预期指数:分行业/建筑业';
COMMENT ON COLUMN cn_pmi.pmi020602 IS '非制造业PMI:业务活动预期指数:分行业/服务业';
COMMENT ON COLUMN cn_pmi.pmi020700 IS '非制造业PMI:新出口订单';
COMMENT ON COLUMN cn_pmi.pmi020800 IS '非制造业PMI:在手订单';
COMMENT ON COLUMN cn_pmi.pmi020900 IS '非制造业PMI:存货';
COMMENT ON COLUMN cn_pmi.pmi021000 IS '非制造业PMI:供应商配送时间';
COMMENT ON COLUMN cn_pmi.pmi030000 IS '中国综合PMI:产出指数';

-- 添加索引
CREATE INDEX idx_cn_pmi_month ON cn_pmi(month);


-- 名称	类型	默认显示	描述
-- month	str	N	月份YYYYMM
-- pmi010000	float	N	制造业PMI
-- pmi010100	float	N	制造业PMI:企业规模/大型企业
-- pmi010200	float	N	制造业PMI:企业规模/中型企业
-- pmi010300	float	N	制造业PMI:企业规模/小型企业
-- pmi010400	float	N	制造业PMI:构成指数/生产指数
-- pmi010401	float	N	制造业PMI:构成指数/生产指数:企业规模/大型企业
-- pmi010402	float	N	制造业PMI:构成指数/生产指数:企业规模/中型企业
-- pmi010403	float	N	制造业PMI:构成指数/生产指数:企业规模/小型企业
-- pmi010500	float	N	制造业PMI:构成指数/新订单指数
-- pmi010501	float	N	制造业PMI:构成指数/新订单指数:企业规模/大型企业
-- pmi010502	float	N	制造业PMI:构成指数/新订单指数:企业规模/中型企业
-- pmi010503	float	N	制造业PMI:构成指数/新订单指数:企业规模/小型企业
-- pmi010600	float	N	制造业PMI:构成指数/供应商配送时间指数
-- pmi010601	float	N	制造业PMI:构成指数/供应商配送时间指数:企业规模/大型企业
-- pmi010602	float	N	制造业PMI:构成指数/供应商配送时间指数:企业规模/中型企业
-- pmi010603	float	N	制造业PMI:构成指数/供应商配送时间指数:企业规模/小型企业
-- pmi010700	float	N	制造业PMI:构成指数/原材料库存指数
-- pmi010701	float	N	制造业PMI:构成指数/原材料库存指数:企业规模/大型企业
-- pmi010702	float	N	制造业PMI:构成指数/原材料库存指数:企业规模/中型企业
-- pmi010703	float	N	制造业PMI:构成指数/原材料库存指数:企业规模/小型企业
-- pmi010800	float	N	制造业PMI:构成指数/从业人员指数
-- pmi010801	float	N	制造业PMI:构成指数/从业人员指数:企业规模/大型企业
-- pmi010802	float	N	制造业PMI:构成指数/从业人员指数:企业规模/中型企业
-- pmi010803	float	N	制造业PMI:构成指数/从业人员指数:企业规模/小型企业
-- pmi010900	float	N	制造业PMI:其他/新出口订单
-- pmi011000	float	N	制造业PMI:其他/进口
-- pmi011100	float	N	制造业PMI:其他/采购量
-- pmi011200	float	N	制造业PMI:其他/主要原材料购进价格
-- pmi011300	float	N	制造业PMI:其他/出厂价格
-- pmi011400	float	N	制造业PMI:其他/产成品库存
-- pmi011500	float	N	制造业PMI:其他/在手订单
-- pmi011600	float	N	制造业PMI:其他/生产经营活动预期
-- pmi011700	float	N	制造业PMI:分行业/装备制造业
-- pmi011800	float	N	制造业PMI:分行业/高技术制造业
-- pmi011900	float	N	制造业PMI:分行业/基础原材料制造业
-- pmi012000	float	N	制造业PMI:分行业/消费品制造业
-- pmi020100	float	N	非制造业PMI:商务活动
-- pmi020101	float	N	非制造业PMI:商务活动:分行业/建筑业
-- pmi020102	float	N	非制造业PMI:商务活动:分行业/服务业业
-- pmi020200	float	N	非制造业PMI:新订单指数
-- pmi020201	float	N	非制造业PMI:新订单指数:分行业/建筑业
-- pmi020202	float	N	非制造业PMI:新订单指数:分行业/服务业
-- pmi020300	float	N	非制造业PMI:投入品价格指数
-- pmi020301	float	N	非制造业PMI:投入品价格指数:分行业/建筑业
-- pmi020302	float	N	非制造业PMI:投入品价格指数:分行业/服务业
-- pmi020400	float	N	非制造业PMI:销售价格指数
-- pmi020401	float	N	非制造业PMI:销售价格指数:分行业/建筑业
-- pmi020402	float	N	非制造业PMI:销售价格指数:分行业/服务业
-- pmi020500	float	N	非制造业PMI:从业人员指数
-- pmi020501	float	N	非制造业PMI:从业人员指数:分行业/建筑业
-- pmi020502	float	N	非制造业PMI:从业人员指数:分行业/服务业
-- pmi020600	float	N	非制造业PMI:业务活动预期指数
-- pmi020601	float	N	非制造业PMI:业务活动预期指数:分行业/建筑业
-- pmi020602	float	N	非制造业PMI:业务活动预期指数:分行业/服务业
-- pmi020700	float	N	非制造业PMI:新出口订单
-- pmi020800	float	N	非制造业PMI:在手订单
-- pmi020900	float	N	非制造业PMI:存货
-- pmi021000	float	N	非制造业PMI:供应商配送时间
-- pmi030000	float	N	中国综合PMI:产出指数