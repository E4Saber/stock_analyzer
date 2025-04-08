import React, { useState, useEffect, useRef } from 'react';
import { Input, Tag, Avatar, Switch } from 'antd';
import { 
  StockOutlined, 
  GlobalOutlined, 
  FireOutlined, 
  SearchOutlined,
  LineChartOutlined,
  CommentOutlined,
  UserOutlined,
  BulbOutlined,
  BulbFilled
} from '@ant-design/icons';
import NewsDetailModal, { NewsDetail } from '../news/NewsDetailModal';
import { generateNewsDetails } from '../news/newsUtils';

const { Search } = Input;

const InPriceHomepage: React.FC = () => {
  const [activeNav, setActiveNav] = useState<string>('market');
  const [darkMode, setDarkMode] = useState<boolean>(false);
  const newsContainerRef = useRef<HTMLDivElement>(null);
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

  // 主题切换处理函数
  const toggleTheme = () => {
    setDarkMode(!darkMode);
  };

  // 监听主题变化并应用到文档
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', darkMode ? 'dark' : 'light');
  }, [darkMode]);

  // 热点区域弹幕效果 - 增加点击事件支持
  useEffect(() => {
    if (!newsContainerRef.current) return;
    
    const container = newsContainerRef.current;
    const containerWidth = container.clientWidth;
    
    // 清除现有内容
    while (container.firstChild) {
      container.removeChild(container.firstChild);
    }
    
    // 创建轨道
    const trackCount = 3; // 3条轨道
    const trackHeight = container.clientHeight / trackCount;
    const tracks = [];
    
    for (let i = 0; i < trackCount; i++) {
      const track = document.createElement('div');
      track.className = 'danmaku-track';
      // 只为第一条轨道添加额外的上边距
      const topPosition = i === 0 
                        ? i * trackHeight + 2 // 第一条轨道有10px的上边距
                        : i * trackHeight;     // 其他轨道保持原样

      track.style.top = `${topPosition}px`;
      container.appendChild(track);
      tracks.push({
        element: track,
        lastSendTime: 0, // 上次发送弹幕的时间
        busy: false, // 轨道是否忙碌
        currentSpeed: 40, // 轨道当前速度 - 为每个轨道设置一个固定速度
      });
    }
    
    // 为每个轨道设置固定但略微不同的速度
    tracks[0].currentSpeed = 38;
    tracks[1].currentSpeed = 40;
    tracks[2].currentSpeed = 42;
    
    // 创建一个消息对象
    const createMessageObj = (message, trackIndex) => {
      // 使用轨道的固定速度而不是随机速度
      return {
        text: message,
        speed: tracks[trackIndex].currentSpeed, // 使用轨道预设的速度
      };
    };
    
    // 随机打乱消息顺序
    const shuffleMessages = [...hotMessages].sort(() => Math.random() - 0.5);
    const messageQueue = shuffleMessages.map(msg => ({ text: msg })); // 不预设速度
    
    // 向指定轨道发送弹幕
    const sendToTrack = (trackIndex, message) => {
      const track = tracks[trackIndex];
      const trackElement = track.element;
      
      // 创建弹幕元素
      const item = document.createElement('div');
      item.className = 'news-item';
      item.innerText = message.text;
      item.style.cursor = 'pointer'; // 添加指针样式表示可点击
      
      // 添加点击事件
      item.addEventListener('click', () => {
        openNewsModal(message.text);
      });
      
      // 添加悬停效果类
      item.addEventListener('mouseenter', () => {
        item.classList.add('news-item-hover');
      });
      
      item.addEventListener('mouseleave', () => {
        item.classList.remove('news-item-hover');
      });
      
      // 从右侧开始，位于容器外
      item.style.left = `${containerWidth}px`; 
      
      trackElement.appendChild(item);
      
      // 获取宽度
      const itemWidth = item.offsetWidth;
      
      // 计算运动时间 - 增加额外距离确保完全移出
      const speed = track.currentSpeed; // px/s
      // 关键改进：增加额外距离确保完全移出
      const extraDistance = itemWidth * 1.5; // 确保有足够的距离完全移出
      const distance = containerWidth + itemWidth + extraDistance;
      const duration = distance / speed;
      
      // 设置轨道为忙碌状态
      track.busy = true;
      
      // 使用CSS变换实现平滑移动
      // 关键改进：将终点位置设置得更远
      item.style.transition = `left ${duration}s linear`;
      item.style.left = `-${itemWidth + extraDistance}px`; // 移动到更远的位置
      
      // 计算下一条弹幕可以发送的时间
      const itemEnterTime = itemWidth / speed; // 弹幕完全进入屏幕的时间
      const minInterval = 1.2;  // 最小间隔时间
      const randomInterval = minInterval + Math.random() * 1.8; // 1.2~3秒的随机间隔
      const nextSendDelay = itemEnterTime + randomInterval;
      
      // 更新轨道状态
      track.lastSendTime = Date.now();
      
      // 设置定时器，延迟后允许下一条弹幕
      setTimeout(() => {
        track.busy = false;
      }, nextSendDelay * 1000);
      
      // 动画结束后移除元素 - 确保在完全移出后再移除
      // 关键改进：显著延长清除时间
      setTimeout(() => {
        if (trackElement.contains(item)) {
          trackElement.removeChild(item);
        }
      }, (duration + 1) * 1000); // 增加1秒缓冲确保完全移出
      
      return nextSendDelay;
    };
    
    // 尝试发送一条弹幕
    const tryToSendMessage = () => {
      if (messageQueue.length === 0) {
        // 如果队列为空，补充消息
        messageQueue.push(...shuffleMessages.map(msg => ({ text: msg })));
      }
      
      // 查找可用轨道
      const availableTracks = tracks.filter(track => !track.busy);
      
      if (availableTracks.length > 0) {
        // 随机选择一条可用轨道
        const randomIndex = Math.floor(Math.random() * availableTracks.length);
        const trackIndex = tracks.indexOf(availableTracks[randomIndex]);
        
        // 从队列中取出一条消息，并设置该轨道的速度
        const messageText = messageQueue.shift();
        const message = createMessageObj(messageText.text, trackIndex);
        
        // 发送弹幕
        const nextSendDelay = sendToTrack(trackIndex, message);
        
        // 随机选择下一条消息的发送时间
        return 800 + Math.random() * 500; // 800~1300ms，减少随机性
      }
      
      // 如果没有可用轨道，稍后再试
      return 500;
    };
    
    // 初始化发送
    let checkInterval: number | null = null;
    
    const checkAndSend = () => {
      const nextCheck = tryToSendMessage();
      checkInterval = setTimeout(checkAndSend, nextCheck) as unknown as number;
    };
    
    // 开始发送
    setTimeout(() => {
      checkAndSend();
    }, 500);
    
    return () => {
      if (checkInterval) {
        clearTimeout(checkInterval);
      }
      
      // 清除所有轨道
      while (container.firstChild) {
        container.removeChild(container.firstChild);
      }
    };
  }, []);

  const handleNavClick = (nav: string) => {
    setActiveNav(nav);
  };

  return (
    <div className="main-container">
      {/* 导航栏 */}
      <header className="inprice-header">
        <div className="inprice-nav">
          <div className="inprice-logo">
            <LineChartOutlined style={{ marginRight: '8px' }} /> In Price
          </div>
          
          <div 
            className={`nav-item ${activeNav === 'macro' ? 'active' : ''}`}
            onClick={() => handleNavClick('macro')}
          >
            <GlobalOutlined style={{ marginRight: '6px' }} /> 宏观
          </div>
          <div 
            className={`nav-item ${activeNav === 'hot' ? 'active' : ''}`}
            onClick={() => handleNavClick('hot')}
          >
            <FireOutlined style={{ marginRight: '6px' }} /> 热点
          </div>
          <div 
            className={`nav-item ${activeNav === 'market' ? 'active' : ''}`}
            onClick={() => handleNavClick('market')}
          >
            <StockOutlined style={{ marginRight: '6px' }} /> 市场
          </div>
          <div 
            className={`nav-item ${activeNav === 'quant' ? 'active' : ''}`}
            onClick={() => handleNavClick('quant')}
          >
            <LineChartOutlined style={{ marginRight: '6px' }} /> 量化
          </div>
          <div 
            className={`nav-item ${activeNav === 'forum' ? 'active' : ''}`}
            onClick={() => handleNavClick('forum')}
          >
            <CommentOutlined style={{ marginRight: '6px' }} /> 论坛
          </div>
        </div>
        
        <div className="right-nav">
          <div className="theme-switcher">
            <Switch
              checked={darkMode}
              onChange={toggleTheme}
              checkedChildren={<BulbFilled />}
              unCheckedChildren={<BulbOutlined />}
              className="theme-switch"
            />
          </div>
          <Avatar 
            size={40} 
            icon={<UserOutlined />} 
            style={{ backgroundColor: '#1890ff', cursor: 'pointer', marginLeft: '16px' }} 
          />
        </div>
      </header>

      {/* 内容区域 */}
      <main className="content-area">
        {/* 搜索区域 */}
        <section className="search-section">
          <div className="search-box">
            <div className="search-input-container">
              <Search 
                placeholder="输入股票名称、代码或关键词" 
                enterButton={<><SearchOutlined /> 搜索</>}
                size="large"
              />
            </div>
            
            <div className="hot-search">
              <span className="hot-search-label">热门搜索:</span>
              {hotSearchTags.map((tag, index) => (
                <Tag 
                  key={index} 
                  className="hot-tag"
                >
                  {tag}
                </Tag>
              ))}
            </div>
          </div>
        </section>
        
        {/* 热点新闻区域 - 弹幕形式 */}
        <section className="news-section">
          <div className="news-container">
            <div className="news-danmaku-container" ref={newsContainerRef}></div>
          </div>
        </section>
      </main>

      {/* 页脚 */}
      <footer className="inprice-footer">
        In Price © 2025 - 专注于价值投资的分析平台
      </footer>

      {/* 使用独立的消息详情Modal组件 */}
      <NewsDetailModal 
        visible={modalVisible} 
        newsDetail={currentNews} 
        onClose={closeNewsModal}
      />
    </div>
  );
};

export default InPriceHomepage;