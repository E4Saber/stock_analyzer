// src/types/stock.ts
export interface StockBasic {
  code: string;
  name: string;
  current: number;
  change: number;
  change_pct: number;
  open: number;
  high: number;
  low: number;
  volume: number;
  amount?: number;
  market_cap?: number;
  industry?: string;
  area?: string;
  list_date?: string;
  sector?: string;
  currency?: string;
}

export interface KLineData {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface StockKLine {
  code: string;
  period: string;
  type: string;
  data: KLineData[];
}

export interface HotStock {
  code: string;
  name: string;
  price: number;
  change_pct: number;
}

export interface HotStocksResponse {
  hot_stocks: HotStock[];
}