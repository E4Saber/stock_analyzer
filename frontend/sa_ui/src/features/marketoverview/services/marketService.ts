// src/services/marketService.ts
import api, { USE_MOCK } from '../../../shared/services/api';
import { IndexData, SectorData, HotStock, MarketStats, MarketTrend, MarketNews } from '../types/market';

// Import mock services if in mock mode
import * as mockMarketService from './mockMarketService';

/**
 * Get minimal market indices data
 * Returns real-time data for major indices from China, Hong Kong, and US markets
 */
export const getMinimalMarketIndices = async (): Promise<IndexData[]> => {
  if (USE_MOCK) {
    return mockMarketService.getMinimalMarketIndices();
  }
  
  try {
    const response = await api.get<{data: IndexData[]}>('/market/minimal_indices');
    return response.data;
  } catch (error) {
    console.error('Failed to get market indices data:', error);
    throw error;
  }
};

/**
 * Get market heatmap data
 * Returns sector/industry performance data
 */
export const getMarketHeatmap = async (): Promise<{sectors: SectorData[]}> => {
  if (USE_MOCK) {
    return mockMarketService.getMarketHeatmap();
  }
  
  try {
    const response = await api.get<{sectors: SectorData[]}>('/market/heatmap');
    return response;
  } catch (error) {
    console.error('Failed to get market heatmap data:', error);
    throw error;
  }
};

/**
 * Get hot stocks list
 * Returns the most active or popular stocks of the day
 */
export const getHotStocks = async (): Promise<{hot_stocks: HotStock[]}> => {
  if (USE_MOCK) {
    return mockMarketService.getHotStocks();
  }
  
  try {
    const response = await api.get<{hot_stocks: HotStock[]}>('/stocks/hot');
    return response;
  } catch (error) {
    console.error('Failed to get hot stocks data:', error);
    throw error;
  }
};

/**
 * Get market overview data
 * Returns comprehensive market data including indices, sectors, hot stocks, and market statistics
 */
export const getMarketOverview = async (): Promise<{
  indices: IndexData[],
  sectors: SectorData[],
  hotStocks: HotStock[],
  marketStats: MarketStats
}> => {
  if (USE_MOCK) {
    return mockMarketService.getMarketOverview();
  }
  
  try {
    const response = await api.get<{
      indices: IndexData[],
      sectors: SectorData[],
      hotStocks: HotStock[],
      marketStats: MarketStats
    }>('/market/overview');
    return response;
  } catch (error) {
    console.error('Failed to get market overview data:', error);
    throw error;
  }
};

/**
 * Get market hotspots data
 * Returns trending sectors/themes and related news
 */
export const getMarketHotspots = async (): Promise<{
  trends: MarketTrend[],
  news: MarketNews[]
}> => {
  if (USE_MOCK) {
    return mockMarketService.getMarketHotspots();
  }
  
  try {
    const response = await api.get<{
      trends: MarketTrend[],
      news: MarketNews[]
    }>('/market/hotspots');
    return response;
  } catch (error) {
    console.error('Failed to get market hotspots data:', error);
    throw error;
  }
};