// src/services/mockMarketService.ts
import { 
    IndexData, 
    SectorData, 
    HotStock 
  } from '../types/market';
  
  /**
   * 生成模拟指数数据
   */
  export const getMinimalMarketIndices = async (): Promise<IndexData[]> => {
    // 模拟延迟
    await new Promise(resolve => setTimeout(resolve, 500));
    
    // 模拟数据
    const indexData: IndexData[] = [
      {
        code: '000001.SH',
        name: '上证指数',
        current: 3251.63,
        change: 32.67,
        change_pct: 1.01,
        ts_code: '000001.SH'
      },
      {
        code: '399001.SZ',
        name: '深证成指',
        current: 10638.11,
        change: -28.92,
        change_pct: -0.27,
        ts_code: '399001.SZ'
      },
      {
        code: '399006.SZ',
        name: '创业板指',
        current: 2067.48,
        change: 12.89,
        change_pct: 0.63,
        ts_code: '399006.SZ'
      },
      {
        code: '000300.SH',
        name: '沪深300',
        current: 3983.27,
        change: 19.56,
        change_pct: 0.49,
        ts_code: '000300.SH'
      },
      {
        code: '.HSI',
        name: '恒生指数',
        current: 17687.42,
        change: -102.63,
        change_pct: -0.58,
        ts_code: '.HSI'
      },
      {
        code: '.IXIC',
        name: '纳斯达克',
        current: 16368.39,
        change: 211.51,
        change_pct: 1.31,
        ts_code: '.IXIC'
      },
      {
        code: '.DJI',
        name: '道琼斯',
        current: 39127.14,
        change: 143.21,
        change_pct: 0.37,
        ts_code: '.DJI'
      },
      {
        code: '.N225',
        name: '日经225',
        current: 39561.72,
        change: -287.14,
        change_pct: -0.72,
        ts_code: '.N225'
      }
    ];
    
    return indexData;
  };
  
  /**
   * 生成模拟行业板块数据
   */
  export const getMarketHeatmap = async (): Promise<{sectors: SectorData[]}> => {
    // 模拟延迟
    await new Promise(resolve => setTimeout(resolve, 500));
    
    // 模拟行业板块数据
    const sectors: SectorData[] = [
      { name: '半导体', change_pct: 2.73, avg_volume: 32580000 },
      { name: '新能源', change_pct: 1.95, avg_volume: 28750000 },
      { name: '医药制造', change_pct: 1.42, avg_volume: 19870000 },
      { name: '银行', change_pct: -0.63, avg_volume: 42150000 },
      { name: '食品饮料', change_pct: 0.87, avg_volume: 15230000 },
      { name: '电子元件', change_pct: 1.56, avg_volume: 22680000 },
      { name: '汽车整车', change_pct: 0.32, avg_volume: 18750000 },
      { name: '有色金属', change_pct: -1.25, avg_volume: 25360000 },
      { name: '房地产', change_pct: -2.18, avg_volume: 38570000 },
      { name: '家用电器', change_pct: 0.43, avg_volume: 11240000 },
      { name: '电力设备', change_pct: 1.28, avg_volume: 17680000 },
      { name: '计算机', change_pct: 1.87, avg_volume: 23480000 },
      { name: '煤炭', change_pct: -0.93, avg_volume: 19760000 },
      { name: '钢铁', change_pct: -1.52, avg_volume: 26840000 },
      { name: '通信设备', change_pct: 1.23, avg_volume: 16950000 },
      { name: '保险', change_pct: -0.38, avg_volume: 14780000 }
    ];
    
    return { sectors };
  };
  
  /**
   * 生成模拟热门股票数据
   */
  export const getHotStocks = async (): Promise<{hot_stocks: HotStock[]}> => {
    // 模拟延迟
    await new Promise(resolve => setTimeout(resolve, 500));
    
    // 模拟热门股票数据
    const hotStocks: HotStock[] = [
      { code: '600519', name: '贵州茅台', price: 1782.50, change_pct: 1.25, volume: 1259800, amount: 2251384950, turnover_rate: 0.23 },
      { code: '601318', name: '中国平安', price: 42.82, change_pct: -0.86, volume: 23568700, amount: 1014321926, turnover_rate: 0.41 },
      { code: '000858', name: '五粮液', price: 162.78, change_pct: 0.93, volume: 3256900, amount: 532154382, turnover_rate: 0.28 },
      { code: '600036', name: '招商银行', price: 36.25, change_pct: -0.52, volume: 18965200, amount: 689478500, turnover_rate: 0.33 },
      { code: '601899', name: '紫金矿业', price: 9.67, change_pct: 2.33, volume: 87562300, amount: 843087041, turnover_rate: 1.05 },
      { code: '603501', name: '韦尔股份', price: 86.23, change_pct: 4.72, volume: 12568400, amount: 1064312952, turnover_rate: 0.82 },
      { code: '600587', name: '新华医疗', price: 26.75, change_pct: 7.58, volume: 26587100, amount: 712456925, turnover_rate: 1.84 },
      { code: '002594', name: '比亚迪', price: 228.63, change_pct: 2.16, volume: 9863500, amount: 2250896805, turnover_rate: 0.56 },
      { code: '601238', name: '广汽集团', price: 12.36, change_pct: -1.12, volume: 15689300, amount: 194818348, turnover_rate: 0.38 },
      { code: '600438', name: '通威股份', price: 18.25, change_pct: 3.75, volume: 45698200, amount: 822586150, turnover_rate: 0.92 }
    ];
    
    return { hot_stocks: hotStocks };
  };
  
  /**
   * 获取市场概览数据
   */
  export const getMarketOverview = async (): Promise<{
    indices: IndexData[],
    sectors: SectorData[],
    hotStocks: HotStock[],
    marketStats: {
      totalStocks: number,
      upStocks: number,
      downStocks: number,
      limitUpStocks: number,
      limitDownStocks: number,
      totalVolume: number,
      totalAmount: number
    }
  }> => {
    // 模拟延迟
    await new Promise(resolve => setTimeout(resolve, 600));
    
    // 获取各项数据
    const indices = await getMinimalMarketIndices();
    const { sectors } = await getMarketHeatmap();
    const { hot_stocks } = await getHotStocks();
    
    // 市场统计数据
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
   * 获取市场热点数据
   */
  export const getMarketHotspots = async (): Promise<{
    trends: { category: string; stocks: HotStock[]; desc: string }[],
    news: { id: string; title: string; source: string; time: string; url: string; }[]
  }> => {
    // 模拟延迟
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