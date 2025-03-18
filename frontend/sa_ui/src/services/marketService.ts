// src/services/marketService.ts
import api from './api';
import { MinimalMarketData, HeatmapData } from '../types/market';
import { HotStocksResponse } from '../types/stock';

/**
 * 获取市场指数数据（极简）
 * 返回A股、港股、美股主要指数的实时数据
 */
export const getMinimalMarketIndices = async (): Promise<MinimalMarketData> => {
  try {
    const response = await api.get<MinimalMarketData>('/market/minimal_indices');
    return response.data as MinimalMarketData;
  } catch (error) {
    console.error('获取市场指数数据失败:', error);
    throw error;
  }
};

/**
 * 获取市场热力图数据
 * 返回行业板块涨跌情况
 */
export const getMarketHeatmap = async (): Promise<HeatmapData> => {
  try {
    const response = await api.get<HeatmapData>('/market/heatmap');
    return response.data as HeatmapData;
  } catch (error) {
    console.error('获取市场热力图数据失败:', error);
    throw error;
  }
};

/**
 * 获取热门股票列表
 * 返回当日交易活跃或关注度高的股票
 */
export const getHotStocks = async (): Promise<HotStocksResponse> => {
  try {
    const response = await api.get<HotStocksResponse>('/stocks/hot');
    return response as HotStocksResponse;
  } catch (error) {
    console.error('获取热门股票数据失败:', error);
    throw error;
  }
};
