// src/types/market.ts

/**
 * 指数数据接口
 */
export interface IndexData {
  code: string;           // 指数代码
  name: string;           // 指数名称
  current: number;        // 当前点位
  change: number;         // 涨跌点数
  change_pct: number;     // 涨跌幅
  ts_code?: string;       // 特殊代码 (兼容tushare)
}

/**
 * 行业板块数据接口
 */
export interface SectorData {
  name: string;           // 板块名称
  change_pct: number;     // 涨跌幅
  avg_volume: number;     // 平均成交量
}

/**
 * 热门股票接口
 */
export interface HotStock {
  code: string;           // 股票代码
  name: string;           // 股票名称
  price: number;          // 价格
  change_pct: number;     // 涨跌幅
  volume: number;         // 成交量
  amount: number;         // 成交额
  turnover_rate: number;  // 换手率
}

/**
 * 市场统计数据
 */
export interface MarketStats {
  totalStocks: number;     // 总股票数
  upStocks: number;        // 上涨股票数
  downStocks: number;      // 下跌股票数
  limitUpStocks: number;   // 涨停股票数
  limitDownStocks: number; // 跌停股票数
  totalVolume: number;     // 总成交量
  totalAmount: number;     // 总成交额
}

/**
 * 市场热点趋势
 */
export interface MarketTrend {
  category: string;       // 板块类别
  stocks: HotStock[];     // 代表股票
  desc: string;           // 描述
}

/**
 * 市场新闻
 */
export interface MarketNews {
  id: string;             // 新闻ID
  title: string;          // 标题
  source: string;         // 来源
  time: string;           // 时间
  url: string;            // 链接
}

/**
 * 股票持股数据
 */
export interface ShareholderData {
  name: string;           // 股东名称
  shares: number;         // 持股数量
  ratio: number;          // 持股比例
  change: number;         // 变动数量
  type: 'institution' | 'individual' | 'government'; // 股东类型
}

/**
 * 公司财务指标
 */
export interface FinancialIndicator {
  year: string;           // 年份
  quarter: string;        // 季度
  revenue: number;        // 营收
  netProfit: number;      // 净利润
  grossMargin: number;    // 毛利率
  netMargin: number;      // 净利率
  roe: number;            // 净资产收益率
  eps: number;            // 每股收益
  debt_to_assets: number; // 资产负债率
}

/**
 * 分时数据点
 */
export interface TimeSeriesDataPoint {
  time: string;           // 时间
  price: number;          // 价格
  volume: number;         // 成交量
  avg_price: number;      // 均价
}