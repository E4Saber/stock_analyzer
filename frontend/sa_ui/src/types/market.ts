// src/types/market.ts

/**
 * Stock data interface
 */
export interface StockData {
  code: string;           // Stock code
  name: string;           // Stock name
  current: number;        // Current price
  change: number;         // Price change
  change_percent: number; // Price change percentage
  open?: number;          // Opening price
  high?: number;          // Highest price
  low?: number;           // Lowest price
  volume?: number;        // Trading volume
  amount?: number;        // Trading amount
  market_cap?: number;    // Market capitalization
  pe?: number;            // Price-to-earnings ratio
  pb?: number;            // Price-to-book ratio
  industry?: string;      // Industry classification
  turnover_rate?: number; // Turnover rate
  dividend?: number;      // Dividend yield
  update_time?: string;   // Update time
}

/**
 * Index data interface
 */
export interface IndexData {
  code: string;           // Index code
  name: string;           // Index name
  current: number;        // Current level
  change: number;         // Change in points
  change_pct: number;     // Change percentage
  ts_code?: string;       // Special code (compatible with tushare)
}

/**
 * Sector data interface
 */
export interface SectorData {
  name: string;           // Sector name
  change_pct: number;     // Change percentage
  avg_volume: number;     // Average volume
}

/**
 * Hot stock interface
 */
export interface HotStock {
  code: string;           // Stock code
  name: string;           // Stock name
  price: number;          // Price
  change_pct: number;     // Change percentage
  volume?: number;        // Volume
  amount?: number;        // Amount
  turnover_rate?: number; // Turnover rate
}

/**
 * Market statistics
 */
export interface MarketStats {
  totalStocks: number;     // Total number of stocks
  upStocks: number;        // Number of stocks up
  downStocks: number;      // Number of stocks down
  limitUpStocks: number;   // Number of stocks limit up
  limitDownStocks: number; // Number of stocks limit down
  totalVolume: number;     // Total volume
  totalAmount: number;     // Total amount
}

/**
 * Market trend
 */
export interface MarketTrend {
  category: string;       // Category
  stocks: HotStock[];     // Representative stocks
  desc: string;           // Description
}

/**
 * Market news
 */
export interface MarketNews {
  id: string;             // News ID
  title: string;          // News title
  source: string;         // News source
  time: string;           // News time
  url: string;            // News URL
}

/**
 * Shareholder data
 */
export interface ShareholderData {
  name: string;           // Shareholder name
  shares: number;         // Number of shares
  ratio: number;          // Shareholding ratio
  change: number;         // Change in shares
  type: 'institution' | 'individual' | 'government'; // Shareholder type
}

/**
 * Financial indicator
 */
export interface FinancialIndicator {
  year: string;           // Year
  quarter: string;        // Quarter
  revenue: number;        // Revenue
  netProfit: number;      // Net profit
  grossMargin: number;    // Gross margin
  netMargin: number;      // Net margin
  roe: number;            // Return on equity
  eps: number;            // Earnings per share
  debt_to_assets: number; // Debt to assets ratio
}

/**
 * Time series data point
 */
export interface TimeSeriesDataPoint {
  time: string;           // Time
  price: number;          // Price
  volume: number;         // Volume
  avg_price?: number;     // Average price
}