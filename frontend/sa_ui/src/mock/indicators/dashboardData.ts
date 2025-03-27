// src/mockData/dashboardData.ts
/**
 * 仪表盘数据模拟
 */
import { IndicatorType, TrendPoint, RegionType, CategoryType, ChangeType, IndicatorStatus } from '../../types/indicator';

// 生成迷你趋势图数据
const generateTrendData = (baseline: number, uptrend: boolean, volatility: number): TrendPoint[] => {
  const result: TrendPoint[] = [];
  let value = baseline;
  
  for (let i = 0; i < 12; i++) {
    // 上升或下降趋势
    const trend = uptrend ? 0.1 : -0.1;
    
    // 随机波动
    const randomFactor = (Math.random() - 0.5) * volatility;
    
    // 计算新值
    value = value + trend + randomFactor;
    
    // 确保值合理 (不会变成负数等)
    value = Math.max(0.1, value);
    
    result.push({
      x: i,
      y: value
    });
  }
  
  return result;
};

// 仪表盘指标数据
const dashboardData: IndicatorType[] = [
  // 美国经济指标
  {
    id: 'us-gdp',
    name: 'GDP增长率',
    value: 2.1,
    unit: '%',
    change: 0.3,
    changeType: 'increase',
    status: 'normal',
    trend: generateTrendData(1.8, true, 0.3),
    region: 'us',
    category: 'growth',
    updateTime: '2023-03-30'
  },
  {
    id: 'us-unemployment',
    name: '失业率',
    value: 3.8,
    unit: '%',
    change: -0.1,
    changeType: 'decrease',
    status: 'normal',
    trend: generateTrendData(4.0, false, 0.2),
    region: 'us',
    category: 'employment',
    updateTime: '2023-04-07'
  },
  {
    id: 'us-cpi',
    name: 'CPI通胀率',
    value: 2.8,
    unit: '%',
    change: -0.3,
    changeType: 'decrease',
    status: 'normal',
    trend: generateTrendData(3.1, false, 0.2),
    region: 'us',
    category: 'price',
    updateTime: '2023-04-12'
  },
  {
    id: 'us-retail',
    name: '零售销售月增长',
    value: 0.6,
    unit: '%',
    change: 0.4,
    changeType: 'increase',
    status: 'normal',
    trend: generateTrendData(0.2, true, 0.4),
    region: 'us',
    category: 'consumption',
    updateTime: '2023-04-14'
  },
  {
    id: 'us-fed-rate',
    name: '联邦基金利率',
    value: 5.25,
    unit: '%',
    change: 0,
    changeType: 'increase',
    status: 'normal',
    trend: generateTrendData(5.25, false, 0.01),
    region: 'us',
    category: 'finance',
    updateTime: '2023-03-22'
  },
  
  // 中国经济指标
  {
    id: 'cn-gdp',
    name: 'GDP同比增长',
    value: 4.9,
    unit: '%',
    change: -0.2,
    changeType: 'decrease',
    status: 'warning',
    trend: generateTrendData(5.1, false, 0.2),
    region: 'china',
    category: 'growth',
    updateTime: '2023-04-18'
  },
  {
    id: 'cn-pmi',
    name: '制造业PMI',
    value: 49.2,
    unit: '',
    change: -0.8,
    changeType: 'decrease',
    status: 'alert',
    trend: generateTrendData(50, false, 0.5),
    region: 'china',
    category: 'production',
    updateTime: '2023-03-31'
  },
  {
    id: 'cn-cpi',
    name: 'CPI同比',
    value: 1.8,
    unit: '%',
    change: 0.4,
    changeType: 'increase',
    status: 'normal',
    trend: generateTrendData(1.4, true, 0.3),
    region: 'china',
    category: 'price',
    updateTime: '2023-04-11'
  },
  {
    id: 'cn-retail',
    name: '社会消费品零售总额增长',
    value: 3.7,
    unit: '%',
    change: 1.2,
    changeType: 'increase',
    status: 'normal',
    trend: generateTrendData(2.5, true, 0.5),
    region: 'china',
    category: 'consumption',
    updateTime: '2023-04-18'
  },
  {
    id: 'cn-loan-rate',
    name: '1年期LPR',
    value: 3.45,
    unit: '%',
    change: -0.1,
    changeType: 'decrease',
    status: 'normal',
    trend: generateTrendData(3.55, false, 0.01),
    region: 'china',
    category: 'finance',
    updateTime: '2023-03-20'
  },
  
  // 中美交叉指标
  {
    id: 'cross-trade',
    name: '中美贸易总额',
    value: 682.3,
    unit: '十亿美元',
    change: -5.2,
    changeType: 'decrease',
    status: 'warning',
    trend: generateTrendData(700, false, 20),
    region: 'cross',
    category: 'trade',
    updateTime: '2023-04-13'
  },
  {
    id: 'cross-exchange',
    name: '人民币/美元汇率',
    value: 6.92,
    unit: '',
    change: 0.8,
    changeType: 'increase',
    status: 'warning',
    trend: generateTrendData(6.85, true, 0.05),
    region: 'cross',
    category: 'finance',
    updateTime: '2023-04-21'
  },
  {
    id: 'cross-china-treasury',
    name: '中国持有美债',
    value: 859.4,
    unit: '十亿美元',
    change: -12.6,
    changeType: 'decrease',
    status: 'warning',
    trend: generateTrendData(872, false, 5),
    region: 'cross',
    category: 'finance',
    updateTime: '2023-03-15'
  }
];

export default dashboardData;