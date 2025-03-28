// src/services/indicators.ts
/**
 * 指标数据服务
 * 提供获取指标数据的方法
 */

import { cpiData, getCPIData } from '../../../mock/cpi';
// 引入其他指标数据 (这里省略，实际应用中需要引入)
// import { gdpData, getGDPData } from '../mockData/indicators/gdp';
// import { unemploymentData, getUnemploymentData } from '../mockData/indicators/unemployment';
import { 
  IndicatorDetailType, 
  RelatedIndicatorType, 
  TimeRangeType, 
  DataPoint,
  TrendType,
  RegionType,
  CategoryType 
} from '../types/indicator';

// 指标ID到数据获取函数的映射
type IndicatorDataFunctionMap = {
  [key: string]: (timeRange?: TimeRangeType) => IndicatorDetailType;
};

const indicatorDataFunctions: IndicatorDataFunctionMap = {
  'cpi': getCPIData,
  'us-cpi': getCPIData,
  // 其他指标数据获取函数
  // 'gdp': getGDPData,
  // 'unemployment': getUnemploymentData,
};

/**
 * 获取指标数据
 * @param {string} indicatorId - 指标ID
 * @param {TimeRangeType} timeRange - 时间范围 ('1m', '3m', '6m', '1y', '3y', '5y')
 * @returns {IndicatorDetailType} 指标数据
 */
export const getIndicatorData = (indicatorId: string, timeRange: TimeRangeType = '1y'): IndicatorDetailType => {
  // 如果有对应的数据获取函数，调用它
  if (indicatorDataFunctions[indicatorId]) {
    return indicatorDataFunctions[indicatorId](timeRange);
  }
  
  // 否则返回模拟数据
  return getMockIndicatorData(indicatorId, timeRange);
};

/**
 * 获取相关指标数据
 * @param {string} indicatorId - 主指标ID
 * @returns {Array<RelatedIndicatorType>} 相关指标数据列表
 */
export const getRelatedIndicators = (indicatorId: string): RelatedIndicatorType[] => {
  // 这里简化处理，实际应用中可能需要更复杂的逻辑来确定相关指标
  const relatedIndicatorsMap: {[key: string]: RelatedIndicatorType[]} = {
    'cpi': [
      {
        id: 'ppi',
        name: 'PPI (生产者价格指数)',
        current: 2.1,
        unit: '%',
        trend: 'down',
        category: 'price',
        frequency: '月度',
        chartData: generateMockChartData(2.1, false, 0.3, 12)
      },
      {
        id: 'core-cpi',
        name: '核心CPI',
        current: 3.2,
        unit: '%',
        trend: 'down',
        category: 'price',
        frequency: '月度',
        chartData: generateMockChartData(3.2, false, 0.2, 12)
      },
      {
        id: 'pce',
        name: 'PCE通胀',
        current: 2.4,
        unit: '%',
        trend: 'down',
        category: 'price',
        frequency: '月度',
        chartData: generateMockChartData(2.4, false, 0.3, 12)
      }
    ],
    'us-cpi': [
      {
        id: 'ppi',
        name: 'PPI (生产者价格指数)',
        current: 2.1,
        unit: '%',
        trend: 'down',
        category: 'price',
        frequency: '月度',
        chartData: generateMockChartData(2.1, false, 0.3, 12)
      },
      {
        id: 'core-cpi',
        name: '核心CPI',
        current: 3.2,
        unit: '%',
        trend: 'down',
        category: 'price',
        frequency: '月度',
        chartData: generateMockChartData(3.2, false, 0.2, 12)
      },
      {
        id: 'pce',
        name: 'PCE通胀',
        current: 2.4,
        unit: '%',
        trend: 'down',
        category: 'price',
        frequency: '月度',
        chartData: generateMockChartData(2.4, false, 0.3, 12)
      }
    ],
    // 添加其他指标的相关指标
  };
  
  return relatedIndicatorsMap[indicatorId] || [];
};

/**
 * 生成模拟图表数据
 * @param {number} baseline - 基准值
 * @param {boolean} uptrend - 是否上升趋势
 * @param {number} volatility - 波动幅度
 * @param {number} count - 数据点数量
 * @returns {Array<DataPoint>} 模拟数据
 */
const generateMockChartData = (
  baseline: number, 
  uptrend: boolean, 
  volatility: number, 
  count: number = 24
): DataPoint[] => {
  const result: DataPoint[] = [];
  let value = baseline;
  const baseDate = new Date(2023, 3, 1); // 2023年4月
  
  for (let i = 0; i < count; i++) {
    const currentDate = new Date(baseDate);
    currentDate.setMonth(baseDate.getMonth() - i);
    
    // 上升或下降趋势
    const trend = uptrend ? 0.1 : -0.1;
    
    // 随机波动
    const randomFactor = (Math.random() - 0.5) * volatility;
    
    // 计算新值
    value = value + trend + randomFactor;
    
    // 确保值合理
    value = Math.max(0.1, value);
    
    // 计算同比和环比变化
    const yoy = i > 11 
      ? ((value / (result[result.length - 12]?.value || baseline)) - 1) * 100 
      : (Math.random() * 2 - 0.5) * 3;
    
    const mom = i > 0 
      ? ((value / (result[result.length - 1]?.value || baseline)) - 1) * 100 
      : (Math.random() * 2 - 0.5) * 0.8;
    
    result.unshift({
      date: `${currentDate.getFullYear()}-${String(currentDate.getMonth() + 1).padStart(2, '0')}`,
      value: value,
      yoy: yoy,
      mom: mom
    });
  }
  
  return result;
};

/**
 * 获取模拟指标数据
 * @param {string} indicatorId - 指标ID
 * @param {TimeRangeType} timeRange - 时间范围
 * @returns {IndicatorDetailType} 模拟指标数据
 */
const getMockIndicatorData = (indicatorId: string, timeRange: TimeRangeType): IndicatorDetailType => {
  // 基于指标ID生成一些模拟数据
  // 实际应用中应该用真实数据替换
  
  // 时间范围到月份数的映射
  const timeRangeToMonths: Record<TimeRangeType, number> = {
    '1m': 1,
    '3m': 3,
    '6m': 6,
    '1y': 12,
    '3y': 36,
    '5y': 60
  };
  
  const months = timeRangeToMonths[timeRange] || 12;
  
  // 根据指标ID设置一些基本参数
  let baseline = 0;
  let uptrend = false;
  let volatility = 0.5;
  let unit = '';
  let name = indicatorId;
  let category: CategoryType = 'other';
  let region: RegionType = 'us';
  let description = '';
  
  // 根据指标ID设置不同的参数
  if (indicatorId.includes('gdp')) {
    baseline = 5.0;
    uptrend = true;
    volatility = 0.8;
    unit = '%';
    name = 'GDP增长率';
    category = 'growth';
    description = '国内生产总值(GDP)是衡量经济活动总量的综合指标。';
  } else if (indicatorId.includes('unemployment')) {
    baseline = 3.5;
    uptrend = false;
    volatility = 0.3;
    unit = '%';
    name = '失业率';
    category = 'employment';
    description = '失业率表示劳动力中当前没有工作但正在积极寻找工作的人的百分比。';
  } else if (indicatorId.includes('pmi')) {
    baseline = 50.5;
    uptrend = true;
    volatility = 1.2;
    unit = '';
    name = '制造业PMI';
    category = 'production';
    description = '采购经理人指数(PMI)是衡量制造业活动的经济指标。';
  }
  
  if (indicatorId.startsWith('us-')) {
    region = 'us';
    name = `美国${name}`;
  } else if (indicatorId.startsWith('cn-')) {
    region = 'china';
    name = `中国${name}`;
  } else {
    region = 'cross';
  }
  
  // 生成图表数据
  const chartData = generateMockChartData(baseline, uptrend, volatility, months);
  
  // 计算一些统计值
  const current = chartData[chartData.length - 1].value;
  const previous = chartData[chartData.length - 2]?.value || current;
  const yoy = chartData[chartData.length - 1].yoy;
  const mom = chartData[chartData.length - 1].mom;
  const values = chartData.map(item => item.value);
  const max = Math.max(...values);
  const min = Math.min(...values);
  const avg = values.reduce((sum, value) => sum + value, 0) / values.length;
  const trend: TrendType = yoy >= 0 ? 'up' : 'down';
  const change = yoy;
  const changeType = yoy >= 0 ? 'increase' : 'decrease';
  
  // 随机生成一个合理的预期值
  const expected = current + (Math.random() - 0.5) * volatility * 0.5;
  
  return {
    id: indicatorId,
    name: name,
    description: description,
    category: category,
    region: region,
    frequency: '月度',
    unit: unit,
    source: region === 'us' ? '美国经济分析局' : region === 'china' ? '中国国家统计局' : '多来源',
    sourceUrl: '#',
    updateTime: '2023-04-15',
    current: current,
    previous: previous,
    expected: expected,
    yoy: yoy,
    mom: mom,
    max: max,
    min: min,
    avg: avg,
    trend: trend,
    value: current,
    change: change,
    changeType: changeType,
    status: 'normal',
    chartData: chartData,
    tableData: chartData
  };
};