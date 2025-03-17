// src/services/stockService.ts
import api from './api';
import { StockBasic, StockKLine } from '../types/stock';

/**
 * 获取股票基本信息
 * @param stockCode 股票代码
 */
export const getStockBasic = async (stockCode: string): Promise<StockBasic> => {
  try {
    const response = await api.get<StockBasic>(`/stocks/basic/${stockCode}`);
    return response.data as StockBasic;
  } catch (error) {
    console.error(`获取股票 ${stockCode} 基本信息失败:`, error);
    throw error;
  }
};

/**
 * 获取股票K线数据
 * @param stockCode 股票代码
 * @param period K线周期: 1d, 5d, 1mo, 3mo, 6mo, 1y
 * @param klineType K线类型: candlestick, line
 */
export const getStockKline = async (
  stockCode: string,
  period: string = '1d',
  klineType: string = 'candlestick'
): Promise<StockKLine> => {
  try {
    const response = await api.get<StockKLine>(
      `/stocks/kline/${stockCode}?period=${period}&kline_type=${klineType}`
    );
    return response.data as StockKLine;
  } catch (error) {
    console.error(`获取股票 ${stockCode} K线数据失败:`, error);
    throw error;
  }
};