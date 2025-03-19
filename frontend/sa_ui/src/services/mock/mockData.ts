// src/services/mock/mockData.ts
import moment from 'moment';
import { StockData, IndexData, SectorData, HotStock, ShareholderData, 
         FinancialIndicator, MarketNews } from '../../types/market';
import { IndicatorType } from '../../components/charts/config/chartConfig';

/**
 * Generate random number
 * @param min Minimum value
 * @param max Maximum value
 * @param precision Decimal precision
 */
export function randomNumber(min: number, max: number, precision: number = 0): number {
  const value = Math.random() * (max - min) + min;
  return Number(value.toFixed(precision));
}

/**
 * Generate test stock data
 * @param code Stock code
 * @param name Stock name
 */
export function generateStockData(code: string, name: string): StockData {
  const current = randomNumber(10, 200, 2);
  const change = randomNumber(-10, 10, 2);
  const changePercent = randomNumber(-5, 5, 2);
  
  return {
    code,
    name,
    current,
    change,
    change_percent: changePercent,
    open: current - randomNumber(-5, 5, 2),
    high: current + randomNumber(1, 10, 2),
    low: current - randomNumber(1, 10, 2),
    volume: randomNumber(1000000, 50000000),
    amount: randomNumber(10000000, 500000000),
    market_cap: randomNumber(1000000000, 1000000000000),
    pe: randomNumber(10, 50, 2),
    pb: randomNumber(1, 10, 2),
    industry: '计算机软件',
    turnover_rate: randomNumber(1, 5, 2),
    dividend: randomNumber(0, 3, 2),
    update_time: moment().format('YYYY-MM-DD HH:mm:ss')
  };
}

/**
 * Generate hot stocks list
 * @param count Number of stocks to generate
 */
export function generateHotStockList(count: number = 10): HotStock[] {
  const stockNamePrefixes = ['中国', '国际', '科技', '金融', '新能源', '互联网', '医疗', '电子', '机械', '地产'];
  const stockNameSuffixes = ['科技', '控股', '集团', '股份', '信息', '技术', '电子', '软件', '通信', '制造'];
  
  return Array(count).fill(0).map((_, index) => {
    const code = `60${randomNumber(1000, 9999)}`;
    const prefix = stockNamePrefixes[index % stockNamePrefixes.length];
    const suffix = stockNameSuffixes[randomNumber(0, stockNameSuffixes.length - 1)];
    const name = `${prefix}${suffix}`;
    
    return {
      code,
      name,
      price: randomNumber(10, 200, 2),
      change_pct: randomNumber(-5, 5, 2),
      volume: randomNumber(1000000, 50000000),
      amount: randomNumber(10000000, 500000000),
      turnover_rate: randomNumber(1, 5, 2)
    };
  });
}

/**
 * Generate index data list
 */
export function generateIndexDataList(): IndexData[] {
  return [
    {
      code: '000001.SH',
      name: '上证指数',
      current: randomNumber(3000, 3500, 2),
      change: randomNumber(-30, 30, 2),
      change_pct: randomNumber(-2, 2, 2),
      ts_code: '000001.SH'
    },
    {
      code: '399001.SZ',
      name: '深证成指',
      current: randomNumber(11000, 12000, 2),
      change: randomNumber(-100, 100, 2),
      change_pct: randomNumber(-2, 2, 2),
      ts_code: '399001.SZ'
    },
    {
      code: '399006.SZ',
      name: '创业板指',
      current: randomNumber(2000, 2500, 2),
      change: randomNumber(-20, 20, 2),
      change_pct: randomNumber(-2, 2, 2),
      ts_code: '399006.SZ'
    },
    {
      code: '000300.SH',
      name: '沪深300',
      current: randomNumber(4000, 4500, 2),
      change: randomNumber(-40, 40, 2),
      change_pct: randomNumber(-2, 2, 2),
      ts_code: '000300.SH'
    },
    {
      code: '.HSI',
      name: '恒生指数',
      current: randomNumber(17500, 18500, 2),
      change: randomNumber(-150, 150, 2),
      change_pct: randomNumber(-2, 2, 2),
      ts_code: '.HSI'
    }
  ];
}

/**
 * Generate sector data
 * @param count Number of sectors to generate
 */
export function generateSectorDataList(count: number = 10): SectorData[] {
  const sectors = [
    '计算机软件', '电子设备', '医药制造', '银行', '保险', '证券', 
    '房地产', '汽车', '新能源', '食品饮料', '家电', '通信', 
    '机械设备', '建筑建材', '钢铁', '化工', '煤炭', '石油石化'
  ];
  
  return sectors.slice(0, count).map(name => ({
    name,
    change_pct: randomNumber(-5, 5, 2),
    avg_volume: randomNumber(10000000, 1000000000),
  }));
}

/**
 * Generate K-line data
 * @param days Number of days
 * @param startPrice Starting price
 * @param volatility Volatility
 */
export function generateKlineData(days: number, startPrice: number, volatility: number = 0.02) {
  const data = [];
  let currentDate = moment().subtract(days, 'days');
  let price = startPrice;
  
  for (let i = 0; i < days; i++) {
    // Skip weekends
    while (currentDate.day() === 0 || currentDate.day() === 6) {
      currentDate = currentDate.add(1, 'day');
    }
    
    const dateStr = currentDate.format('YYYY-MM-DD');
    
    // Calculate price changes
    const changePercent = randomNumber(-volatility * 100, volatility * 100, 2) / 100;
    const open = price;
    const close = Number((price * (1 + changePercent)).toFixed(2));
    const high = Number((Math.max(open, close) * (1 + randomNumber(0, 0.01, 3))).toFixed(2));
    const low = Number((Math.min(open, close) * (1 - randomNumber(0, 0.01, 3))).toFixed(2));
    const volume = randomNumber(1000000, 50000000);
    
    data.push({
      date: dateStr,
      open,
      close,
      high,
      low,
      volume,
      amount: volume * close
    });
    
    price = close;
    currentDate = currentDate.add(1, 'day');
  }
  
  return data;
}

/**
 * Generate technical indicator data
 * @param klineData K-line data
 * @param indicatorType Indicator type
 */
export function generateIndicatorData(klineData: any[], indicatorType: IndicatorType) {
  switch (indicatorType) {
    case 'MACD':
      return generateMACDData(klineData);
    case 'KDJ':
      return generateKDJData(klineData);
    case 'RSI':
      return generateRSIData(klineData);
    case 'VOL':
      return generateVOLData(klineData);
    case 'MA':
      return generateMAData(klineData);
    case 'BOLL':
      return generateBOLLData(klineData);
    default:
      return {};
  }
}

// Helper functions for each indicator type
function generateMACDData(klineData: any[]) {
  return {
    DIF: klineData.map((item) => {
      const value = randomNumber(-2, 2, 2);
      return [item.date, value];
    }),
    DEA: klineData.map((item) => {
      const value = randomNumber(-1.5, 1.5, 2);
      return [item.date, value];
    }),
    MACD: klineData.map((item) => {
      const value = randomNumber(-1, 1, 2);
      return [item.date, value];
    }),
    HIST: klineData.map((item) => {
      const value = randomNumber(-1, 1, 2);
      return [item.date, value];
    })
  };
}

function generateKDJData(klineData: any[]) {
  return {
    K: klineData.map((item) => {
      const value = randomNumber(20, 80, 2);
      return [item.date, value];
    }),
    D: klineData.map((item) => {
      const value = randomNumber(20, 80, 2);
      return [item.date, value];
    }),
    J: klineData.map((item) => {
      const value = randomNumber(0, 100, 2);
      return [item.date, value];
    })
  };
}

function generateRSIData(klineData: any[]) {
  return {
    RSI6: klineData.map((item) => {
      const value = randomNumber(20, 80, 2);
      return [item.date, value];
    }),
    RSI12: klineData.map((item) => {
      const value = randomNumber(30, 70, 2);
      return [item.date, value];
    }),
    RSI24: klineData.map((item) => {
      const value = randomNumber(40, 60, 2);
      return [item.date, value];
    })
  };
}

function generateVOLData(klineData: any[]) {
  return {
    MA5: klineData.map((item) => {
      const value = randomNumber(10000000, 30000000);
      return [item.date, value];
    }),
    MA10: klineData.map((item) => {
      const value = randomNumber(10000000, 30000000);
      return [item.date, value];
    })
  };
}

function generateMAData(klineData: any[]) {
  return {
    MA5: klineData.map((item, index) => {
      return [item.date, calculateMA(5, klineData, index)];
    }),
    MA10: klineData.map((item, index) => {
      return [item.date, calculateMA(10, klineData, index)];
    }),
    MA20: klineData.map((item, index) => {
      return [item.date, calculateMA(20, klineData, index)];
    })
  };
}

function generateBOLLData(klineData: any[]) {
  const ma20 = klineData.map((item, index) => calculateMA(20, klineData, index));
  
  return {
    MID: klineData.map((item, index) => {
      return [item.date, ma20[index]];
    }),
    UPPER: klineData.map((item, index) => {
      const mid = ma20[index];
      return [item.date, mid + randomNumber(2, 5, 2)];
    }),
    LOWER: klineData.map((item, index) => {
      const mid = ma20[index];
      return [item.date, mid - randomNumber(2, 5, 2)];
    })
  };
}

/**
 * Calculate moving average
 * @param days Number of days
 * @param data Data array
 * @param index Current index
 */
function calculateMA(days: number, data: any[], index: number) {
  if (index < days - 1) {
    return '-';
  }
  
  let sum = 0;
  for (let i = 0; i < days; i++) {
    sum += data[index - i].close;
  }
  
  return Number((sum / days).toFixed(2));
}

/**
 * Generate financial data
 * @param years Number of years
 */
export function generateFinancialData(years: number = 5) {
  const currentYear = moment().year();
  const data = [];
  
  for (let i = 0; i < years; i++) {
    const year = currentYear - i;
    const yearGrowth = Math.max(0.9, 1 - i * 0.05); // Assume slower growth in earlier years
    
    data.push({
      year: `${year}`,
      revenue: randomNumber(1000000000, 10000000000) * yearGrowth,
      profit: randomNumber(100000000, 1000000000) * yearGrowth,
      eps: randomNumber(0.5, 2, 2) * yearGrowth,
      roe: randomNumber(5, 20, 2) * yearGrowth
    });
  }
  
  return data;
}