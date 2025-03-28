// src/types/stock.ts

/**
 * K-line data point
 */
export interface KLineData {
  date: string;     // Date
  open: number;     // Opening price
  high: number;     // Highest price
  low: number;      // Lowest price
  close: number;    // Closing price
  volume: number;   // Volume
  amount?: number;  // Amount
}

/**
 * K-line response structure
 */
export interface StockKLine {
  code: string;      // Stock code
  period: string;    // Period, e.g., '1d', '1wk'
  type: string;      // Chart type, e.g., 'line', 'candle'
  data: KLineData[]; // K-line data array
}