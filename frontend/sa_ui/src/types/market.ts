// src/types/market.ts
export interface IndexData {
  code: string;
  name: string;
  current: number;
  change: number;
  change_pct: number;
}

export interface SectorData {
  name: string;
  change_pct: number;
  avg_volume: number;
}

export interface MarketData {
  cn_indices: IndexData[];
  global_indices: IndexData[];
}

export interface HeatmapData {
  sectors: SectorData[];
}
