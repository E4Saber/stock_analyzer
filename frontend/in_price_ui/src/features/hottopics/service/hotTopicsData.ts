import { HotTopicItem } from '../components/HotTopicCard';
import { ExpertOpinionItem } from '../components/ExpertOpinions';

// 热点数据类型
export interface HotTopicsData {
  trending: HotTopicItem[];
  policy: HotTopicItem[];
  market: HotTopicItem[];
  company: HotTopicItem[];
  data: HotTopicItem[];
}

// 专家观点数据
export const expertOpinionsData: ExpertOpinionItem[] = [
  {
    id: '1',
    name: '张经济',
    title: '关于美联储加息的影响分析',
    content: '本次美联储加息虽在预期之内，但暗示年内还有1-2次加息超出市场预期，这将对新兴市场形成较大压力。短期内，美元指数或继续走强，新兴市场货币面临贬值压力，资本流出风险上升。对中国而言，人民币汇率管理难度增加，但中美利差仍有一定空间，外汇储备充足，有能力应对短期冲击。',
    expertise: '宏观经济',
    date: '2024-09-26',
    likes: 128,
    comments: 32
  },
  {
    id: '2',
    name: '李分析',
    title: '能源危机对全球通胀的传导效应',
    content: '能源价格飙升将通过多个渠道向全球通胀传导，对各国通胀预期形成上行压力，央行或被迫采取更激进的货币政策。从历史经验看，能源价格上涨通常滞后6-8个月才充分反映在CPI中，因此即使原油价格见顶，通胀压力仍将持续。预计四季度全球通胀可能再次上行，各国央行或被迫延长紧缩周期。',
    expertise: '能源市场',
    date: '2024-09-25',
    likes: 87,
    comments: 24
  },
  {
    id: '3',
    name: '王策略',
    title: '中国降准如何影响A股市场',
    content: '此次降准释放的流动性主要用于支持实体经济，短期内对A股是利好，但能否改变市场趋势还要看后续政策组合拳。从历史经验看，单纯的降准对股市的提振作用有限且持续时间较短。真正能带动市场转势的是实体经济基本面的改善和企业盈利的提升。建议关注政策受益板块，如基建、地产及部分中小企业相关板块。',
    expertise: 'A股市场',
    date: '2024-09-24',
    likes: 103,
    comments: 36
  }
];

// 模拟热点数据
export const hotTopicsData: HotTopicsData = {
  trending: [
    {
      id: '1',
      title: '美联储宣布加息25个基点，市场波动加剧',
      summary: '美联储于本周三宣布加息25个基点，这是2024年首次加息，并暗示年内可能还会有1-2次加息。市场对此反应强烈，主要股指在消息公布后出现剧烈波动。',
      timestamp: '2024-09-25 22:00',
      heat: 98,
      impact: 'high',
      category: 'policy',
      tags: ['美联储', '加息', '货币政策'],
      sentiment: -15,
      relatedAssets: ['美股', '美元', '国债'],
      views: 12583,
      comments: 521,
      likes: 328
    },
    {
      id: '2',
      title: '中国央行推出新一轮降准，释放流动性超过1万亿',
      summary: '中国人民银行宣布下调金融机构存款准备金率0.5个百分点，将释放长期资金约1万亿元，支持实体经济发展。',
      timestamp: '2024-09-23 16:30',
      heat: 94,
      impact: 'high',
      category: 'policy',
      tags: ['央行', '降准', '流动性'],
      sentiment: 75,
      relatedAssets: ['A股', '人民币', '债券'],
      views: 10256,
      comments: 426,
      likes: 285
    },
    {
      id: '3',
      title: '全球能源危机加剧，原油价格创近五年新高',
      summary: '受地缘政治冲突和供应链中断影响，全球原油价格持续上涨，布伦特原油一度突破110美元/桶，创近五年新高。',
      timestamp: '2024-09-24 09:15',
      heat: 92,
      impact: 'high',
      category: 'market',
      tags: ['原油', '能源危机', '通胀风险'],
      sentiment: -60,
      relatedAssets: ['原油', '能源股', '通货膨胀'],
      views: 9874,
      comments: 385,
      likes: 142
    },
    {
      id: '4',
      title: '科技巨头财报集体超预期，AI投资成效显现',
      summary: '多家科技巨头发布2024年第三季度财报，业绩普遍超出市场预期，特别是在AI相关业务上的投资已经开始显现出成效。',
      timestamp: '2024-09-22 21:45',
      heat: 90,
      impact: 'medium',
      category: 'company',
      tags: ['科技股', '财报季', '人工智能'],
      sentiment: 85,
      relatedAssets: ['纳斯达克', '科技股', 'AI概念股'],
      views: 8962,
      comments: 312,
      likes: 246
    },
    {
      id: '5',
      title: '欧元区通胀数据好于预期，欧央行降息预期升温',
      summary: '欧元区9月CPI同比上涨2.3%，低于预期的2.5%，核心CPI同比上涨2.2%。通胀数据好于预期，市场对欧央行10月降息的预期升温。',
      timestamp: '2024-09-21 14:20',
      heat: 85,
      impact: 'medium',
      category: 'data',
      tags: ['欧元区', '通胀', '欧央行'],
      sentiment: 40,
      relatedAssets: ['欧元', '欧股', '欧债'],
      views: 7125,
      comments: 241,
      likes: 184
    }
  ],
  policy: [
    {
      id: '101',
      title: '美联储宣布加息25个基点，市场波动加剧',
      summary: '美联储于本周三宣布加息25个基点，这是2024年首次加息，并暗示年内可能还会有1-2次加息。',
      timestamp: '2024-09-25 22:00',
      heat: 98,
      category: 'policy',
      tags: ['美联储', '加息', '货币政策']
    },
    {
      id: '102',
      title: '中国央行推出新一轮降准，释放流动性超过1万亿',
      summary: '中国人民银行宣布下调金融机构存款准备金率0.5个百分点，将释放长期资金约1万亿元。',
      timestamp: '2024-09-23 16:30',
      heat: 94,
      category: 'policy',
      tags: ['央行', '降准', '流动性']
    },
    {
      id: '103',
      title: '欧央行暗示年内或将再次降息',
      summary: '欧洲央行行长拉加德在讲话中表示，如果通胀持续降低，欧央行将考虑年内再次降息。',
      timestamp: '2024-09-20 15:45',
      heat: 82,
      category: 'policy',
      tags: ['欧央行', '降息', '拉加德']
    },
    {
      id: '104',
      title: '日本央行结束负利率政策，日元大幅升值',
      summary: '日本央行宣布将基准利率上调至0.1%，正式结束长达多年的负利率政策，日元兑美元汇率大幅升值。',
      timestamp: '2024-09-19 10:30',
      heat: 80,
      category: 'policy',
      tags: ['日本央行', '负利率', '日元']
    }
  ],
  market: [
    {
      id: '201',
      title: '全球能源危机加剧，原油价格创近五年新高',
      summary: '受地缘政治冲突和供应链中断影响，全球原油价格持续上涨，布伦特原油一度突破110美元/桶。',
      timestamp: '2024-09-24 09:15',
      heat: 92,
      category: 'market',
      tags: ['原油', '能源危机', '通胀风险']
    },
    {
      id: '202',
      title: '美股高估值引发担忧，市场调整风险增加',
      summary: '多家投行警告美股估值过高，特别是科技股可能面临调整风险，建议投资者适当降低仓位。',
      timestamp: '2024-09-22 16:40',
      heat: 84,
      category: 'market',
      tags: ['美股', '估值', '调整风险']
    },
    {
      id: '203',
      title: '黄金突破2500美元/盎司，创历史新高',
      summary: '受全球经济不确定性和通胀担忧影响，黄金价格持续上涨，一度突破2500美元/盎司，创历史新高。',
      timestamp: '2024-09-21 11:20',
      heat: 79,
      category: 'market',
      tags: ['黄金', '避险', '通胀']
    },
    {
      id: '204',
      title: '比特币再次突破8万美元，加密货币市场全面走强',
      summary: '受机构投资增加和监管环境改善影响，比特币价格再次突破8万美元关口，带动整个加密货币市场上涨。',
      timestamp: '2024-09-20 22:15',
      heat: 76,
      category: 'market',
      tags: ['比特币', '加密货币', '数字资产']
    }
  ],
  company: [
    {
      id: '301',
      title: '科技巨头财报集体超预期，AI投资成效显现',
      summary: '多家科技巨头发布2024年第三季度财报，业绩普遍超出市场预期，特别是在AI相关业务上的投资已经开始显现出成效。',
      timestamp: '2024-09-22 21:45',
      heat: 90,
      category: 'company',
      tags: ['科技股', '财报季', '人工智能']
    },
    {
      id: '302',
      title: '特斯拉宣布推出全新车型，预计明年量产',
      summary: '特斯拉在新品发布会上宣布推出一款全新入门级电动车型，售价约为2.5万美元，预计2025年开始量产。',
      timestamp: '2024-09-21 20:30',
      heat: 82,
      category: 'company',
      tags: ['特斯拉', '电动汽车', '新品发布']
    },
    {
      id: '303',
      title: '阿里巴巴宣布新一轮回购计划，总额250亿美元',
      summary: '阿里巴巴集团宣布新一轮股票回购计划，总额高达250亿美元，这是该公司历史上最大规模的回购计划。',
      timestamp: '2024-09-20 09:00',
      heat: 78,
      category: 'company',
      tags: ['阿里巴巴', '股票回购', '中概股']
    },
    {
      id: '304',
      title: '英伟达宣布下一代GPU芯片计划，算力提升超80%',
      summary: '英伟达CEO黄仁勋宣布下一代GPU芯片研发计划，预计算力较当前产品提升超过80%，将于明年发布。',
      timestamp: '2024-09-18 23:40',
      heat: 85,
      category: 'company',
      tags: ['英伟达', 'GPU', '芯片']
    }
  ],
  data: [
    {
      id: '401',
      title: '欧元区通胀数据好于预期，欧央行降息预期升温',
      summary: '欧元区9月CPI同比上涨2.3%，低于预期的2.5%，核心CPI同比上涨2.2%。通胀数据好于预期，市场对欧央行10月降息的预期升温。',
      timestamp: '2024-09-21 14:20',
      heat: 85,
      category: 'data',
      tags: ['欧元区', '通胀', '欧央行']
    },
    {
      id: '402',
      title: '中国8月PMI数据回升，经济复苏迹象显现',
      summary: '中国8月官方制造业PMI为50.2，非制造业PMI为51.7，均高于预期且处于扩张区间，表明经济复苏迹象显现。',
      timestamp: '2024-09-19 10:00',
      heat: 83,
      category: 'data',
      tags: ['中国', 'PMI', '经济复苏']
    },
    {
      id: '403',
      title: '美国8月非农就业数据好于预期，失业率小幅下降',
      summary: '美国8月非农就业人数增加22.8万，好于预期的18万；失业率降至3.8%，好于预期的3.9%。就业市场依然强劲。',
      timestamp: '2024-09-17 22:30',
      heat: 80,
      category: 'data',
      tags: ['美国', '非农就业', '失业率']
    },
    {
      id: '404',
      title: '日本GDP二季度终值上修，但通缩压力仍存',
      summary: '日本二季度GDP环比终值上修至0.8%，高于初值的0.7%。但通胀压力不足，核心CPI仅上涨1.8%，低于央行2%的目标。',
      timestamp: '2024-09-15 08:45',
      heat: 75,
      category: 'data',
      tags: ['日本', 'GDP', '通缩']
    }
  ]
};

// 市场热度指标数据
export interface HeatIndexItem {
  title: string;
  value: number;
  icon: any; // React节点类型
  color: string;
  tooltip?: string;
}

// 市场情绪和影响类型定义
export type MarketSentiment = 'positive' | 'neutral' | 'negative';
export type ImpactLevel = 'high' | 'medium' | 'low';

// 获取热点详情服务函数
export const getHotTopicById = (id: string): HotTopicItem | undefined => {
  // 在所有分类中查找匹配ID的热点
  for (const category in hotTopicsData) {
    const found = (hotTopicsData as any)[category].find((topic: HotTopicItem) => topic.id === id);
    if (found) {
      return found;
    }
  }
  return undefined;
};

// 按热度排序的热点
export const getTopHotTopics = (limit: number = 5): HotTopicItem[] => {
  // 将所有热点合并并按热度排序
  let allTopics: HotTopicItem[] = [];
  for (const category in hotTopicsData) {
    allTopics = [...allTopics, ...(hotTopicsData as any)[category]];
  }
  
  // 去重
  const uniqueTopics = allTopics.filter((topic, index, self) =>
    index === self.findIndex(t => t.id === topic.id)
  );
  
  // 按热度排序并返回前N条
  return uniqueTopics
    .sort((a, b) => b.heat - a.heat)
    .slice(0, limit);
};

// 获取最近的热点
export const getRecentHotTopics = (limit: number = 5): HotTopicItem[] => {
  // 将所有热点合并并按时间排序
  let allTopics: HotTopicItem[] = [];
  for (const category in hotTopicsData) {
    allTopics = [...allTopics, ...(hotTopicsData as any)[category]];
  }
  
  // 去重
  const uniqueTopics = allTopics.filter((topic, index, self) =>
    index === self.findIndex(t => t.id === topic.id)
  );
  
  // 按时间排序并返回最近的N条
  return uniqueTopics
    .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
    .slice(0, limit);
};

// 按类别获取热点
export const getHotTopicsByCategory = (category: keyof HotTopicsData, limit?: number): HotTopicItem[] => {
  const topics = hotTopicsData[category];
  return limit ? topics.slice(0, limit) : topics;
};

// 搜索热点
export const searchHotTopics = (keyword: string): HotTopicItem[] => {
  if (!keyword.trim()) return [];
  
  const lowerKeyword = keyword.toLowerCase();
  let results: HotTopicItem[] = [];
  
  for (const category in hotTopicsData) {
    const matches = (hotTopicsData as any)[category].filter((topic: HotTopicItem) => {
      return (
        topic.title.toLowerCase().includes(lowerKeyword) ||
        (topic.summary && topic.summary.toLowerCase().includes(lowerKeyword)) ||
        (topic.tags && topic.tags.some(tag => tag.toLowerCase().includes(lowerKeyword)))
      );
    });
    
    results = [...results, ...matches];
  }
  
  // 去重
  return results.filter((topic, index, self) =>
    index === self.findIndex(t => t.id === topic.id)
  );
};

// 默认导出
export default {
  hotTopicsData,
  expertOpinionsData,
  getHotTopicById,
  getTopHotTopics,
  getRecentHotTopics,
  getHotTopicsByCategory,
  searchHotTopics
};