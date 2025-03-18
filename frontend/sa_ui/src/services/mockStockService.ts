// src/services/mockStockService.ts
import { 
  StockData, 
  ShareholderData, 
  FinancialIndicator, 
  MarketNews, 
  TimeSeriesDataPoint
} from '../types/market';
import { generateKlineData } from './mockMarketService';

/**
 * 获取股票详情
 * @param code 股票代码
 */
export const getStockDetail = async (code: string) => {
  // 模拟延迟
  await new Promise(resolve => setTimeout(resolve, 600));
  
  // 根据股票代码生成模拟数据
  const stockNames: Record<string, string> = {
    '600519': '贵州茅台',
    '601318': '中国平安',
    '000858': '五粮液',
    '000651': '格力电器',
    '600036': '招商银行',
    '601166': '兴业银行',
    '600276': '恒瑞医药',
    '000333': '美的集团',
    '600887': '伊利股份',
    '601398': '工商银行'
  };
  
  const industries: Record<string, string> = {
    '600519': '食品饮料',
    '601318': '保险',
    '000858': '食品饮料',
    '000651': '家用电器',
    '600036': '银行',
    '601166': '银行',
    '600276': '医药制造',
    '000333': '家用电器',
    '600887': '食品饮料',
    '601398': '银行'
  };
  
  const stockName = stockNames[code] || `股票${code}`;
  const industry = industries[code] || '其他行业';
  
  // 生成股票基本数据
  const price = parseFloat(code) % 1000 + 50;
  const changePercent = (Math.random() * 10 - 5).toFixed(2);
  const isPositive = parseFloat(changePercent) >= 0;
  const change = isPositive ? parseFloat((price * parseFloat(changePercent) / 100).toFixed(2)) : parseFloat((price * parseFloat(changePercent) / 100).toFixed(2));
  
  const stockData: StockData = {
    code: code,
    name: stockName,
    current: price,
    change: change,
    change_percent: parseFloat(changePercent),
    open: price - Math.random() * 5 + 2.5,
    high: price + Math.random() * 8,
    low: price - Math.random() * 8,
    volume: Math.floor(Math.random() * 50000000) + 5000000,
    amount: Math.floor(Math.random() * 500000000) + 50000000,
    market_cap: price * (Math.floor(Math.random() * 5000000000) + 500000000),
    pe: Math.random() * 50 + 10,
    pb: Math.random() * 10 + 1,
    industry: industry,
    turnover: Math.random() * 5 + 0.5
  };
  
  // 生成相关股票
  let relatedStocks: StockData[] = [];
  for (const [stockCode, stockName] of Object.entries(stockNames)) {
    if (stockCode !== code && industries[stockCode] === industry) {
      const relatedPrice = parseFloat(stockCode) % 1000 + 50;
      const relatedChangePercent = (Math.random() * 10 - 5).toFixed(2);
      const relatedIsPositive = parseFloat(relatedChangePercent) >= 0;
      const relatedChange = relatedIsPositive ? parseFloat((relatedPrice * parseFloat(relatedChangePercent) / 100).toFixed(2)) : parseFloat((relatedPrice * parseFloat(relatedChangePercent) / 100).toFixed(2));
      
      relatedStocks.push({
        code: stockCode,
        name: stockName,
        current: relatedPrice,
        change: relatedChange,
        change_percent: parseFloat(relatedChangePercent),
        open: relatedPrice - Math.random() * 5 + 2.5,
        high: relatedPrice + Math.random() * 8,
        low: relatedPrice - Math.random() * 8,
        volume: Math.floor(Math.random() * 50000000) + 5000000,
        amount: Math.floor(Math.random() * 500000000) + 50000000,
        market_cap: relatedPrice * (Math.floor(Math.random() * 5000000000) + 500000000),
        pe: Math.random() * 50 + 10,
        pb: Math.random() * 10 + 1,
        industry: industries[stockCode],
        turnover: Math.random() * 5 + 0.5
      });
    }
  }
  
  // 最多取5个相关股票
  relatedStocks = relatedStocks.slice(0, 5);
  
  // 生成股东数据
  const shareholders: ShareholderData[] = [
    {
      name: `${stockName}集团有限公司`,
      shares: Math.floor(Math.random() * 1000000000) + 500000000,
      ratio: Math.random() * 30 + 20,
      change: Math.floor(Math.random() * 10000000) - 5000000,
      type: 'institution'
    },
    {
      name: '国家资产管理委员会',
      shares: Math.floor(Math.random() * 500000000) + 200000000,
      ratio: Math.random() * 15 + 10,
      change: 0,
      type: 'government'
    },
    {
      name: '香港中央结算有限公司',
      shares: Math.floor(Math.random() * 300000000) + 100000000,
      ratio: Math.random() * 10 + 5,
      change: Math.floor(Math.random() * 20000000) - 10000000,
      type: 'institution'
    },
    {
      name: '中国证券金融股份有限公司',
      shares: Math.floor(Math.random() * 200000000) + 50000000,
      ratio: Math.random() * 5 + 2,
      change: Math.floor(Math.random() * 5000000) - 2500000,
      type: 'institution'
    },
    {
      name: '中央汇金资产管理有限责任公司',
      shares: Math.floor(Math.random() * 150000000) + 50000000,
      ratio: Math.random() * 4 + 2,
      change: Math.floor(Math.random() * 8000000) - 4000000,
      type: 'institution'
    },
    {
      name: '张三',
      shares: Math.floor(Math.random() * 50000000) + 10000000,
      ratio: Math.random() * 2 + 0.5,
      change: Math.floor(Math.random() * 2000000) - 1000000,
      type: 'individual'
    },
    {
      name: '李四',
      shares: Math.floor(Math.random() * 40000000) + 10000000,
      ratio: Math.random() * 1.5 + 0.3,
      change: Math.floor(Math.random() * 1500000) - 750000,
      type: 'individual'
    },
    {
      name: '全国社保基金理事会',
      shares: Math.floor(Math.random() * 100000000) + 30000000,
      ratio: Math.random() * 3 + 1,
      change: Math.floor(Math.random() * 3000000) - 1500000,
      type: 'institution'
    },
    {
      name: '中国工商银行股份有限公司',
      shares: Math.floor(Math.random() * 80000000) + 20000000,
      ratio: Math.random() * 2.5 + 1,
      change: Math.floor(Math.random() * 2500000) - 1250000,
      type: 'institution'
    },
    {
      name: '中国人寿保险股份有限公司',
      shares: Math.floor(Math.random() * 70000000) + 20000000,
      ratio: Math.random() * 2 + 1,
      change: Math.floor(Math.random() * 2000000) - 1000000,
      type: 'institution'
    }
  ];
  
  // 生成财务数据
  const currentYear = new Date().getFullYear();
  const financials: FinancialIndicator[] = [];
  
  for (let year = currentYear; year >= currentYear - 4; year--) {
    for (let quarter of ['Q4', 'Q3', 'Q2', 'Q1']) {
      // 跳过当前年份未到的季度
      if (year === currentYear) {
        const currentMonth = new Date().getMonth() + 1;
        if ((quarter === 'Q4' && currentMonth < 12) ||
            (quarter === 'Q3' && currentMonth < 9) ||
            (quarter === 'Q2' && currentMonth < 6) ||
            (quarter === 'Q1' && currentMonth < 3)) {
          continue;
        }
      }
      
      const yearIndex = currentYear - year;
      // 基础值，年份越早，数值越小，模拟公司增长
      const baseRevenue = Math.floor(Math.random() * 10000000000) + 5000000000;
      const growthFactor = Math.pow(1.15, 4 - yearIndex); // 每年增长15%
      const seasonalFactor = quarter === 'Q4' ? 1.3 : quarter === 'Q3' ? 1.1 : quarter === 'Q2' ? 0.9 : 0.7; // 季节性因素
      
      financials.push({
        year: year.toString(),
        quarter: quarter,
        revenue: baseRevenue * growthFactor * seasonalFactor,
        netProfit: baseRevenue * growthFactor * seasonalFactor * (Math.random() * 0.1 + 0.15), // 15%-25%的净利率
        grossMargin: Math.random() * 20 + 50, // 50%-70%的毛利率
        netMargin: Math.random() * 10 + 15, // 15%-25%的净利率
        roe: Math.random() * 10 + 15, // 15%-25%的ROE
        eps: (Math.random() * 2 + 1) * growthFactor, // 随机EPS，随时间增长
        debt_to_assets: Math.random() * 20 + 30 // 30%-50%的资产负债率
      });
    }
  }
  
  // 按年份和季度排序
  financials.sort((a, b) => {
    if (a.year !== b.year) {
      return parseInt(b.year) - parseInt(a.year); // 年份降序
    }
    // 季度降序：Q4, Q3, Q2, Q1
    const quarterValue = { 'Q4': 4, 'Q3': 3, 'Q2': 2, 'Q1': 1 };
    return quarterValue[b.quarter as 'Q4' | 'Q3' | 'Q2' | 'Q1'] - quarterValue[a.quarter as 'Q4' | 'Q3' | 'Q2' | 'Q1'];
  });
  
  // 生成新闻数据
  const news: MarketNews[] = [
    {
      id: 'news1',
      title: `${stockName}发布2025年第一季度财报，净利润同比增长21.3%`,
      source: '证券时报',
      time: '2025-03-18 08:45',
      url: '#'
    },
    {
      id: 'news2',
      title: `机构调研：${stockName}未来三年有望保持15%以上的增长`,
      source: '中国证券报',
      time: '2025-03-17 15:23',
      url: '#'
    },
    {
      id: 'news3',
      title: `${stockName}签署战略合作协议，拓展新业务领域`,
      source: '上海证券报',
      time: '2025-03-15 10:15',
      url: '#'
    },
    {
      id: 'news4',
      title: `分析师观点：看好${stockName}长期发展前景`,
      source: '财经日报',
      time: '2025-03-14 16:42',
      url: '#'
    },
    {
      id: 'news5',
      title: `${stockName}宣布增加研发投入，未来三年将投入50亿元`,
      source: '第一财经',
      time: '2025-03-12 09:30',
      url: '#'
    },
    {
      id: 'news6',
      title: `行业动态：${industry}行业政策利好，${stockName}有望受益`,
      source: '中国经济网',
      time: '2025-03-10 14:20',
      url: '#'
    },
    {
      id: 'news7',
      title: `${stockName}完成对某公司的收购，加速产业布局`,
      source: '21世纪经济报道',
      time: '2025-03-08 11:05',
      url: '#'
    },
    {
      id: 'news8',
      title: `${stockName}获多家券商推荐，目标价上调10%`,
      source: '证券日报',
      time: '2025-03-06 10:18',
      url: '#'
    }
  ];
  
  return {
    stock: stockData,
    relatedStocks,
    shareholders,
    financials,
    news
  };
};

/**
 * 获取股票K线数据
 * @param stockCode 股票代码
 * @param period K线周期: 1d, 5d, 1mo, 3mo, 6mo, 1y
 * @param chartType 图表类型: candlestick, line, bar
 */
export const getStockKline = async (
  stockCode: string,
  period: string = '1d',
  chartType: string = 'candlestick'
) => {
  // 模拟延迟
  await new Promise(resolve => setTimeout(resolve, 500));
  
  // 确定天数
  let days = 60;
  switch (period) {
    case '1m':
    case '5m':
    case '15m':
    case '30m':
    case '60m':
      days = 5;
      break;
    case '1d':
      days = 60;
      break;
    case '5d':
      days = 5;
      break;
    case '1wk':
    case 'week':
      days = 30;
      break;
    case '1mo':
    case 'month':
      days = 60;
      break;
    case '3mo':
      days = 90;
      break;
    case '6mo':
      days = 180;
      break;
    case '1y':
    case 'year':
      days = 365;
      break;
    case '5y':
      days = 365 * 5;
      break;
    default:
      days = 60;
  }
  
  // 生成随机起始价格
  const startPrice = parseFloat(stockCode) % 1000 + 50;
  
  // 生成K线数据
  const klineData = generateKlineData(days, startPrice);
  
  return {
    data: klineData
  };
};

/**
 * 获取股票技术指标
 * @param stockCode 股票代码
 * @param period 周期
 * @param indicators 指标类型数组
 */
export const getStockIndicators = async (
  stockCode: string,
  period: string,
  indicators: string[]
) => {
  // 首先获取K线数据
  const klineResponse = await getStockKline(stockCode, period);
  const klineData = klineResponse.data;
  
  // 生成各类指标数据
  const indicatorData: Record<string, any> = {};
  
  // MACD指标
  if (indicators.includes('MACD')) {
    indicatorData['MACD'] = {
      DIF: klineData.map((item: any, index: number) => {
        const value = Math.random() * 4 - 2;
        return [item.date, value];
      }),
      DEA: klineData.map((item: any, index: number) => {
        const value = Math.random() * 3 - 1.5;
        return [item.date, value];
      }),
      MACD: klineData.map((item: any, index: number) => {
        const value = Math.random() * 2 - 1;
        return [item.date, value];
      }),
      HIST: klineData.map((item: any, index: number) => {
        const value = Math.random() * 2 - 1;
        return [item.date, value];
      })
    };
  }
  
  // KDJ指标
  if (indicators.includes('KDJ')) {
    indicatorData['KDJ'] = {
      K: klineData.map((item: any, index: number) => {
        const value = Math.random() * 60 + 20;
        return [item.date, value];
      }),
      D: klineData.map((item: any, index: number) => {
        const value = Math.random() * 60 + 20;
        return [item.date, value];
      }),
      J: klineData.map((item: any, index: number) => {
        const value = Math.random() * 80 + 10;
        return [item.date, value];
      })
    };
  }
  
  // RSI指标
  if (indicators.includes('RSI')) {
    indicatorData['RSI'] = {
      RSI6: klineData.map((item: any, index: number) => {
        const value = Math.random() * 60 + 20;
        return [item.date, value];
      }),
      RSI12: klineData.map((item: any, index: number) => {
        const value = Math.random() * 50 + 25;
        return [item.date, value];
      }),
      RSI24: klineData.map((item: any, index: number) => {
        const value = Math.random() * 40 + 30;
        return [item.date, value];
      })
    };
  }
  
  // 布林带指标
  if (indicators.includes('BOLL')) {
    // 中轨（20日移动平均线）
    const mid = klineData.map((item: any, index: number) => {
      let ma20 = item.close;
      if (index >= 19) {
        let sum = 0;
        for (let i = 0; i < 20; i++) {
          sum += klineData[index - i].close;
        }
        ma20 = sum / 20;
      }
      return [item.date, ma20];
    });
    
    indicatorData['BOLL'] = {
      MID: mid,
      UPPER: mid.map((item: any, index: number) => {
        // 上轨 = 中轨 + 2 * 标准差
        const std = Math.random() * 5 + 3;
        return [item[0], item[1] + 2 * std];
      }),
      LOWER: mid.map((item: any, index: number) => {
        // 下轨 = 中轨 - 2 * 标准差
        const std = Math.random() * 5 + 3;
        return [item[0], item[1] - 2 * std];
      })
    };
  }
  
  // 移动平均线
  if (indicators.includes('MA')) {
    indicatorData['MA'] = {
      MA5: calculateMA(klineData, 5),
      MA10: calculateMA(klineData, 10),
      MA20: calculateMA(klineData, 20),
      MA30: calculateMA(klineData, 30),
      MA60: calculateMA(klineData, 60)
    };
  }
  
  // 成交量
  if (indicators.includes('VOL')) {
    indicatorData['VOL'] = {
      MA5: klineData.map((item: any, index: number) => {
        let ma5 = item.volume;
        if (index >= 4) {
          let sum = 0;
          for (let i = 0; i < 5; i++) {
            sum += klineData[index - i].volume;
          }
          ma5 = sum / 5;
        }
        return [item.date, ma5];
      }),
      MA10: klineData.map((item: any, index: number) => {
        let ma10 = item.volume;
        if (index >= 9) {
          let sum = 0;
          for (let i = 0; i < 10; i++) {
            sum += klineData[index - i].volume;
          }
          ma10 = sum / 10;
        }
        return [item.date, ma10];
      })
    };
  }
  
  return {
    data: indicatorData
  };
};

/**
 * 计算移动平均线
 * @param data K线数据
 * @param days 天数
 */
function calculateMA(data: any[], days: number) {
  return data.map((item, index) => {
    let ma = item.close;
    if (index >= days - 1) {
      let sum = 0;
      for (let i = 0; i < days; i++) {
        sum += data[index - i].close;
      }
      ma = sum / days;
    }
    return [item.date, ma];
  });
}

/**
 * 获取股票财务数据
 * @param stockCode 股票代码
 */
export const getStockFinancial = async (stockCode: string) => {
  // 已经在getStockDetail中包含了财务数据，这里只是为了兼容原有接口
  const response = await getStockDetail(stockCode);
  return {
    data: response.financials
  };
};