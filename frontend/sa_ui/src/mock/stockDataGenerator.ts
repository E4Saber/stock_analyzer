// src/mock/stockDataGenerator.ts
import moment from 'moment';
import { StockData, HotStock } from '../types/market';
import { IndicatorType } from '../components/charts/config/chartConfig';

/**
 * 生成随机数
 * @param min 最小值
 * @param max 最大值
 * @param precision 精度（小数位数）
 */
function randomNumber(min: number, max: number, precision: number = 0): number {
  const value = Math.random() * (max - min) + min;
  return Number(value.toFixed(precision));
}

/**
 * 生成测试股票数据
 * @param code 股票代码
 * @param name 股票名称
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
 * 生成热门股票列表数据
 * @param count 数量
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
 * 生成指数数据列表
 */
export function generateIndexDataList() {
  return [
    {
      code: '000001.SH',
      name: '上证指数',
      current: randomNumber(3000, 3500, 2),
      change: randomNumber(-30, 30, 2),
      change_pct: randomNumber(-2, 2, 2),
    },
    {
      code: '399001.SZ',
      name: '深证成指',
      current: randomNumber(11000, 12000, 2),
      change: randomNumber(-100, 100, 2),
      change_pct: randomNumber(-2, 2, 2),
    },
    {
      code: '399006.SZ',
      name: '创业板指',
      current: randomNumber(2000, 2500, 2),
      change: randomNumber(-20, 20, 2),
      change_pct: randomNumber(-2, 2, 2),
    },
    {
      code: '000300.SH',
      name: '沪深300',
      current: randomNumber(4000, 4500, 2),
      change: randomNumber(-40, 40, 2),
      change_pct: randomNumber(-2, 2, 2),
    }
  ];
}

/**
 * 生成行业板块数据
 */
export function generateSectorDataList(count: number = 10) {
  const sectors = [
    '计算机软件', '电子设备', '医药制造', '银行', '保险', '证券', 
    '房地产', '汽车', '新能源', '食品饮料', '家电', '通信', 
    '机械设备', '建筑建材', '钢铁', '化工', '煤炭', '石油石化'
  ];
  
  return sectors.slice(0, count).map(name => ({
    name,
    code: `BK${randomNumber(100000, 999999)}`,
    change_pct: randomNumber(-5, 5, 2),
    avg_volume: randomNumber(10000000, 1000000000),
  }));
}

/**
 * 生成K线图数据
 * @param days 天数
 * @param startPrice 起始价格
 * @param volatility 波动率
 */
export function generateKlineData(days: number, startPrice: number, volatility: number = 0.02) {
  const data = [];
  let currentDate = moment().subtract(days, 'days');
  let price = startPrice;
  
  for (let i = 0; i < days; i++) {
    // 跳过周末
    while (currentDate.day() === 0 || currentDate.day() === 6) {
      currentDate = currentDate.add(1, 'day');
    }
    
    const dateStr = currentDate.format('YYYY-MM-DD');
    
    // 计算价格波动
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
 * 生成技术指标数据
 * @param klineData K线数据
 * @param indicatorType 指标类型
 */
export function generateIndicatorData(klineData: any[], indicatorType: IndicatorType) {
  if (indicatorType === 'MACD') {
    return {
      DIF: klineData.map((item, index) => {
        const value = randomNumber(-2, 2, 2);
        return [item.date, value];
      }),
      DEA: klineData.map((item, index) => {
        const value = randomNumber(-1.5, 1.5, 2);
        return [item.date, value];
      }),
      MACD: klineData.map((item, index) => {
        const value = randomNumber(-1, 1, 2);
        return [item.date, value];
      }),
      HIST: klineData.map((item, index) => {
        const value = randomNumber(-1, 1, 2);
        return [item.date, value];
      })
    };
  } else if (indicatorType === 'KDJ') {
    return {
      K: klineData.map((item, index) => {
        const value = randomNumber(20, 80, 2);
        return [item.date, value];
      }),
      D: klineData.map((item, index) => {
        const value = randomNumber(20, 80, 2);
        return [item.date, value];
      }),
      J: klineData.map((item, index) => {
        const value = randomNumber(0, 100, 2);
        return [item.date, value];
      })
    };
  } else if (indicatorType === 'RSI') {
    return {
      RSI6: klineData.map((item, index) => {
        const value = randomNumber(20, 80, 2);
        return [item.date, value];
      }),
      RSI12: klineData.map((item, index) => {
        const value = randomNumber(30, 70, 2);
        return [item.date, value];
      }),
      RSI24: klineData.map((item, index) => {
        const value = randomNumber(40, 60, 2);
        return [item.date, value];
      })
    };
  } else if (indicatorType === 'VOL') {
    return {
      MA5: klineData.map((item, index) => {
        const value = randomNumber(10000000, 30000000);
        return [item.date, value];
      }),
      MA10: klineData.map((item, index) => {
        const value = randomNumber(10000000, 30000000);
        return [item.date, value];
      })
    };
  } else if (indicatorType === 'MA') {
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
  } else if (indicatorType === 'BOLL') {
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
  
  // 默认返回空对象
  return {};
}

/**
 * 计算移动平均线
 * @param days 天数
 * @param data 数据
 * @param index 索引
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
 * 生成财务数据
 * @param years 年数
 */
export function generateFinancialData(years: number = 5) {
  const currentYear = moment().year();
  const data = [];
  
  for (let i = 0; i < years; i++) {
    const year = currentYear - i;
    const yearGrowth = Math.max(0.9, 1 - i * 0.05); // 假设越早的年份增长越慢
    
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

/**
 * 模拟API响应延迟
 * @param data 返回数据
 * @param delay 延迟时间（毫秒）
 */
export function mockApiResponse<T>(data: T, delay: number = 500): Promise<T> {
  return new Promise(resolve => {
    setTimeout(() => {
      resolve(data);
    }, delay);
  });
}