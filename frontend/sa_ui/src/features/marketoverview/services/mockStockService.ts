// src/services/mock/mockStockService.ts
import moment from 'moment';
import { StockData, ShareholderData, FinancialIndicator, MarketNews } from '../types/market';
import { IndicatorType } from '../../stockinsight/components/widgets/config/chartConfig';
import { generateKlineData, generateIndicatorData } from './mockData';

/**
 * Get stock detail (mock)
 * @param code Stock code
 */
export const getStockDetail = async (code: string) => {
  // Simulate delay
  await new Promise(resolve => setTimeout(resolve, 600));
  
  // Stock names and industries mapping
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
  
  // Generate stock basic data
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
    turnover_rate: Math.random() * 5 + 0.5
  };
  
  // Generate related stocks
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
        turnover_rate: Math.random() * 5 + 0.5
      });
    }
  }
  
  // Take at most 5 related stocks
  relatedStocks = relatedStocks.slice(0, 5);
  
  // Generate shareholders data
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
    }
  ];
  
  // Generate financial data
  const currentYear = new Date().getFullYear();
  const financials: FinancialIndicator[] = [];
  
  for (let year = currentYear; year >= currentYear - 4; year--) {
    for (let quarter of ['Q4', 'Q3', 'Q2', 'Q1']) {
      // Skip quarters not yet reached in current year
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
      // Base values, smaller for earlier years to simulate growth
      const baseRevenue = Math.floor(Math.random() * 10000000000) + 5000000000;
      const growthFactor = Math.pow(1.15, 4 - yearIndex); // 15% annual growth
      const seasonalFactor = quarter === 'Q4' ? 1.3 : quarter === 'Q3' ? 1.1 : quarter === 'Q2' ? 0.9 : 0.7; // Seasonal factors
      
      financials.push({
        year: year.toString(),
        quarter: quarter,
        revenue: baseRevenue * growthFactor * seasonalFactor,
        netProfit: baseRevenue * growthFactor * seasonalFactor * (Math.random() * 0.1 + 0.15), // 15%-25% net margin
        grossMargin: Math.random() * 20 + 50, // 50%-70% gross margin
        netMargin: Math.random() * 10 + 15, // 15%-25% net margin
        roe: Math.random() * 10 + 15, // 15%-25% ROE
        eps: (Math.random() * 2 + 1) * growthFactor, // Random EPS growing over time
        debt_to_assets: Math.random() * 20 + 30 // 30%-50% debt to assets ratio
      });
    }
  }
  
  // Sort by year and quarter in descending order
  financials.sort((a, b) => {
    if (a.year !== b.year) {
      return parseInt(b.year) - parseInt(a.year); // Year descending
    }
    // Quarter descending: Q4, Q3, Q2, Q1
    const quarterValue = { 'Q4': 4, 'Q3': 3, 'Q2': 2, 'Q1': 1 };
    return quarterValue[b.quarter as 'Q4' | 'Q3' | 'Q2' | 'Q1'] - quarterValue[a.quarter as 'Q4' | 'Q3' | 'Q2' | 'Q1'];
  });
  
  // Generate news data
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
 * Get stock K-line data (mock)
 * @param stockCode Stock code
 * @param period K-line period: 1d, 5d, 1mo, 3mo, 6mo, 1y
 * @param chartType Chart type: line, candle, bar
 */
export const getStockKline = async (
  stockCode: string,
  period: string = '1d',
  chartType: string = 'candlestick'
) => {
  // Simulate delay
  await new Promise(resolve => setTimeout(resolve, 500));
  
  // Determine days based on period
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
  
  // Generate random starting price
  const startPrice = parseFloat(stockCode) % 1000 + 50;
  
  // Generate K-line data
  const klineData = generateKlineData(days, startPrice);
  
  return {
    data: klineData
  };
};

/**
 * Get stock technical indicators (mock)
 * @param stockCode Stock code
 * @param period Period
 * @param indicators Indicator types array
 */
export const getStockIndicators = async (
  stockCode: string,
  period: string,
  indicators: IndicatorType[]
) => {
  // First get K-line data
  const klineResponse = await getStockKline(stockCode, period);
  const klineData = klineResponse.data;
  
  // Generate indicators data
  const indicatorData: Record<string, any> = {};
  
  for (const indicator of indicators) {
    indicatorData[indicator] = generateIndicatorData(klineData, indicator);
  }
  
  return {
    data: indicatorData
  };
};

/**
 * Get stock financial data (mock)
 * @param stockCode Stock code
 */
export const getStockFinancial = async (stockCode: string) => {
  // Already included in getStockDetail, but kept for API compatibility
  const response = await getStockDetail(stockCode);
  return {
    data: response.financials
  };
};