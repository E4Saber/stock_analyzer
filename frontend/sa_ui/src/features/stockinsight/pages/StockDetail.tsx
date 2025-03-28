// src/pages/StockDetail.tsx
import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { 
  Row, Col, Card, Tabs, Typography, Statistic, Descriptions, Table, 
  Spin, Alert, Tag, Space, List, Divider, Progress
} from 'antd';
import { 
  ArrowUpOutlined, ArrowDownOutlined, 
  InfoCircleOutlined, LineChartOutlined, 
  BarChartOutlined, FileTextOutlined,
  DollarOutlined, TeamOutlined, FileSearchOutlined,
  RiseOutlined, FallOutlined, FireOutlined
} from '@ant-design/icons';
import { getStockDetail, getStockFinancial } from '../../marketoverview/services/mockStockService';
import StockAnalysisPanel from '../components/widgets/StockAnalysisPanel';
import StockInfoHeader from '../components/common/StockInfoHeader';
import { StockData } from '../components/widgets/config/chartConfig';
import { ShareholderData, FinancialIndicator, MarketNews } from '../../marketoverview/types/market';
import { formatLargeNumber, formatPercent } from '../../../shared/utils/numberFormatter';
import AIAssistantTrigger from '../components/widgets/AIAssistantTrigger';

const { Title, Text, Paragraph } = Typography;
const { TabPane } = Tabs;

interface StockDetailData {
  stock: StockData;
  relatedStocks: StockData[];
  shareholders: ShareholderData[];
  financials: FinancialIndicator[];
  news: MarketNews[];
}

const StockDetail: React.FC = () => {
  // 从路由参数获取股票代码
  const { code = '600519' } = useParams<{ code: string }>();
  
  // 状态管理
  const [stockData, setStockData] = useState<StockData | null>(null);
  const [relatedStocks, setRelatedStocks] = useState<StockData[]>([]);
  const [shareholders, setShareholders] = useState<ShareholderData[]>([]);
  const [financials, setFinancials] = useState<FinancialIndicator[]>([]);
  const [news, setNews] = useState<MarketNews[]>([]);
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
        setStockData(detailResponse.stock);
        setRelatedStocks(detailResponse.relatedStocks);
        setShareholders(detailResponse.shareholders);
        setFinancials(detailResponse.financials);
        setNews(detailResponse.news);
        
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

  // 股东列表表格列
  const shareholderColumns = [
    {
      title: '股东名称',
      dataIndex: 'name',
      key: 'name',
      width: '40%',
      render: (name: string, record: ShareholderData) => (
        <Space>
          {name}
          {record.type === 'institution' && <Tag color="blue">机构</Tag>}
          {record.type === 'individual' && <Tag color="green">个人</Tag>}
          {record.type === 'government' && <Tag color="red">国家</Tag>}
        </Space>
      ),
    },
    {
      title: '持股数量',
      dataIndex: 'shares',
      key: 'shares',
      render: (shares: number) => formatLargeNumber(shares),
      sorter: (a: ShareholderData, b: ShareholderData) => a.shares - b.shares,
    },
    {
      title: '持股比例',
      dataIndex: 'ratio',
      key: 'ratio',
      render: (ratio: number) => `${ratio.toFixed(2)}%`,
      sorter: (a: ShareholderData, b: ShareholderData) => a.ratio - b.ratio,
    },
    {
      title: '变动',
      dataIndex: 'change',
      key: 'change',
      render: (change: number) => (
        <span style={{ color: change > 0 ? '#3f8600' : change < 0 ? '#cf1322' : '' }}>
          {change > 0 ? '+' : ''}{formatLargeNumber(change)}
        </span>
      ),
    },
  ];

  // 财务数据表格列
  const financialColumns = [
    {
      title: '报告期',
      dataIndex: 'year',
      key: 'year',
      render: (year: string, record: FinancialIndicator) => `${year}年${record.quarter}`,
    },
    {
      title: '营收(亿元)',
      dataIndex: 'revenue',
      key: 'revenue',
      render: (value: number) => (value / 100000000).toFixed(2),
      sorter: (a: FinancialIndicator, b: FinancialIndicator) => a.revenue - b.revenue,
    },
    {
      title: '净利润(亿元)',
      dataIndex: 'netProfit',
      key: 'netProfit',
      render: (value: number) => (value / 100000000).toFixed(2),
      sorter: (a: FinancialIndicator, b: FinancialIndicator) => a.netProfit - b.netProfit,
    },
    {
      title: '毛利率(%)',
      dataIndex: 'grossMargin',
      key: 'grossMargin',
      render: (value: number) => value.toFixed(2),
      sorter: (a: FinancialIndicator, b: FinancialIndicator) => a.grossMargin - b.grossMargin,
    },
    {
      title: '净利率(%)',
      dataIndex: 'netMargin',
      key: 'netMargin',
      render: (value: number) => value.toFixed(2),
      sorter: (a: FinancialIndicator, b: FinancialIndicator) => a.netMargin - b.netMargin,
    },
    {
      title: 'ROE(%)',
      dataIndex: 'roe',
      key: 'roe',
      render: (value: number) => value.toFixed(2),
      sorter: (a: FinancialIndicator, b: FinancialIndicator) => a.roe - b.roe,
    },
    {
      title: 'EPS(元)',
      dataIndex: 'eps',
      key: 'eps',
      render: (value: number) => value.toFixed(2),
      sorter: (a: FinancialIndicator, b: FinancialIndicator) => a.eps - b.eps,
    },
  ];

  // 增强股票数据 - 添加图片中显示的额外数据
  const enhancedStockData = {
    ...stockData,
    prevClose: 103.00,  // 昨收
    amount: 60.25 * 100000000,  // 成交额（亿元）
    circulating_market_cap: 1051 * 100000000,  // 流通市值（亿元）
    total_shares: 11.14 * 100000000,  // 总股本（亿）
    circulating_shares: 11.10 * 100000000,  // 流通股本（亿）
    amplitude: stockData.high && stockData.low ? 
      ((stockData.high - stockData.low) / stockData.low * 100) : 4.66,  // 振幅
    high_52w: 157.54,  // 52周最高
    low_52w: 83.54,    // 52周最低
    roa: 5.52,         // ROA
    roe: 10.10,        // ROE
    volume_ratio: 2.98, // 量比
    eps_ttm: 3.46,     // 每股收益TTM
    eps_lyr: 0.70,     // 每股收益LYR
    dividend: 0.46,    // 股息
    dividend_yield: 0.49, // 股息收益率
    forecast_pe: 13.85, // 预测市盈率
    forecast_eps: 6.839 // 预测每股收益
  };

  return (
    <div className="stock-detail-container">
      {/* 使用新的股票信息头部组件 */}
      <StockInfoHeader stock={enhancedStockData} />
      
      <div style={{ height: '16px' }} />
      
      {/* 股票分析面板 */}
      <StockAnalysisPanel
        stocks={[enhancedStockData, ...relatedStocks]}
        defaultStock={enhancedStockData.code}
        height={600}
        fullWidth={true}
      />
      
      <div style={{ height: '16px' }} />
      
      {/* 详细信息标签页 */}
      <Card bordered={false}>
        <Tabs defaultActiveKey="financial" size="large">
          <TabPane 
            tab={<span><DollarOutlined />财务数据</span>} 
            key="financial"
          >
            <div style={{ marginBottom: '16px' }}>
              <Title level={4}>关键财务指标</Title>
              <Row gutter={[16, 16]}>
                <Col xs={24} sm={12} md={8} lg={6}>
                  <Card bordered={false}>
                    <Statistic
                      title="最新营收"
                      value={financials[0]?.revenue ? (financials[0].revenue / 100000000).toFixed(2) : '-'}
                      suffix="亿元"
                      precision={2}
                    />
                    <div style={{ marginTop: '8px' }}>
                      <Text type="secondary">同比: </Text>
                      <Text style={{ color: '#cf1322' }}>+15.8%</Text>
                    </div>
                  </Card>
                </Col>
                <Col xs={24} sm={12} md={8} lg={6}>
                  <Card bordered={false}>
                    <Statistic
                      title="最新净利润"
                      value={financials[0]?.netProfit ? (financials[0].netProfit / 100000000).toFixed(2) : '-'}
                      suffix="亿元"
                      precision={2}
                    />
                    <div style={{ marginTop: '8px' }}>
                      <Text type="secondary">同比: </Text>
                      <Text style={{ color: '#cf1322' }}>+21.3%</Text>
                    </div>
                  </Card>
                </Col>
                <Col xs={24} sm={12} md={8} lg={6}>
                  <Card bordered={false}>
                    <Statistic
                      title="净资产收益率"
                      value={financials[0]?.roe || '-'}
                      suffix="%"
                      precision={2}
                    />
                    <div style={{ marginTop: '8px' }}>
                      <Text type="secondary">行业排名: </Text>
                      <Text style={{ color: '#1890ff' }}>前15%</Text>
                    </div>
                  </Card>
                </Col>
                <Col xs={24} sm={12} md={8} lg={6}>
                  <Card bordered={false}>
                    <Statistic
                      title="每股收益"
                      value={financials[0]?.eps || '-'}
                      suffix="元"
                      precision={2}
                    />
                    <div style={{ marginTop: '8px' }}>
                      <Text type="secondary">同比: </Text>
                      <Text style={{ color: '#cf1322' }}>+18.5%</Text>
                    </div>
                  </Card>
                </Col>
              </Row>
            </div>
            
            <Divider style={{ margin: '24px 0 16px' }} />
            
            <div>
              <Title level={4}>历史财务数据</Title>
              <Table 
                dataSource={financials} 
                columns={financialColumns} 
                rowKey={(record) => `${record.year}-${record.quarter}`}
                pagination={false}
                scroll={{ x: 'max-content' }}
              />
            </div>
            
            <Divider style={{ margin: '24px 0 16px' }} />
            
            <div>
              <Title level={4}>营收与利润趋势</Title>
              <div style={{ height: '300px', background: '#fafafa', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
                <Text type="secondary">图表区域 - 收入和利润的历史走势图</Text>
              </div>
            </div>
          </TabPane>
          
          <TabPane 
            tab={<span><InfoCircleOutlined />公司资料</span>} 
            key="company"
          >
            <Row gutter={[16, 24]}>
              <Col span={24}>
                <Card title="公司简介" bordered={false}>
                  <Paragraph>
                    {stockData.name}（{stockData.code}）是一家中国领先的{stockData.industry}企业，总部位于中国。
                    公司主要从事产品研发、生产和销售业务，在行业内占据重要地位。公司注重技术创新和产品质量，
                    持续推进产业链延伸和产品升级，不断提高市场竞争力和盈利能力。
                  </Paragraph>
                  <Paragraph>
                    公司成立于1999年，2001年8月27日在上海证券交易所上市。经过多年的发展，公司已形成完整的业务体系，
                    建立了强大的研发能力和生产规模，产品广泛应用于多个领域。公司拥有一支经验丰富的管理团队和技术团队，
                    致力于为股东创造长期价值。
                  </Paragraph>
                </Card>
              </Col>
              
              <Col xs={24} lg={12}>
                <Card title="公司基本资料" bordered={false}>
                  <Descriptions column={{ xs: 1, sm: 2 }} bordered>
                    <Descriptions.Item label="股票代码">{stockData.code}</Descriptions.Item>
                    <Descriptions.Item label="股票简称">{stockData.name}</Descriptions.Item>
                    <Descriptions.Item label="所属行业">{stockData.industry || '-'}</Descriptions.Item>
                    <Descriptions.Item label="上市日期">2001-08-27</Descriptions.Item>
                    <Descriptions.Item label="总股本">{formatLargeNumber(enhancedStockData.total_shares || 0)}股</Descriptions.Item>
                    <Descriptions.Item label="流通股本">{formatLargeNumber(enhancedStockData.circulating_shares || 0)}股</Descriptions.Item>
                    <Descriptions.Item label="注册资本">{formatLargeNumber(1200000000)}元</Descriptions.Item>
                    <Descriptions.Item label="员工人数">15,832人</Descriptions.Item>
                    <Descriptions.Item label="法人代表">张三</Descriptions.Item>
                    <Descriptions.Item label="董事长">李四</Descriptions.Item>
                    <Descriptions.Item label="总经理">王五</Descriptions.Item>
                    <Descriptions.Item label="董秘">赵六</Descriptions.Item>
                    <Descriptions.Item label="注册地址" span={2}>北京市朝阳区xxx路xxx号</Descriptions.Item>
                    <Descriptions.Item label="办公地址" span={2}>北京市海淀区xxx路xxx号</Descriptions.Item>
                  </Descriptions>
                </Card>
              </Col>
              
              <Col xs={24} lg={12}>
                <Card title="十大股东" bordered={false}>
                  <Table 
                    dataSource={shareholders} 
                    columns={shareholderColumns} 
                    pagination={false}
                    rowKey="name"
                    size="middle"
                  />
                </Card>
              </Col>
            </Row>
          </TabPane>
          
          <TabPane 
            tab={<span><BarChartOutlined />行业对比</span>} 
            key="industry"
          >
            <div style={{ marginBottom: '24px' }}>
              <Title level={4}>行业对比分析</Title>
              <Paragraph>
                下面是{stockData.name}与同行业其他公司的关键指标对比，包括市盈率、市净率、营收增长率等。
              </Paragraph>
              
              <Row gutter={[16, 16]} style={{ marginTop: '16px' }}>
                <Col xs={24} sm={12} lg={8}>
                  <Card title="市盈率对比" bordered={false}>
                    <div style={{ marginBottom: '16px' }}>
                      <Text>行业平均: </Text>
                      <Text strong>32.56</Text>
                    </div>
                    {[enhancedStockData, ...relatedStocks].map(stock => (
                      <div 
                        key={stock.code} 
                        style={{ 
                          marginBottom: '8px', 
                          display: 'flex', 
                          alignItems: 'center', 
                          justifyContent: 'space-between' 
                        }}
                      >
                        <Text style={{ width: '100px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                          {stock.name}
                        </Text>
                        <Progress 
                          percent={stock.pe ? (stock.pe / 100) * 100 : 0} 
                          showInfo={false} 
                          strokeColor={stock.code === enhancedStockData.code ? "#1890ff" : "#d9d9d9"}
                          style={{ flex: 1, margin: '0 8px' }}
                        />
                        <Text style={{ width: '40px', textAlign: 'right' }}>{stock.pe?.toFixed(2) || '-'}</Text>
                      </div>
                    ))}
                  </Card>
                </Col>
                
                <Col xs={24} sm={12} lg={8}>
                  <Card title="市净率对比" bordered={false}>
                    <div style={{ marginBottom: '16px' }}>
                      <Text>行业平均: </Text>
                      <Text strong>5.87</Text>
                    </div>
                    {[enhancedStockData, ...relatedStocks].map(stock => (
                      <div 
                        key={stock.code} 
                        style={{ 
                          marginBottom: '8px', 
                          display: 'flex', 
                          alignItems: 'center', 
                          justifyContent: 'space-between' 
                        }}
                      >
                        <Text style={{ width: '100px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                          {stock.name}
                        </Text>
                        <Progress 
                          percent={stock.pb ? (stock.pb / 15) * 100 : 0} 
                          showInfo={false} 
                          strokeColor={stock.code === enhancedStockData.code ? "#1890ff" : "#d9d9d9"}
                          style={{ flex: 1, margin: '0 8px' }}
                        />
                        <Text style={{ width: '40px', textAlign: 'right' }}>{stock.pb?.toFixed(2) || '-'}</Text>
                      </div>
                    ))}
                  </Card>
                </Col>
                
                <Col xs={24} sm={12} lg={8}>
                  <Card title="市值对比(亿元)" bordered={false}>
                    <div style={{ marginBottom: '16px' }}>
                      <Text>行业平均: </Text>
                      <Text strong>1,562.35亿</Text>
                    </div>
                    {[enhancedStockData, ...relatedStocks].map(stock => (
                      <div 
                        key={stock.code} 
                        style={{ 
                          marginBottom: '8px', 
                          display: 'flex', 
                          alignItems: 'center', 
                          justifyContent: 'space-between' 
                        }}
                      >
                        <Text style={{ width: '100px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                          {stock.name}
                        </Text>
                        <Progress 
                          percent={stock.market_cap ? Math.min((stock.market_cap / 2000000000000) * 100, 100) : 0} 
                          showInfo={false} 
                          strokeColor={stock.code === enhancedStockData.code ? "#1890ff" : "#d9d9d9"}
                          style={{ flex: 1, margin: '0 8px' }}
                        />
                        <Text style={{ width: '60px', textAlign: 'right' }}>
                          {stock.market_cap ? (stock.market_cap / 100000000).toFixed(0) : '-'}
                        </Text>
                      </div>
                    ))}
                  </Card>
                </Col>
              </Row>
            </div>
            
            <Divider style={{ margin: '16px 0' }} />
            
            <div>
              <Title level={4}>财务指标雷达图</Title>
              <div style={{ height: '400px', background: '#fafafa', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
                <Text type="secondary">图表区域 - 与行业平均水平的雷达图对比</Text>
              </div>
            </div>
          </TabPane>
          
          <TabPane 
            tab={<span><FireOutlined />热点新闻</span>} 
            key="news"
          >
            <List
              itemLayout="vertical"
              dataSource={news}
              renderItem={item => (
                <List.Item
                  key={item.id}
                  extra={
                    <div style={{ color: '#8c8c8c', fontSize: '12px', whiteSpace: 'nowrap' }}>
                      {item.time}
                    </div>
                  }
                >
                  <List.Item.Meta
                    title={<a href={item.url} target="_blank" rel="noopener noreferrer">{item.title}</a>}
                    description={<Text type="secondary">{item.source}</Text>}
                  />
                </List.Item>
              )}
              pagination={{ pageSize: 10 }}
            />
          </TabPane>
        </Tabs>
      </Card>

      {/* AI分析助手触发器 */}
      <AIAssistantTrigger currentStock={stockData} position="bottom-right" />
    </div>
  );
};

export default StockDetail;