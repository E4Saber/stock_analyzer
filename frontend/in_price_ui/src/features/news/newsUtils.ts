import { NewsDetail } from './NewsDetailModal';

// 通用市场消息生成器 - 用于扩展弹幕消息
export const generateNewsDetails = (message: string): NewsDetail => {
  // 从消息中提取时间和标题
  const timeMatch = message.match(/\[(.*?)\]/);
  const time = timeMatch ? timeMatch[1] : "未知时间";
  const title = timeMatch ? message.replace(timeMatch[0], '').trim() : message;
  
  // 根据标题内容判断涨跌和影响
  const isPositive = /上涨|走强|涨停|高开|增长|活跃|上升|利好/.test(title);
  const isNegative = /下跌|走弱|跌停|低开|下降|利空|震荡|低迷/.test(title);
  const change = isPositive ? Math.random() * 5 + 0.5 : (isNegative ? -(Math.random() * 5 + 0.5) : 0);
  const impact = isPositive ? 'positive' : (isNegative ? 'negative' : 'neutral');
  
  // 创建相关股票
  const relatedStocks: Array<{code: string; name: string; change: number}> = [];
  
  // 从标题中提取可能的股票名称
  const stockNameMatch = title.match(/([\u4e00-\u9fa5]{2,4}(?:控股|证券|银行|医药|科技|集团|股份|时代|汽车|通讯|绿能))/g);
  
  if (stockNameMatch) {
    stockNameMatch.forEach(name => {
      // 生成随机股票代码和涨跌幅
      const isShanghai = Math.random() > 0.5;
      const codePrefix = isShanghai ? '60' : '00';
      const codeSuffix = Math.floor(Math.random() * 10000).toString().padStart(4, '0');
      const stockCode = codePrefix + codeSuffix;
      
      // 股票涨跌幅跟随整体趋势，但有随机波动
      const stockChange = change + (Math.random() * 2 - 1);
      
      relatedStocks.push({
        code: stockCode,
        name,
        change: parseFloat(stockChange.toFixed(2))
      });
    });
  }
  
  // 如果没有提取到股票，可能是行业板块
  if (relatedStocks.length === 0) {
    const sectorMatch = title.match(/([\u4e00-\u9fa5]{2,4}(?:板块|概念|领域|行业))/g);
    if (sectorMatch) {
      // 为板块添加2-3只相关股票
      const stockCount = Math.floor(Math.random() * 2) + 2;
      const sectorName = sectorMatch[0].replace(/(板块|概念|领域|行业)/g, '');
      
      const stockNames = [
        `${sectorName}龙头股`,
        `${sectorName}优质股`,
        `${sectorName}新星`
      ];
      
      for(let i = 0; i < stockCount; i++) {
        const isShanghai = Math.random() > 0.5;
        const codePrefix = isShanghai ? '60' : '00';
        const codeSuffix = Math.floor(Math.random() * 10000).toString().padStart(4, '0');
        const stockCode = codePrefix + codeSuffix;
        
        const stockChange = change + (Math.random() * 3 - 1.5);
        
        relatedStocks.push({
          code: stockCode,
          name: stockNames[i] || `${sectorName}股${i+1}`,
          change: parseFloat(stockChange.toFixed(2))
        });
      }
    }
  }
  
  // 生成详细内容
  let content = "";
  if (isPositive) {
    content = `今日${title}，市场情绪高涨。分析师认为，这主要受到近期政策利好和资金面改善的推动。机构投资者对该板块的未来发展持积极态度。`;
  } else if (isNegative) {
    content = `今日${title}，投资者信心受挫。业内专家分析，这可能与近期市场风险偏好下降及行业基本面变化有关。短期内可能仍有调整压力。`;
  } else {
    content = `市场消息：${title}。分析人士指出，投资者可关注后续政策动向及行业发展趋势，把握结构性机会。`;
  }
  
  // 随机生成消息来源
  const sources = ["证券时报", "上海证券报", "中国证券报", "金融时报", "财经日报", "市场观察", "投资参考"];
  const randomSource = sources[Math.floor(Math.random() * sources.length)];
  
  return {
    time,
    title,
    content,
    change: parseFloat(change.toFixed(2)),
    impact,
    relatedStocks,
    source: randomSource
  };
};