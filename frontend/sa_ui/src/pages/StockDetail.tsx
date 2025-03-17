// src/pages/StockDetail.tsx
import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { Row, Col, Card, Tabs, Typography, Statistic, Descriptions, Table, Spin, Alert } from 'antd';
import { 
  ArrowUpOutlined, ArrowDownOutlined, 
  InfoCircleOutlined, LineChartOutlined, 
  BarChartOutlined, FileTextOutlined
} from '@ant-design/icons';
import { getStockDetail, getStockFinancial } from '../services/stockService';
import StockAnalysisPanel from '../components/charts/StockAnalysisPanel';
import { StockData } from '../components/charts/config/chartConfig';

const { Title, Text } = Typography;
const { TabPane } = Tabs;

interface FinancialData {
  year: string;
  revenue: number;
  profit: number;
  eps: number;
  roe: number;
  // 其他财务数据...
}

const StockDetail: React.FC = () => {
  // 从路由参数获取股票代码
  const { code } = useParams<{ code: string }>();
  
  // 状态管理
  const [stockData, setStockData] = useState<StockData | null>(null);
  const [relatedStocks, setRelatedStocks] = useState<StockData[]>([]);
  const [financialData, setFinancialData] = useState<FinancialData[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  
  // 获取数据
  useEffect(() => {
    if (!code) return;
    
    const fetchStockData = async () => {
      setLoading(true);
      try {
        // 获取股票详情
        const detailResponse = await getStockDetail(code);
        setStockData(detailResponse.data);
        
        // 获取相关股票（同行业股票）
        setRelatedStocks(detailResponse.related_stocks || []);
        
        // 获取财务数据
        const financialResponse = await getStockFinancial(code);
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
  }, [code]);
  
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
                    <Statistic title="成交量" value={stockData.volume || '-'} />
                  </Col>
                  <Col xs={12} sm={6}>
                    <Statistic title="市盈率" value={stockData.pe || '-'} precision={2} />
                  </Col>
                  <Col xs={12} sm={6}>
                    <Statistic title="市净率" value={stockData.pb || '-'} precision={2} />
                  </Col>
                  <Col xs={12} sm={6}>
                    <Statistic title="市值(亿)" value={stockData.market_cap ? (stockData.market_cap / 100000000).toFixed(2) : '-'} />
                  </Col>
                  <Col xs={12} sm={6}>
                    <Statistic title="行业" value={stockData.industry || '-'} />
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
            height={700}
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
                  <Descriptions.Item label="上市日期" span={3}>待获取</Descriptions.Item>
                  <Descriptions.Item label="公司介绍" span={3}>
                    这里是公司介绍内容。由于API限制，这里使用占位文本。真实场景中，这里会显示公司的详细介绍，包括主营业务、发展历史、核心产品等信息。
                  </Descriptions.Item>
                </Descriptions>
              </TabPane>
              
              <TabPane 
                tab={<span><BarChartOutlined />行业对比</span>} 
                key="industry"
              >
                <div style={{ padding: '20px 0' }}>
                  <Alert
                    message="行业对比"
                    description="此部分将展示与同行业其他公司的指标对比，包括市盈率、市净率、净资产收益率等关键财务指标的对比分析。"
                    type="info"
                    showIcon
                  />
                </div>
              </TabPane>
            </Tabs>
          </Card>
        </Col>
      </Row>
    </div>
  );
};