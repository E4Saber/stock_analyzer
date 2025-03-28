// src/services/mock/mockMarketService.ts
import { IndexData, SectorData, HotStock, MarketStats } from '../types/market';
import { 
  generateIndexDataList, 
  generateSectorDataList, 
  generateHotStockList 
} from './mockData';

/**
 * Get minimal market indices data (mock)
 */
export const getMinimalMarketIndices = async (): Promise<IndexData[]> => {
  // Simulate delay
  await new Promise(resolve => setTimeout(resolve, 500));
  
  // Generate mock data
  return generateIndexDataList();
};

/**
 * Get market heatmap data (mock)
 */
export const getMarketHeatmap = async (): Promise<{sectors: SectorData[]}> => {
  // Simulate delay
  await new Promise(resolve => setTimeout(resolve, 500));
  
  // Generate mock sector data
  const sectors = generateSectorDataList(16);
  
  return { sectors };
};

/**
 * Get hot stocks list (mock)
 */
export const getHotStocks = async (): Promise<{hot_stocks: HotStock[]}> => {
  // Simulate delay
  await new Promise(resolve => setTimeout(resolve, 500));
  
  // Generate mock hot stocks data
  const hotStocks = generateHotStockList(10);
  
  return { hot_stocks: hotStocks };
};

/**
 * Get market overview data (mock)
 */
export const getMarketOverview = async (): Promise<{
  indices: IndexData[],
  sectors: SectorData[],
  hotStocks: HotStock[],
  marketStats: MarketStats
}> => {
  // Simulate delay
  await new Promise(resolve => setTimeout(resolve, 600));
  
  // Get all data
  const indices = await getMinimalMarketIndices();
  const { sectors } = await getMarketHeatmap();
  const { hot_stocks } = await getHotStocks();
  
  // Mock market statistics
  const marketStats = {
    totalStocks: 4823,
    upStocks: 2965,
    downStocks: 1798,
    limitUpStocks: 87,
    limitDownStocks: 35,
    totalVolume: 798526000000,
    totalAmount: 9365874520000
  };
  
  return {
    indices,
    sectors,
    hotStocks: hot_stocks,
    marketStats
  };
};

/**
 * Get market hotspots data (mock)
 */
export const getMarketHotspots = async (): Promise<{
  trends: { category: string; stocks: HotStock[]; desc: string }[],
  news: { id: string; title: string; source: string; time: string; url: string; }[]
}> => {
  // Simulate delay
  await new Promise(resolve => setTimeout(resolve, 700));
  
  const trends = [
    {
      category: '半导体产业链',
      stocks: [
        { code: '603501', name: '韦尔股份', price: 86.23, change_pct: 4.72, volume: 12568400, amount: 1064312952, turnover_rate: 0.82 },
        { code: '603986', name: '兆易创新', price: 118.56, change_pct: 3.87, volume: 8956300, amount: 1063254862, turnover_rate: 0.76 },
        { code: '688012', name: '中微公司', price: 65.89, change_pct: 5.23, volume: 7548900, amount: 497345561, turnover_rate: 0.98 }
      ],
      desc: '国产替代加速推进，半导体行业景气度持续上升，相关公司业绩增长显著。'
    },
    {
      category: '医药创新',
      stocks: [
        { code: '600587', name: '新华医疗', price: 26.75, change_pct: 7.58, volume: 26587100, amount: 712456925, turnover_rate: 1.84 },
        { code: '603259', name: '药明康德', price: 68.32, change_pct: 3.25, volume: 9526800, amount: 651072576, turnover_rate: 0.65 },
        { code: '300759', name: '康龙化成', price: 45.28, change_pct: 2.56, volume: 6892500, amount: 312212400, turnover_rate: 0.54 }
      ],
      desc: '医药创新持续推进，CRO/CDMO行业景气度高，国产创新药研发取得突破。'
    },
    {
      category: '新能源汽车',
      stocks: [
        { code: '002594', name: '比亚迪', price: 228.63, change_pct: 2.16, volume: 9863500, amount: 2250896805, turnover_rate: 0.56 },
        { code: '300750', name: '宁德时代', price: 156.83, change_pct: 1.98, volume: 8569200, amount: 1343854236, turnover_rate: 0.48 },
        { code: '601877', name: '正泰电器', price: 28.76, change_pct: 3.15, volume: 12658900, amount: 364068844, turnover_rate: 0.72 }
      ],
      desc: '新能源汽车销量持续增长，国内外市场需求旺盛，相关零部件企业受益。'
    }
  ];
  
  const news = [
    {
      id: 'news1',
      title: '央行下调存款基准利率，货币政策继续保持宽松',
      source: '财经日报',
      time: '2025-03-18 09:32',
      url: '#'
    },
    {
      id: 'news2',
      title: '工信部：持续推进芯片产业自主创新，加大扶持力度',
      source: '证券时报',
      time: '2025-03-18 08:45',
      url: '#'
    },
    {
      id: 'news3',
      title: '国务院常务会议：部署进一步扩大内需措施',
      source: '人民日报',
      time: '2025-03-17 19:30',
      url: '#'
    },
    {
      id: 'news4',
      title: '多家券商发布研报看好新能源板块后市表现',
      source: '上海证券报',
      time: '2025-03-17 16:25',
      url: '#'
    },
    {
      id: 'news5',
      title: '央行、银保监会联合发文规范房地产金融业务',
      source: '21世纪经济报道',
      time: '2025-03-17 14:58',
      url: '#'
    }
  ];
  
  return { trends, news };
};