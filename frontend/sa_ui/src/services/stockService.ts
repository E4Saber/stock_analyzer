// src/services/stockService.ts
import api, { USE_MOCK } from './api';
import { StockData, ShareholderData, FinancialIndicator, MarketNews } from '../types/market';
import { ChartType, IndicatorType } from '../components/charts/config/chartConfig';

// Import mock services if in mock mode
import * as mockStockService from './mock/mockStockService';

/**
 * Get stock detail information
 * @param code Stock code
 */
export const getStockDetail = async (code: string): Promise<{
  stock: StockData,
  relatedStocks: StockData[],
  shareholders: ShareholderData[],
  financials: FinancialIndicator[],
  news: MarketNews[]
}> => {
  if (USE_MOCK) {
    return mockStockService.getStockDetail(code);
  }
  
  try {
    const response = await api.get<{
      stock: StockData,
      relatedStocks: StockData[],
      shareholders: ShareholderData[],
      financials: FinancialIndicator[],
      news: MarketNews[]
    }>(`/stocks/detail/${code}`);
    return response;
  } catch (error) {
    console.error(`Failed to get stock detail for ${code}:`, error);
    throw error;
  }
};

/**
 * Get stock K-line data
 * @param stockCode Stock code
 * @param period K-line period: 1d, 5d, 1mo, 3mo, 6mo, 1y
 * @param chartType Chart type: line, candle, bar
 */
export const getStockKline = async (
  stockCode: string,
  period: string = '1d',
  chartType: string = 'candle'
) => {
  if (USE_MOCK) {
    return mockStockService.getStockKline(stockCode, period, chartType);
  }
  
  try {
    const response = await api.get(
      `/stocks/kline/${stockCode}?period=${period}&chart_type=${chartType}`
    );
    return response;
  } catch (error) {
    console.error(`Failed to get K-line data for ${stockCode}:`, error);
    throw error;
  }
};

/**
 * Get stock technical indicators
 * @param stockCode Stock code
 * @param period Period
 * @param indicators Indicator types array
 */
export const getStockIndicators = async (
  stockCode: string,
  period: string,
  indicators: IndicatorType[]
) => {
  if (USE_MOCK) {
    return mockStockService.getStockIndicators(stockCode, period, indicators);
  }
  
  try {
    const response = await api.get(
      `/stocks/indicators/${stockCode}?period=${period}&indicators=${indicators.join(',')}`
    );
    return response;
  } catch (error) {
    console.error(`Failed to get indicators for ${stockCode}:`, error);
    throw error;
  }
};

/**
 * Get stock financial data
 * @param stockCode Stock code
 */
export const getStockFinancial = async (stockCode: string) => {
  if (USE_MOCK) {
    return mockStockService.getStockFinancial(stockCode);
  }
  
  try {
    const response = await api.get(`/stocks/financial/${stockCode}`);
    return response;
  } catch (error) {
    console.error(`Failed to get financial data for ${stockCode}:`, error);
    throw error;
  }
};