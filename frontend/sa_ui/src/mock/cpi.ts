// src/mockData/indicators/cpi.ts
/**
 * CPI指标模拟数据
 */
import { DataPoint, IndicatorDetailType, CompositionItem, TimeRangeType } from '../features/economicmonitor/types/indicator';

// 生成过去24个月的CPI数据
const generateCPIData = (): DataPoint[] => {
  const baseDate = new Date(2023, 3, 1); // 2023年4月
  const result: DataPoint[] = [];
  
  // 模拟基准值和波动范围
  const baseValue = 2.5; // 基准CPI值
  const volatility = 0.8; // 波动范围
  
  // 生成过去24个月的数据
  for (let i = 0; i < 24; i++) {
    const currentDate = new Date(baseDate);
    currentDate.setMonth(baseDate.getMonth() - i);
    
    // 基于时间生成一些波动，让数据看起来更真实
    const timeEffect = Math.sin(i / 3) * volatility;
    const randomEffect = (Math.random() - 0.5) * volatility * 0.5;
    
    const value = baseValue + timeEffect + randomEffect;
    
    // 计算同比和环比变化
    // 为简化，这里用随机值模拟
    const yoy = i > 11 ? ((value / result[i - 12].value) - 1) * 100 : (Math.random() * 2 - 0.5) * 3;
    const mom = i > 0 ? ((value / result[i - 1].value) - 1) * 100 : (Math.random() * 2 - 0.5) * 0.8;
    
    result.unshift({
      date: `${currentDate.getFullYear()}-${String(currentDate.getMonth() + 1).padStart(2, '0')}`,
      value: value,
      yoy: yoy,
      mom: mom
    });
  }
  
  return result;
};

// CPI指标详细数据
export const cpiData: IndicatorDetailType = {
  id: 'cpi',
  name: 'CPI (消费者价格指数)',
  description: 'CPI是衡量一篮子消费商品和服务价格随时间变化的指标，是计量通货膨胀的重要指标。',
  category: 'price',
  region: 'us',
  frequency: '月度',
  unit: '%',
  source: '美国劳工统计局',
  sourceUrl: 'https://www.bls.gov/cpi/',
  updateTime: '2023-04-15',
  current: 2.8,
  previous: 3.1,
  expected: 2.9,
  yoy: -0.3,
  mom: -0.2,
  max: 4.1,
  min: 1.9,
  avg: 2.7,
  value: 2.8,
  change: -0.3,
  changeType: 'decrease',
  trend: 'down', // 'up' or 'down'
  status: 'normal', // 'normal', 'warning', 'alert'
  chartData: generateCPIData(),
  
  // 表格数据(简化版，实际应用中可能需要更详细的数据)
  tableData: generateCPIData(),
  
  // CPI 构成数据
  composition: [
    { name: '食品', value: 25.3 },
    { name: '住房', value: 33.8 },
    { name: '交通', value: 17.1 },
    { name: '医疗', value: 8.7 },
    { name: '教育', value: 6.2 },
    { name: '其他', value: 8.9 }
  ]
};

// 获取CPI数据的函数
export const getCPIData = (timeRange: TimeRangeType = '1y'): IndicatorDetailType => {
  // 根据时间范围筛选数据
  // 这里简化处理，实际应用中可能需要更复杂的逻辑
  const monthsMap: Record<TimeRangeType, number> = {
    '1m': 1,
    '3m': 3,
    '6m': 6,
    '1y': 12,
    '3y': 36,
    '5y': 60
  };
  
  const months = monthsMap[timeRange] || 12;
  
  // 复制一份数据，避免修改原始数据
  const result = { ...cpiData };
  result.chartData = result.chartData.slice(-months);
  result.tableData = result.tableData.slice(-months);
  
  return result;
};