// src/types/market.ts
export interface MinimalIndexData {
  ts_code: string;
  name: string;
  current: number;
  change: number;
  pct_chg: number;
}

export interface SectorData {
  name: string;
  change_pct: number;
  avg_volume: number;
}

// export interface MinimalMarketData {
//   cn_indices: MinimalIndexData[];
//   global_indices: MinimalIndexData[];
// }

export interface HeatmapData {
  sectors: SectorData[];
}
