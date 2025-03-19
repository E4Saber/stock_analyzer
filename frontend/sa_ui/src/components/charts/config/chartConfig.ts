// src/components/charts/config/chartConfig.ts
import { StockData as MarketStockData } from '../../../types/market';

// Re-export StockData type for consistency
export type StockData = MarketStockData;

/**
 * Chart type
 */
export type ChartType = 'line' | 'candle' | 'bar';

/**
 * Period type
 */
export type PeriodType = '1m' | '5m' | '15m' | '30m' | '60m' | 'day' | 'week' | 'month' | 'year';

/**
 * Indicator type
 */
export type IndicatorType = 'MA' | 'MACD' | 'KDJ' | 'RSI' | 'VOL' | 'BOLL';

/**
 * Indicator panel configuration
 */
export interface IndicatorPanelConfig {
  type: IndicatorType;   // Indicator type
  height: number;        // Panel height
  active: boolean;       // Whether active
}

/**
 * Period mapping table
 */
export const periodMap: Record<PeriodType, string> = {
  '1m': '1m',
  '5m': '5m',
  '15m': '15m',
  '30m': '30m',
  '60m': '60m',
  'day': '1d',
  'week': '1wk',
  'month': '1mo',
  'year': '1y'
};

/**
 * Get indicator title
 * @param type Indicator type
 */
export function getIndicatorTitle(type: IndicatorType): string {
  switch (type) {
    case 'MA':
      return '移动平均线 (MA)';
    case 'MACD':
      return 'MACD指标';
    case 'KDJ':
      return 'KDJ指标';
    case 'RSI':
      return '相对强弱指标 (RSI)';
    case 'VOL':
      return '成交量';
    case 'BOLL':
      return '布林带 (BOLL)';
    default:
      return '技术指标';
  }
}

/**
 * Get indicator color configuration
 * @param type Indicator type
 */
export function getIndicatorColors(type: IndicatorType): Record<string, string> {
  switch (type) {
    case 'MA':
      return {
        MA5: '#8d4bbb',
        MA10: '#ff9900',
        MA20: '#cc0000'
      };
    case 'MACD':
      return {
        MACD: '#ffffff',
        DIF: '#da6ee8',
        DEA: '#40a9ff',
        HIST_UP: '#ef232a',
        HIST_DOWN: '#14b143'
      };
    case 'KDJ':
      return {
        K: '#ffc53d',
        D: '#40a9ff',
        J: '#ff4d4f'
      };
    case 'RSI':
      return {
        RSI6: '#ffc53d',
        RSI12: '#40a9ff',
        RSI24: '#ff4d4f'
      };
    case 'VOL':
      return {
        UP: '#ef232a',
        DOWN: '#14b143',
        MA5: '#ffc53d',
        MA10: '#40a9ff'
      };
    case 'BOLL':
      return {
        MID: '#8d4bbb',
        UPPER: '#ff9900',
        LOWER: '#ff9900'
      };
    default:
      return {};
  }
}

/**
 * Get available indicator types
 */
export function getAvailableIndicators(): IndicatorType[] {
  return ['MA', 'MACD', 'KDJ', 'RSI', 'VOL', 'BOLL'];
}

/**
 * Get default indicator panel configuration
 */
export function getDefaultIndicatorPanels(): IndicatorPanelConfig[] {
  return [
    { type: 'MACD', height: 120, active: false },
    { type: 'KDJ', height: 120, active: false },
    { type: 'RSI', height: 120, active: false },
    { type: 'VOL', height: 120, active: true },
    { type: 'MA', height: 0, active: true },    // MA usually displayed on main chart
    { type: 'BOLL', height: 0, active: false }  // BOLL usually displayed on main chart
  ];
}