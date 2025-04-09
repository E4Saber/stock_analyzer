import React, { useState } from 'react';
import { 
  Typography, 
  Card, 
  Row, 
  Col, 
  Tabs, 
  List, 
  Space, 
  Button, 
  Badge,
  Input
} from 'antd';
import { 
  FireOutlined, 
  GlobalOutlined,
  BankOutlined,
  LineChartOutlined,
  BuildOutlined,
  BarChartOutlined,
  BellOutlined,
  SearchOutlined,
  ShareAltOutlined,
} from '@ant-design/icons';

// 导入组件
import HotTopicCard, { HotTopicItem } from '../components/HotTopicCard';
import HotTopicCarousel from '../components//HotTopicCarousel';
import HeatIndexes from '../components//HeatIndexes';
import HotTopicTimeline from '../components//HotTopicTimeline';
import ExpertOpinions from '../components//ExpertOpinions';
import HotTopicDetail from '../components//HotTopicDetail';

// 导入数据服务
import { 
  hotTopicsData, 
  expertOpinionsData, 
  getHotTopicById
} from '../service/hotTopicsData';

// 导入样式
import './HotTopicsPage.css';

const { Title } = Typography;
const { TabPane } = Tabs;
const { Search } = Input;

// 热点页面组件
const HotTopicsPage: React.FC = () => {
  // 状态管理
  const [activeTab, setActiveTab] = useState('trending');
  const [selectedTopic, setSelectedTopic] = useState<HotTopicItem | null>(null);
  const [detailModalVisible, setDetailModalVisible] = useState(false);
  const [searchKeyword, setSearchKeyword] = useState('');
  const [searchResults, setSearchResults] = useState<HotTopicItem[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  
  // 处理标签页切换
  const handleTabChange = (key: string) => {
    setActiveTab(key);
    
    // 如果正在搜索，重置搜索状态
    if (isSearching) {
      setIsSearching(false);
      setSearchKeyword('');
      setSearchResults([]);
    }
  };
  
  // 打开热点详情
  const handleOpenTopicDetail = (topic: HotTopicItem) => {
    setSelectedTopic(topic);
    setDetailModalVisible(true);
  };
  
  // 关闭热点详情
  const handleCloseTopicDetail = () => {
    setDetailModalVisible(false);
  };
  
  // 处理搜索
  const handleSearch = (value: string) => {
    if (!value.trim()) {
      setIsSearching(false);
      setSearchResults([]);
      return;
    }
    
    setSearchKeyword(value);
    setIsSearching(true);
    
    // 简单搜索实现
    const results: HotTopicItem[] = [];
    Object.values(hotTopicsData).forEach(topicList => {
      topicList.forEach(topic => {
        if (
          topic.title.toLowerCase().includes(value.toLowerCase()) ||
          (topic.summary && topic.summary.toLowerCase().includes(value.toLowerCase())) ||
          (topic.tags && topic.tags.some(tag => tag.toLowerCase().includes(value.toLowerCase())))
        ) {
          results.push(topic);
        }
      });
    });
    
    // 移除重复项
    const uniqueResults = results.filter((topic, index, self) =>
      index === self.findIndex(t => t.id === topic.id)
    );
    
    setSearchResults(uniqueResults);
  };
  
  // 获取标签页图标
  const getTabIcon = (category: string) => {
    switch (category) {
      case 'trending':
        return <FireOutlined />;
      case 'policy':
        return <BankOutlined />;
      case 'market':
        return <LineChartOutlined />;
      case 'company':
        return <BuildOutlined />;
      case 'data':
        return <BarChartOutlined />;
      default:
        return <GlobalOutlined />;
    }
  };
  
  // 渲染标签页标题
  const renderTabTitle = (title: string, category: string, count: number) => {
    return (
      <span>
        <Space size="small">
          {getTabIcon(category)}
          {title}
          <Badge count={count} style={{ backgroundColor: '#1890ff' }} />
        </Space>
      </span>
    );
  };
  
  // 渲染搜索结果
  const renderSearchResults = () => {
    if (!isSearching) return null;
    
    return (
      <Card title={`搜索结果: "${searchKeyword}" (${searchResults.length})`} size="small">
        {searchResults.length > 0 ? (
          <List
            dataSource={searchResults}
            renderItem={(item) => (
              <List.Item key={item.id} style={{ padding: 0 }}>
                <HotTopicCard 
                  topic={item} 
                  onClick={handleOpenTopicDetail}
                />
              </List.Item>
            )}
          />
        ) : (
          <div className="empty-state">
            <p>未找到相关热点</p>
            <Button type="primary" onClick={() => setIsSearching(false)} size="small">
              返回热点列表
            </Button>
          </div>
        )}
      </Card>
    );
  };
  
  // 更紧凑的内容区布局
  const renderMainContent = () => {
    return (
      <Row gutter={[8, 8]} className="row-gutter-reduced">
        {/* 上部分区域：热点轮播和热度指标 */}
        <Col span={16}>
          <HotTopicCarousel 
            topics={hotTopicsData.trending} 
            onViewDetail={(id) => {
              const topic = getHotTopicById(id);
              if (topic) {
                handleOpenTopicDetail(topic);
              }
            }}
          />
        </Col>
        <Col span={8}>
          <HeatIndexes />
        </Col>
        
        {/* 中部区域：主要内容和时间轴 */}
        <Col xs={24} md={16}>
          <Card size="small" bodyStyle={{ padding: '8px' }}>
            <Tabs 
              defaultActiveKey="trending" 
              onChange={handleTabChange}
              size="small"
              className="hot-topics-tabs"
            >
              <TabPane 
                tab={renderTabTitle('热门榜单', 'trending', hotTopicsData.trending.length)} 
                key="trending"
              >
                <List
                  dataSource={hotTopicsData.trending}
                  renderItem={(item) => (
                    <List.Item key={item.id} style={{ padding: 0 }}>
                      <HotTopicCard 
                        topic={item} 
                        size="default" // 从large改为default，更紧凑
                        onClick={handleOpenTopicDetail}
                      />
                    </List.Item>
                  )}
                />
              </TabPane>
              
              <TabPane 
                tab={renderTabTitle('政策动向', 'policy', hotTopicsData.policy.length)} 
                key="policy"
              >
                <List
                  dataSource={hotTopicsData.policy}
                  renderItem={(item) => (
                    <List.Item key={item.id} style={{ padding: 0 }}>
                      <HotTopicCard 
                        topic={item}
                        onClick={handleOpenTopicDetail}
                      />
                    </List.Item>
                  )}
                />
              </TabPane>
              
              <TabPane 
                tab={renderTabTitle('市场波动', 'market', hotTopicsData.market.length)} 
                key="market"
              >
                <List
                  dataSource={hotTopicsData.market}
                  renderItem={(item) => (
                    <List.Item key={item.id} style={{ padding: 0 }}>
                      <HotTopicCard 
                        topic={item}
                        onClick={handleOpenTopicDetail}
                      />
                    </List.Item>
                  )}
                />
              </TabPane>
              
              <TabPane 
                tab={renderTabTitle('公司热点', 'company', hotTopicsData.company.length)} 
                key="company"
              >
                <List
                  dataSource={hotTopicsData.company}
                  renderItem={(item) => (
                    <List.Item key={item.id} style={{ padding: 0 }}>
                      <HotTopicCard 
                        topic={item}
                        onClick={handleOpenTopicDetail}
                      />
                    </List.Item>
                  )}
                />
              </TabPane>
              
              <TabPane 
                tab={renderTabTitle('经济数据', 'data', hotTopicsData.data.length)} 
                key="data"
              >
                <List
                  dataSource={hotTopicsData.data}
                  renderItem={(item) => (
                    <List.Item key={item.id} style={{ padding: 0 }}>
                      <HotTopicCard 
                        topic={item}
                        onClick={handleOpenTopicDetail}
                      />
                    </List.Item>
                  )}
                />
              </TabPane>
            </Tabs>
          </Card>
        </Col>
        
        <Col xs={24} md={8}>
          <div>
            <HotTopicTimeline 
              topics={hotTopicsData.trending}
              onClickTopic={handleOpenTopicDetail}
              limit={6} // 增加显示数量
            />
          </div>
          
          <div style={{ marginTop: 8 }}>
            <ExpertOpinions 
              opinions={expertOpinionsData}
              onViewMore={() => console.log('查看更多专家观点')}
              onViewOpinion={(id) => console.log('查看专家观点', id)}
              className="expert-opinions-card"
              showMore={false} // 不显示"查看更多"按钮，节省空间
            />
          </div>
        </Col>
      </Row>
    );
  };
  
  return (
    <div className="page-content">
      {/* 页面标题和操作区 - 更紧凑的设计 */}
      <div className="page-title-area">
        <Title level={3} style={{ margin: 0 }}>市场热点</Title>
        <Space className="action-buttons" size="small">
          <Search 
            placeholder="搜索热点" 
            allowClear
            enterButton={<SearchOutlined />}
            className="topic-search"
            onSearch={handleSearch}
            size="small"
            onChange={e => {
              if (!e.target.value) {
                setIsSearching(false);
                setSearchResults([]);
              }
            }}
          />
          <Button icon={<BellOutlined />} size="small">订阅</Button>
          <Button icon={<ShareAltOutlined />} size="small">分享</Button>
        </Space>
      </div>
      
      {/* 搜索结果区域 */}
      {isSearching ? renderSearchResults() : renderMainContent()}
      
      {/* 热点详情模态框 */}
      <HotTopicDetail
        topic={selectedTopic}
        visible={detailModalVisible}
        onClose={handleCloseTopicDetail}
      />
    </div>
  );
};

export default HotTopicsPage;