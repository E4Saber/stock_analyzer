// src/pages/StockDetailDemo.tsx
import React, { useEffect, useState } from 'react';
import { Row, Col, Card, Tabs, Typography, Statistic, Descriptions, Table, Spin, Alert, Tag } from 'antd';
import { 
  ArrowUpOutlined, ArrowDownOutlined, 
  InfoCircleOutlined, LineChartOutlined, 
  BarChartOutlined, FileTextOutlined
} from '@ant-design/icons';
import StockAnalysisPanel from '../components/charts/StockAnalysisPanel';
import { StockData } from '../components/charts/config/chartConfig';
import * as mockService from '../services/mockStockService';

const { Title, Text } = Typography;
const { TabPane } = Tabs;

interface FinancialData {
  year: string;
  revenue: number;
  profit: number;
  eps: number;
  roe: number;
}

const StockDetailDemo: React.FC = () => {
  // 使用固定股票代码进行演示
  const code = '600519'; // 贵州茅台
  
  // 状态管理
  const [stockData, setStockData] = useState<StockData | null>(null);
  const [relatedStocks, setRelatedStocks] = useState<StockData[]>([]);
  const [financialData, setFinancialData] = useState<FinancialData[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  
  // 获取数据
  useEffect(() => {
    const fetchStockData = async () => {
      setLoading(true);
      try {
        // 获取股票详情
        const detailResponse = await mockService.getStockDetail(code);
        setStockData(detailResponse.data);
        
        // 获取相关股票（同行业股票）
        setRelatedStocks(detailResponse.related_stocks || []);
        
        // 获取财务数据
        const financialResponse = await mockService.getStockFinancial(code);
        setFinancialData(financialResponse.data);
        
        setError(null);
      } catch (err) {
        console.error('获取股票详情失败:', err);
        setError('获取数据失败，请稍后重试');
      } finally {
        setLoading(false);
      }
    };
    
    fetchStockData();
  }, []);
  
  // 生成财务数据表格列
  const financialColumns = [
    {
      title: '年度',
      dataIndex: 'year',
      key: 'year',
    },
    {
      title: '营收(亿元)',
      dataIndex: 'revenue',
      key: 'revenue',
      render: (value: number) => (value / 100000000).toFixed(2),
      sorter: (a: FinancialData, b: FinancialData) => a.revenue - b.revenue,
    },
    {
      title: '净利润(亿元)',
      dataIndex: 'profit',
      key: 'profit',
      render: (value: number) => (value / 100000000).toFixed(2),
      sorter: (a: FinancialData, b: FinancialData) => a.profit - b.profit,
    },
    {
      title: '每股收益(元)',
      dataIndex: 'eps',
      key: 'eps',
      render: (value: number) => value.toFixed(2),
      sorter: (a: FinancialData, b: FinancialData) => a.eps - b.eps,
    },
    {
      title: 'ROE(%)',
      dataIndex: 'roe',
      key: 'roe',
      render: (value: number) => value.toFixed(2),
      sorter: (a: FinancialData, b: FinancialData) => a.roe - b.roe,
    },
  ];
  
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
    <div className="stock-detail-container" style={{ padding: '16px' }}>
      <Row gutter={[16, 16]}>
        <Col span={24}>
          <Card bordered={false}>
            <Row gutter={16} align="middle">
              <Col xs={24} md={8}>
                <Title level={3}>{stockData.name} ({stockData.code})</Title>
                <Statistic
                  value={stockData.current}
                  precision={2}
                  valueStyle={{ 
                    color: stockData.change >= 0 ? '#3f8600' : '#cf1322',
                    fontSize: '28px' 
                  }}
                  prefix={stockData.change >= 0 ? <ArrowUpOutlined /> : <ArrowDownOutlined />}
                  suffix={
                    <Text style={{ 
                      color: stockData.change >= 0 ? '#3f8600' : '#cf1322',
                      fontSize: '16px'
                    }}>
                      {stockData.change >= 0 ? '+' : ''}{stockData.change.toFixed(2)} ({stockData.change_percent}%)
                    </Text>
                  }
                />
              </Col>
              
              <Col xs={24} md={16}>
                <Row gutter={[16, 16]}>
                  <Col xs={12} sm={6}>
                    <Statistic title="今开" value={stockData.open || '-'} precision={2} />
                  </Col>
                  <Col xs={12} sm={6}>
                    <Statistic title="最高" value={stockData.high || '-'} precision={2} />
                  </Col>
                  <Col xs={12} sm={6}>
                    <Statistic title="最低" value={stockData.low || '-'} precision={2} />
                  </Col>
                  <Col xs={12} sm={6}>
                    <Statistic title="成交量" value={stockData.volume || '-'} suffix="股" formatter={value => {
                      if (typeof value === 'number') {
                        if (value >= 100000000) {
                          return `${(value / 100000000).toFixed(2)}亿`;
                        } else if (value >= 10000) {
                          return `${(value / 10000).toFixed(2)}万`;
                        }
                      }
                      return value;
                    }} />
                  </Col>
                  <Col xs={12} sm={6}>
                    <Statistic title="市盈率" value={stockData.pe || '-'} precision={2} />
                  </Col>
                  <Col xs={12} sm={6}>
                    <Statistic title="市净率" value={stockData.pb || '-'} precision={2} />
                  </Col>
                  <Col xs={12} sm={6}>
                    <Statistic title="市值" value={stockData.market_cap ? (stockData.market_cap / 100000000).toFixed(2) : '-'} suffix="亿" />
                  </Col>
                  <Col xs={12} sm={6}>
                    <Statistic title="行业" value={stockData.industry || '-'} formatter={value => <Tag color="blue">{value}</Tag>} />
                  </Col>
                </Row>
              </Col>
            </Row>
          </Card>
        </Col>
        
        <Col span={24}>
          {/* 股票分析面板 */}
          <StockAnalysisPanel
            stocks={[stockData, ...relatedStocks]}
            defaultStock={stockData.code}
            height={600}
            fullWidth={true}
          />
        </Col>
        
        <Col span={24}>
          <Card bordered={false}>
            <Tabs defaultActiveKey="financial">
              <TabPane 
                tab={<span><FileTextOutlined />财务数据</span>} 
                key="financial"
              >
                <Table 
                  dataSource={financialData} 
                  columns={financialColumns} 
                  rowKey="year"
                  pagination={false}
                  scroll={{ x: 'max-content' }}
                />
              </TabPane>
              
              <TabPane 
                tab={<span><InfoCircleOutlined />公司资料</span>} 
                key="company"
              >
                <Descriptions title="公司简介" bordered>
                  <Descriptions.Item label="公司名称" span={3}>{stockData.name}</Descriptions.Item>
                  <Descriptions.Item label="股票代码" span={3}>{stockData.code}</Descriptions.Item>
                  <Descriptions.Item label="所属行业" span={3}>{stockData.industry || '-'}</Descriptions.Item>
                  <Descriptions.Item label="上市日期" span={3}>2001-08-27</Descriptions.Item>
                  <Descriptions.Item label="公司介绍" span={3}>
                    贵州茅台酒股份有限公司是中国酱香型白酒的典型代表，始建于1951年，老厂位于贵州省仁怀市茅台镇，是中国最大的名酒生产企业之一。公司的主要产品"贵州茅台酒"是世界三大蒸馏名酒之一，享有极高的声誉。公司秉承"质量第一、效益优先"的经营理念，不断创新发展，现已成为中国市值最高的白酒上市公司。
                  </Descriptions.Item>
                </Descriptions>
              </TabPane>
              
              <TabPane 
                tab={<span><BarChartOutlined />行业对比</span>} 
                key="industry"
              >
                <div style={{ padding: '20px 0' }}>
                  <Row gutter={[16, 16]}>
                    <Col span={24}>
                      <Title level={4}>与行业内其他公司对比</Title>
                    </Col>
                    
                    <Col xs={24} sm={12} md={8}>
                      <Card title="市盈率对比" bordered={false}>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                          {[stockData, ...relatedStocks].map(item => (
                            <div key={item.code} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                              <span>{item.name}</span>
                              <div style={{ 
                                width: `${item.pe ? Math.min(item.pe * 4, 100) : 30}%`, 
                                height: '20px', 
                                background: item.code === stockData.code ? '#1890ff' : '#d9d9d9',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'flex-end',
                                paddingRight: '5px'
                              }}>
                                {item.pe?.toFixed(2) || '-'}
                              </div>
                            </div>
                          ))}
                        </div>
                      </Card>
                    </Col>
                    
                    <Col xs={24} sm={12} md={8}>
                      <Card title="市净率对比" bordered={false}>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                          {[stockData, ...relatedStocks].map(item => (
                            <div key={item.code} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                              <span>{item.name}</span>
                              <div style={{ 
                                width: `${item.pb ? Math.min(item.pb * 10, 100) : 30}%`, 
                                height: '20px', 
                                background: item.code === stockData.code ? '#1890ff' : '#d9d9d9',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'flex-end',
                                paddingRight: '5px'
                              }}>
                                {item.pb?.toFixed(2) || '-'}
                              </div>
                            </div>
                          ))}
                        </div>
                      </Card>
                    </Col>
                    
                    <Col xs={24} sm={12} md={8}>
                      <Card title="市值对比(亿元)" bordered={false}>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                          {[stockData, ...relatedStocks].map(item => (
                            <div key={item.code} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                              <span>{item.name}</span>
                              <div style={{ 
                                width: `${item.market_cap ? Math.min((item.market_cap / 10000000000) * 5, 100) : 30}%`, 
                                height: '20px', 
                                background: item.code === stockData.code ? '#1890ff' : '#d9d9d9',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'flex-end',
                                paddingRight: '5px'
                              }}>
                                {item.market_cap ? (item.market_cap / 100000000).toFixed(0) : '-'}
                              </div>
                            </div>
                          ))}
                        </div>
                      </Card>
                    </Col>
                  </Row>
                </div>
              </TabPane>
            </Tabs>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default StockDetailDemo;