// 资金特征分析模拟数据
export const mockFundQualityData = {
    stockCode: '600519',
    stockName: '贵州茅台',
    
    // 假设60天的数据
    dates: Array.from({ length: 60 }, (_, i) => {
      const date = new Date(2025, 1, 1);
      date.setDate(date.getDate() + i);
      return date.toISOString().slice(0, 10);
    }),
    
    // 大单占比 (%)
    largeOrderRatio: [
      // 第一段埋伏期 (0-9)
      42, 45, 47, 51, 49, 52, 48, 50, 54, 51,
      // 非埋伏期 (10-19)
      32, 35, 30, 33, 36, 31, 28, 34, 32, 35,
      // 第二段埋伏期 (20-34)
      38, 42, 45, 49, 52, 55, 58, 61, 57, 53, 56, 59, 62, 58, 55,
      // 股价上涨期 (资金流出) (35-44)
      45, 42, 38, 40, 37, 35, 39, 36, 33, 37,
      // 第三段埋伏期 (45-59)
      40, 43, 46, 49, 52, 56, 53, 57, 60, 58, 55, 59, 62, 58, 61
    ],
    
    // 大单买卖比
    largeOrderBuySellRatio: [
      // 第一段埋伏期 (0-9)
      1.3, 1.4, 1.5, 1.6, 1.5, 1.7, 1.4, 1.6, 1.8, 1.6,
      // 非埋伏期 (10-19)
      0.9, 1.1, 0.8, 0.9, 1.2, 0.7, 0.6, 1.0, 0.9, 1.1,
      // 第二段埋伏期 (20-34)
      1.2, 1.4, 1.5, 1.7, 1.9, 2.0, 2.3, 2.5, 2.2, 1.8, 2.1, 2.4, 2.6, 2.3, 2.0,
      // 股价上涨期 (35-44)
      1.2, 0.9, 0.7, 0.8, 0.6, 0.5, 0.9, 0.7, 0.6, 0.8,
      // 第三段埋伏期 (45-59)
      1.3, 1.5, 1.8, 1.7, 2.0, 2.3, 2.1, 2.4, 2.7, 2.5, 2.2, 2.5, 2.8, 2.6, 2.9
    ],
    
    // 主动性买盘比例 (%)
    activeBuyRatio: [
      // 第一段埋伏期
      72, 75, 73, 78, 76, 79, 74, 77, 81, 78,
      // 非埋伏期
      65, 68, 62, 64, 69, 61, 58, 67, 63, 66,
      // 第二段埋伏期
      70, 73, 75, 78, 81, 83, 86, 88, 84, 82, 85, 87, 89, 85, 83,
      // 股价上涨期
      75, 72, 67, 69, 64, 62, 68, 65, 63, 66,
      // 第三段埋伏期
      71, 74, 77, 76, 79, 82, 80, 84, 87, 85, 82, 86, 89, 85, 88
    ],
    
    // 资金流入加速度 (近5日vs前5日增长率, %)
    inflowAcceleration: [
      // 第一段埋伏期
      10, 15, 18, 22, 25, 20, 24, 28, 25, 30,
      // 非埋伏期
      -5, 8, -12, -8, 5, -15, -20, 0, -10, 5,
      // 第二段埋伏期
      12, 18, 22, 28, 35, 40, 45, 50, 42, 38, 44, 48, 53, 45, 40,
      // 股价上涨期
      15, 10, -8, -5, -15, -25, 0, -10, -18, -5,
      // 第三段埋伏期
      15, 20, 28, 25, 32, 40, 36, 42, 48, 45, 38, 44, 50, 42, 46
    ],
    
    // 主力类型判断 ('institutional'=机构, 'northbound'=北向资金, 'retail'=游资, 'unknown'=未知)
    fundStyle: [
      // 第一段埋伏期
      'institutional', 'institutional', 'institutional', 'institutional', 'institutional', 
      'institutional', 'institutional', 'institutional', 'institutional', 'institutional',
      // 非埋伏期
      'unknown', 'retail', 'unknown', 'unknown', 'retail', 
      'unknown', 'unknown', 'retail', 'unknown', 'retail',
      // 第二段埋伏期
      'institutional', 'institutional', 'institutional', 'institutional', 'institutional', 
      'northbound', 'northbound', 'northbound', 'northbound', 'northbound', 
      'northbound', 'northbound', 'northbound', 'northbound', 'northbound',
      // 股价上涨期
      'retail', 'retail', 'unknown', 'unknown', 'unknown', 
      'unknown', 'retail', 'unknown', 'unknown', 'retail',
      // 第三段埋伏期
      'institutional', 'institutional', 'institutional', 'northbound', 'northbound', 
      'northbound', 'northbound', 'northbound', 'northbound', 'northbound', 
      'northbound', 'northbound', 'northbound', 'northbound', 'northbound'
    ],
    
    // 主力埋伏时间段标记
    ambushPeriods: [
      { start: 0, end: 9, confidence: 'high', desc: '首次建仓期' },
      { start: 20, end: 34, confidence: 'very-high', desc: '主升前集中建仓' },
      { start: 45, end: 59, confidence: 'medium', desc: '二次建仓期' }
    ],
    
    // 市场指标
    marketCap: 22756.8, // 流通市值(亿元)
    indicators: {
      largeOrderAvgRatio: 48.2, // 平均大单占比(%)
      activeBuyAvgRatio: 77.3, // 平均主动买盘比例(%)
      mainFundType: 'institutional', // 主要资金类型(机构型)
      northboundInflowDays: 22 // 北向资金净流入天数
    }
  };