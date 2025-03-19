// src/pages/StockDetailWithAI.tsx
import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { 
  Row, Col, Card, Tabs, Typography, Statistic, Descriptions, Table, 
  Spin, Alert, Tag, Space, Divider
} from 'antd';
import { 
  ArrowUpOutlined, ArrowDownOutlined, 
  InfoCircleOutlined, LineChartOutlined, 
  BarChartOutlined, FileTextOutlined
} from '@ant-design/icons';
import { getStockDetail } from '../services/stockService';
import StockAnalysisPanel from '../components/charts/StockAnalysisPanel';
import { StockData } from '../types/market';
import AIAssistantTrigger from '../components/widgets/AIAssistantTrigger';

const { Title, Text } = Typography;
const { TabPane } = Tabs;

/**
 * 带AI助手的股票详情页面
 */
const StockDetailWithAI: React.FC = () => {
  // 从路由参数获取股票代码
  const { code = '600519' } = useParams<{ code: string }>();
  
  // 状态管理
  const [stockData, setStockData] = useState<StockData | null>(null);
  const [relatedStocks, setRelatedStocks] = useState<StockData[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  
  // 获取数据
  useEffect(() => {
    if (!code) return;
    
    const fetchStockData = async () => {
      setLoading(true);
      try {
        // 获取股票详情
        const response = await getStockDetail(code);
        setStockData(response.stock);
        setRelatedStocks(response.relatedStocks);
        setError(null);
      } catch (err) {
        console.error('获取股票详情失败:', err);
        setError('获取数据失败，请稍后重试');
      } finally {
        setLoading(false);
      }
    };
    
    fetchStockData();
  }, [code]);
  
  // 渲染加载状态
  if (loading && !stockData) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
        <p>正在加载股票数据...</p>
      </div>
    );
  }
  
  // 渲染错误状态
  if (error) {
    return (
      <Alert
        message="数据加载错误"
        description={error}
        type="error"
        showIcon
        style={{ margin: '20px' }}
      />
    );
  }
  
  // 如果没有数据
  if (!stockData) {
    return (
      <Alert
        message="未找到股票"
        description={`未找到代码为 ${code} 的股票数据`}
        type="warning"
        showIcon
        style={{ margin: '20px' }}
      />
    );
  }

  return (
    <div className="stock-detail-container">
      {/* 股票基本信息卡片 */}
      <Card bordered={false} className="stock-info-card">
        <Row gutter={[24, 16]} align="middle">
          <Col xs={24} md={12} lg={8}>
            <Space direction="vertical" size="small" style={{ width: '100%' }}>
              <Title level={2} style={{ margin: 0 }}>
                {stockData.name} 
                <Text type="secondary" style={{ fontSize: '18px', marginLeft: '8px' }}>
                  {stockData.code}
                </Text>
              </Title>
              
              <Space align="center">
                <Text style={{ fontSize: '32px', fontWeight: 'bold', color: stockData.change >= 0 ? '#cf1322' : '#3f8600' }}>
                  {stockData.current.toFixed(2)}
                </Text>
                <Space>
                  <Tag 
                    color={stockData.change >= 0 ? 'red' : 'green'} 
                    style={{ fontSize: '14px', padding: '4px 8px' }}
                  >
                    {stockData.change >= 0 ? '+' : ''}{stockData.change.toFixed(2)}
                  </Tag>
                  <Tag 
                    color={stockData.change >= 0 ? 'red' : 'green'} 
                    style={{ fontSize: '14px', padding: '4px 8px' }}
                  >
                    {stockData.change >= 0 ? '+' : ''}{stockData.change_percent.toFixed(2)}%
                  </Tag>
                </Space>
              </Space>
              
              <Space size="large">
                <Text type="secondary">
                  量比: <Text strong>{((stockData.volume || 0) / 10000000).toFixed(2)}</Text>
                </Text>
                <Text type="secondary">
                  换手率: <Text strong>{stockData.turnover_rate?.toFixed(2) || '-'}%</Text>
                </Text>
                <Text type="secondary">
                  振幅: <Text strong>
                    {stockData.high && stockData.low ? 
                      ((stockData.high - stockData.low) / stockData.current * 100).toFixed(2) : '-'}%
                  </Text>
                </Text>
              </Space>
            </Space>
          </Col>
          
          <Col xs={24} md={12} lg={16}>
            <Row gutter={[16, 16]}>
              <Col xs={12} sm={8} md={6}>
                <Statistic title="今开" value={stockData.open || '-'} precision={2} />
              </Col>
              <Col xs={12} sm={8} md={6}>
                <Statistic title="最高" value={stockData.high || '-'} precision={2} />
              </Col>
              <Col xs={12} sm={8} md={6}>
                <Statistic title="最低" value={stockData.low || '-'} precision={2} />
              </Col>
              <Col xs={12} sm={8} md={6}>
                <Statistic 
                  title="成交量" 
                  value={stockData.volume ? (stockData.volume / 10000).toFixed(2) : '-'} 
                  suffix="万"
                />
              </Col>
              <Col xs={12} sm={8} md={6}>
                <Statistic title="市盈率" value={stockData.pe || '-'} precision={2} />
              </Col>
              <Col xs={12} sm={8} md={6}>
                <Statistic title="市净率" value={stockData.pb || '-'} precision={2} />
              </Col>
              <Col xs={12} sm={8} md={6}>
                <Statistic 
                  title="市值" 
                  value={stockData.market_cap ? (stockData.market_cap / 100000000).toFixed(2) : '-'} 
                  suffix="亿"
                />
              </Col>
              <Col xs={12} sm={8} md={6}>
                <Statistic 
                  title="行业" 
                  value={stockData.industry || '-'} 
                  formatter={(value) => <Tag color="blue">{value}</Tag>} 
                />
              </Col>
            </Row>
          </Col>
        </Row>
      </Card>
      
      <div style={{ height: '16px' }} />
      
      {/* 股票分析面板 */}
      <StockAnalysisPanel
        stocks={[stockData, ...relatedStocks]}
        defaultStock={stockData.code}
        height={600}
        fullWidth={true}
      />
      
      <div style={{ height: '16px' }} />
      
      {/* 详细信息标签页 */}
      <Card bordered={false}>
        <Tabs defaultActiveKey="technical" size="large">
          <TabPane 
            tab={<span><LineChartOutlined />技术分析</span>} 
            key="technical"
          >
            <div style={{ padding: '20px' }}>
              <Title level={4}>技术分析内容</Title>
              <Paragraph>
                这里是技术分析的详细内容...
              </Paragraph>
            </div>
          </TabPane>
          
          <TabPane 
            tab={<span><InfoCircleOutlined />公司资料</span>} 
            key="company"
          >
            <div style={{ padding: '20px' }}>
              <Title level={4}>公司基本资料</Title>
              <Descriptions bordered>
                <Descriptions.Item label="公司名称" span={3}>{stockData.name}</Descriptions.Item>
                <Descriptions.Item label="股票代码" span={3}>{stockData.code}</Descriptions.Item>
                <Descriptions.Item label="所属行业" span={3}>{stockData.industry || '-'}</Descriptions.Item>
                <Descriptions.Item label="上市日期" span={3}>2001-08-27</Descriptions.Item>
                <Descriptions.Item label="公司介绍" span={3}>
                  这里是公司的基本介绍内容...
                </Descriptions.Item>
              </Descriptions>
            </div>
          </TabPane>
          
          <TabPane 
            tab={<span><BarChartOutlined />财务数据</span>} 
            key="financial"
          >
            <div style={{ padding: '20px' }}>
              <Title level={4}>财务指标</Title>
              <Paragraph>
                这里是财务数据的详细内容...
              </Paragraph>
            </div>
          </TabPane>
          
          <TabPane 
            tab={<span><FileTextOutlined />相关新闻</span>} 
            key="news"
          >
            <div style={{ padding: '20px' }}>
              <Title level={4}>相关新闻</Title>
              <Paragraph>
                这里是相关新闻的列表...
              </Paragraph>
            </div>
          </TabPane>
        </Tabs>
      </Card>
      
      {/* AI分析助手触发器 */}
      <AIAssistantTrigger currentStock={stockData} position="bottom-right" />
    </div>
  );
};

export default StockDetailWithAI;

// 临时的段落组件以避免类型错误
const Paragraph: React.FC<{children: React.ReactNode}> = ({children}) => {
  return <Typography.Paragraph>{children}</Typography.Paragraph>;
};