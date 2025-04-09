// src/features/home/pages/Homepage.tsx
import React, { useState } from 'react';
import SearchSection from '../components/SearchSection';
import NewsSection from '../components/NewsSection';
import NewsDetailModal, { NewsDetail } from '../components/NewsDetailModal';
import { generateNewsDetails } from '../components/newsUtils';

const Homepage: React.FC = () => {
  const [modalVisible, setModalVisible] = useState<boolean>(false);
  const [currentNews, setCurrentNews] = useState<NewsDetail | null>(null);
  
  // 热门搜索标签
  const hotSearchTags: string[] = ['贵州茅台', '宁德时代', '腾讯控股', 'AI芯片', '新能源'];

  // 热点消息
  const hotMessages: string[] = [
    '[09:30] 沪指小幅高开，科技股活跃',
    '[09:35] 贵州茅台突破1800元关口',
    '[09:40] 新能源汽车板块全线上涨',
    '[09:42] 半导体设备概念股受关注',
    '[09:45] 医药板块震荡，恒瑞医药领跌',
    '[09:50] AI芯片概念股持续活跃',
    '[09:55] 券商板块走强，国泰君安涨3%',
    '[10:00] 创业板指数上涨0.8%',
    '[10:05] 稀土永磁概念股表现活跃',
    '[10:10] 银行板块低迷，工商银行跌0.5%',
    '[10:15] 特斯拉中国4月销量同比增长五成',
    '[10:20] 光伏概念股走强，隆基绿能涨3.2%',
    '[10:25] 通信板块表现活跃，中兴通讯涨停',
    '[10:30] 国防军工板块集体上涨',
    '[10:35] 消费电子领域获机构关注',
    '[10:40] 美股期货走高，道指期货涨0.5%'
  ];

  // 打开弹窗显示详细消息
  const openNewsModal = (message: string) => {
    const newsDetail = generateNewsDetails(message);
    setCurrentNews(newsDetail);
    setModalVisible(true);
  };

  // 关闭弹窗
  const closeNewsModal = () => {
    setModalVisible(false);
  };

  return (
    <div className="page-content">
      {/* 搜索区域 */}
      <SearchSection hotSearchTags={hotSearchTags} />
      
      {/* 热点新闻区域 */}
      <NewsSection 
        hotMessages={hotMessages} 
        onOpenNewsModal={openNewsModal} 
      />

      {/* 使用独立的消息详情Modal组件 */}
      <NewsDetailModal 
        visible={modalVisible} 
        newsDetail={currentNews} 
        onClose={closeNewsModal}
      />
    </div>
  );
};

export default Homepage;