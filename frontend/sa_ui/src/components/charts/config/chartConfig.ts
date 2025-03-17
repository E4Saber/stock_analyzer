// src/components/charts/config/chartConfig.ts

// 技术指标类型定义
export type IndicatorType = 'MACD' | 'KDJ' | 'RSI' | 'BOLL' | 'VOL' | 'MA' | 'EMA';

// 图表类型定义
export type ChartType = 'line' | 'candle' | 'bar';

// 时间周期定义
export type PeriodType = '1m' | '5m' | '15m' | '30m' | '60m' | 'day' | 'week' | 'month';

// 股票数据接口
export interface StockData {
  code: string;
  name: string;
  current: number;
  change: number;
  change_percent: number;
  open?: number;
  high?: number;
  low?: number;
  volume?: number;
  amount?: number;
  turnover?: number;
  pe?: number;
  pb?: number;
  market_cap?: number;
  industry?: string;
}

// 指标面板配置
export interface IndicatorPanelConfig {
  type: IndicatorType;
  height: number;
  active: boolean;
}

// 映射周期到API格式
export const periodMap: Record<PeriodType, string> = {
  '1m': '1m',
  '5m': '5m',
  '15m': '15m',
  '30m': '30m',
  '60m': '60m',
  'day': '1d',
  'week': '1wk',
  'month': '1mo'
};

// 获取指标标题
export const getIndicatorTitle = (type: IndicatorType): string => {
  const titleMap: Record<IndicatorType, string> = {
    'MACD': 'MACD指标(12,26,9)',
    'KDJ': 'KDJ指标(9,3,3)',
    'RSI': 'RSI指标(6,12,24)',
    'BOLL': '布林带(20,2)',
    'VOL': '成交量',
    'MA': '移动平均线',
    'EMA': '指数移动平均线'
  };
  
  return titleMap[type] || type;
};

// 获取指标颜色配置
export const getIndicatorColors = (type: IndicatorType): Record<string, string> => {
  const colorMap: Record<IndicatorType, Record<string, string>> = {
    'MACD': {
      'MACD': '#ffffff',
      'DIF': '#da6ee8',
      'DEA': '#40a9ff',
      'HIST_UP': '#ef232a',
      'HIST_DOWN': '#14b143'
    },
    'KDJ': {
      'K': '#ffc53d',
      'D': '#40a9ff',
      'J': '#ff4d4f'
    },
    'RSI': {
      'RSI6': '#ffc53d',
      'RSI12': '#40a9ff',
      'RSI24': '#ff4d4f'
    },
    'BOLL': {
      'UPPER': '#ff9900',
      'MID': '#8d4bbb',
      'LOWER': '#ff9900'
    },
    'VOL': {
      'UP': '#ef232a',
      'DOWN': '#14b143',
      'MA5': '#ffc53d',
      'MA10': '#40a9ff'
    },
    'MA': {
      'MA5': '#8d4bbb',
      'MA10': '#ff9900',
      'MA20': '#cc0000',
      'MA30': '#40a9ff',
      'MA60': '#52c41a'
    },
    'EMA': {
      'EMA5': '#8d4bbb',
      'EMA10': '#ff9900',
      'EMA20': '#cc0000',
      'EMA30': '#40a9ff',
      'EMA60': '#52c41a'
    }
  };
  
  return colorMap[type] || {};
};

// 获取可用技术指标列表
export const getAvailableIndicators = (): IndicatorType[] => {
  return ['MACD', 'KDJ', 'RSI', 'BOLL', 'VOL', 'MA', 'EMA'];
};

// 获取默认活跃指标面板
export const getDefaultIndicatorPanels = (): IndicatorPanelConfig[] => {
  return [
    { type: 'MACD', height: 120, active: true },
    { type: 'VOL', height: 120, active: true },
    { type: 'KDJ', height: 120, active: false },
    { type: 'RSI', height: 120, active: false },
    { type: 'BOLL', height: 120, active: false },
    { type: 'MA', height: 120, active: false },
    { type: 'EMA', height: 120, active: false }
  ];
};