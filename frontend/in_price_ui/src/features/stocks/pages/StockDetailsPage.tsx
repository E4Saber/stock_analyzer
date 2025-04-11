// src/features/stocks/pages/StockDetailsPage.tsx
import React, { useState, useEffect } from 'react';
import { Tabs, Card, Row, Col, Statistic, Tag, Button, Table, Typography, Space, Divider } from 'antd';
import { 
  ArrowUpOutlined, 
  ArrowDownOutlined, 
  LineChartOutlined, 
  FileTextOutlined,
  TeamOutlined,
  CommentOutlined,
  StarOutlined,
  ShareAltOutlined,
  InfoCircleOutlined
} from '@ant-design/icons';
import type { TabsProps } from 'antd';
import { useParams, useNavigate } from 'react-router-dom';
import './StockDetailsPage.css';

// 假数据，实际应用中应从API获取
const mockStockData = {
  code: '600519',
  name: '贵州茅台',
  current: 569.00,
  change: 16.22,
  changePercent: 2.85,
  high: 571.32,
  low: 565.31,
  volume: '60.27亿',
  marketCap: '614.49万亿',
  pe: 13.85,
  pb: 6.19,
  metrics: [
    { name: '今年', value: 568.85 },
    { name: '昨收', value: 565.31 },
    { name: '盘中峰值', value: 103.00 },
    { name: '52周高', value: 571.32 },
    { name: '52周低', value: '-' },
    { name: '市值', value: '614.49万亿' },
    { name: '成交量', value: '2.98万亿' },
    { name: '流通市值', value: '1051亿' },
    { name: '总营收', value: '4.53' },
    { name: '流通股本', value: '11亿' },
    { name: '股息', value: '3.46' },
    { name: '股息收益率', value: '0.70%' },
    { name: '市盈率动态', value: '13.85' }
  ],
  relatedNews: [
    '茅台一季度营收增长15.3%，超出市场预期',
    '贵州茅台推出新品，市场反应积极',
    '酒类股普遍上涨，茅台领涨白酒板块',
    '机构看好茅台长期发展，目标价上调至650元'
  ],
  comments: [
    {
      author: '投资者A',
      content: '茅台作为白酒龙头，具有极强的定价权和品牌溢价，长期持有价值明显。',
      time: '2025-04-10 15:32'
    },
    {
      author: '分析师B',
      content: '一季度数据表现强劲，但需关注消费降级风险对高端白酒的影响。',
      time: '2025-04-10 14:56'
    }
  ],
  hotTags: ['白酒龙头', '茅台新品', '一季报', '高股息', '机构推荐']
};

const { Title, Text, Paragraph } = Typography;
const { TabPane } = Tabs;

// 定义指标Tab的内容
const MetricsTabContent: React.FC<{ stockData: any }> = ({ stockData }) => {
  // 将指标数据分为几列显示
  const leftCol = stockData.metrics.slice(0, 7);
  const rightCol = stockData.metrics.slice(7);
  
  return (
    <Row gutter={[16, 8]}>
      <Col xs={24} md={12}>
        {leftCol.map((item, index) => (
          <Row key={index} className="metric-row">
            <Col span={12} className="metric-label">{item.name}</Col>
            <Col span={12} className="metric-value">{item.value}</Col>
          </Row>
        ))}
      </Col>
      <Col xs={24} md={12}>
        {rightCol.map((item, index) => (
          <Row key={index} className="metric-row">
            <Col span={12} className="metric-label">{item.name}</Col>
            <Col span={12} className="metric-value">{item.value}</Col>
          </Row>
        ))}
      </Col>
    </Row>
  );
};

// 定义财报Tab的内容
const FinancialReportTabContent: React.FC = () => {
  return (
    <div className="financial-report-container">
      <Row gutter={[16, 16]}>
        <Col span={8}>
          <Card title="营收（亿元）" size="small">
            <Statistic value={1715.28} precision={2} />
            <div className="growth-rate positive">
              <ArrowUpOutlined /> 15.3% 同比
            </div>
          </Card>
        </Col>
        <Col span={8}>
          <Card title="净利润（亿元）" size="small">
            <Statistic value={618.53} precision={2} />
            <div className="growth-rate positive">
              <ArrowUpOutlined /> 13.9% 同比
            </div>
          </Card>
        </Col>
        <Col span={8}>
          <Card title="毛利率" size="small">
            <Statistic value={91.7} precision={1} suffix="%" />
            <div className="growth-rate negative">
              <ArrowDownOutlined /> 0.3% 同比
            </div>
          </Card>
        </Col>
      </Row>
      
      <Divider />
      
      <Title level={5}>季度财务数据趋势</Title>
      <Paragraph>
        此处将显示季度财务数据的图表，展示营收、利润等关键指标的趋势变化。
      </Paragraph>
    </div>
  );
};

// 定义公司Tab的内容
const CompanyTabContent: React.FC = () => {
  return (
    <div className="company-info-container">
      <Title level={5}>公司简介</Title>
      <Paragraph>
        贵州茅台酒股份有限公司是中国的大型上市公司，专注于生产和销售茅台酒等酒类产品。
        公司总部位于贵州省仁怀市茅台镇，是中国白酒行业的龙头企业，产品在国内外享有盛誉。
      </Paragraph>
      
      <Title level={5}>主营业务</Title>
      <Paragraph>
        <ul>
          <li>茅台酒及系列酒的生产与销售</li>
          <li>酒类相关产品的研发和营销</li>
          <li>酒文化传播与品牌建设</li>
        </ul>
      </Paragraph>
      
      <Title level={5}>管理层</Title>
      <div className="management-list">
        <p><strong>董事长：</strong> 丁雄军</p>
        <p><strong>总经理：</strong> 李静仁</p>
        <p><strong>财务总监：</strong> 杨波</p>
      </div>
    </div>
  );
};

const StockDetailsPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>('metrics');
  const { stockCode } = useParams<{ stockCode: string }>();
  const navigate = useNavigate();
  const [stockData, setStockData] = useState(mockStockData);
  
  // 实际应用中，这里应该有数据获取逻辑
  useEffect(() => {
    // 获取股票详情数据的API调用
    // fetchStockDetails(stockCode)
    console.log('Fetching details for stock:', stockCode);
    
    // 模拟根据股票代码获取不同数据
    if (stockCode) {
      // 这里可以替换为实际的API调用
      // 模拟数据更新，保持相同的结构但更新股票代码
      setStockData({
        ...mockStockData,
        code: stockCode,
      });
    }
  }, [stockCode]);

  // 处理Tab切换
  const handleTabChange = (key: string) => {
    setActiveTab(key);
  };

  const items: TabsProps['items'] = [
    {
      key: 'metrics',
      label: '价分',
      children: <MetricsTabContent stockData={stockData} />,
      icon: <LineChartOutlined />
    },
    {
      key: 'financial',
      label: '财报',
      children: <FinancialReportTabContent />,
      icon: <FileTextOutlined />
    },
    {
      key: 'company',
      label: '公司',
      children: <CompanyTabContent />,
      icon: <TeamOutlined />
    }
  ];

  // 价格变化是否为正数
  const isPriceUp = mockStockData.change > 0;
  const priceChangeColorClass = isPriceUp ? 'price-up' : 'price-down';
  const PriceArrowIcon = isPriceUp ? ArrowUpOutlined : ArrowDownOutlined;

  return (
    <div className="stock-details-page">
      {/* 股票基本信息区域 */}
      <div className="stock-header">
        <Row gutter={16}>
          {/* 左侧：股票基本信息 */}
          <Col xs={24} md={8}>
            <div className="stock-title">
              <Title level={2}>{stockData.name}</Title>
              <Text type="secondary">{stockData.code}</Text>
            </div>
            
            <div className="stock-price-container">
              <span className={`stock-price ${priceChangeColorClass}`}>
                {stockData.current.toFixed(2)}
              </span>
              <span className={`stock-change ${priceChangeColorClass}`}>
                <PriceArrowIcon /> {stockData.change.toFixed(2)} ({stockData.changePercent.toFixed(2)}%)
              </span>
            </div>
            
            <div className="stock-actions">
              <Button type="primary" icon={<StarOutlined />}>关注</Button>
              <Button icon={<ShareAltOutlined />}>分享</Button>
            </div>
          </Col>
          
          {/* 右侧：主要指标 */}
          <Col xs={24} md={16}>
            <Row gutter={[16, 8]}>
              <Col span={8}>
                <div className="metric-item">
                  <div className="metric-label">今日高</div>
                  <div className="metric-value">{stockData.high}</div>
                </div>
              </Col>
              <Col span={8}>
                <div className="metric-item">
                  <div className="metric-label">今日低</div>
                  <div className="metric-value">{stockData.low}</div>
                </div>
              </Col>
              <Col span={8}>
                <div className="metric-item">
                  <div className="metric-label">昨收</div>
                  <div className="metric-value">{stockData.metrics[1].value}</div>
                </div>
              </Col>
              
              <Col span={8}>
                <div className="metric-item">
                  <div className="metric-label">成交量</div>
                  <div className="metric-value">{stockData.metrics[6].value}</div>
                </div>
              </Col>
              <Col span={8}>
                <div className="metric-item">
                  <div className="metric-label">市值</div>
                  <div className="metric-value">{stockData.metrics[5].value}</div>
                </div>
              </Col>
              <Col span={8}>
                <div className="metric-item">
                  <div className="metric-label">市盈率</div>
                  <div className="metric-value">{stockData.pe}</div>
                </div>
              </Col>
              
              <Col span={8}>
                <div className="metric-item">
                  <div className="metric-label">52周高</div>
                  <div className="metric-value">{stockData.metrics[3].value}</div>
                </div>
              </Col>
              <Col span={8}>
                <div className="metric-item">
                  <div className="metric-label">52周低</div>
                  <div className="metric-value">{stockData.metrics[4].value}</div>
                </div>
              </Col>
              <Col span={8}>
                <div className="metric-item">
                  <div className="metric-label">量比</div>
                  <div className="metric-value">{stockData.metrics[11].value}</div>
                </div>
              </Col>
            </Row>
          </Col>
        </Row>
      </div>
      
      {/* 主要内容区域 */}
      <div className="stock-content">
        <Row gutter={[16, 16]}>
          {/* 左侧内容 */}
          <Col xs={24} md={18}>
            {/* 图表区域 */}
            <Card 
              className="chart-card"
              tabList={[
                {
                  key: 'kline',
                  tab: 'K线图',
                },
                {
                  key: 'minute',
                  tab: '分时图',
                },
                {
                  key: 'week',
                  tab: '周K线',
                },
                {
                  key: 'month',
                  tab: '月K线',
                },
              ]}
            >
              <div className="main-chart">
                <div className="chart-placeholder">
                  {/* 实际项目中这里应该是图表组件 */}
                  <div style={{ height: '300px', background: '#f5f5f5', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    K线图区域
                  </div>
                </div>
              </div>
            </Card>
            
            <Card title="指标图" className="chart-card" style={{ marginTop: '16px' }}>
              <div className="secondary-chart">
                <div className="chart-placeholder">
                  {/* 实际项目中这里应该是图表组件 */}
                  <div style={{ height: '160px', background: '#f5f5f5', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    成交量/MACD等技术指标图区域
                  </div>
                </div>
              </div>
            </Card>
            
            {/* 指标Tab区域 */}
            <Card style={{ marginTop: '16px' }}>
              <Tabs 
                defaultActiveKey="metrics" 
                onChange={handleTabChange}
                items={items}
              />
            </Card>
          </Col>
          
          {/* 右侧内容 */}
          <Col xs={24} md={6}>
            {/* 相关热点新闻 */}
            <Card title="相关热点新闻" className="news-card">
              <ul className="news-list">
                {mockStockData.relatedNews.map((news, index) => (
                  <li key={index} className="news-item">
                    <a href="#">{news}</a>
                  </li>
                ))}
              </ul>
            </Card>
            
            {/* 热点标签 */}
            <Card title="热点标签" className="tags-card" style={{ marginTop: '16px' }}>
              <div className="tags-container">
                {mockStockData.hotTags.map((tag, index) => (
                  <Tag key={index} color="blue" style={{ margin: '4px' }}>{tag}</Tag>
                ))}
              </div>
            </Card>
            
            {/* 评论区 */}
            <Card 
              title={<><CommentOutlined /> 评论</>} 
              extra={<a href="#">发表评论</a>}
              className="comments-card" 
              style={{ marginTop: '16px' }}
            >
              <div className="comments-container">
                {mockStockData.comments.map((comment, index) => (
                  <div key={index} className="comment-item">
                    <div className="comment-header">
                      <span className="comment-author">{comment.author}</span>
                      <span className="comment-time">{comment.time}</span>
                    </div>
                    <div className="comment-content">{comment.content}</div>
                    {index < mockStockData.comments.length - 1 && <Divider style={{ margin: '8px 0' }} />}
                  </div>
                ))}
              </div>
            </Card>
          </Col>
        </Row>
      </div>
    </div>
  );
};

export default StockDetailsPage;