// src/pages/MarketOverview.tsx
import React, { useEffect, useState } from 'react';
import { 
  Row, Col, Card, Typography, Spin, Alert, Tabs, Table, Statistic, Progress, Tag, List, Space 
} from 'antd';
import { 
  RiseOutlined, FallOutlined, LineChartOutlined, PieChartOutlined, 
  BarChartOutlined, AreaChartOutlined, FireOutlined
} from '@ant-design/icons';
import { getMarketOverview } from '../services/mockMarketService';
import { IndexData, SectorData, HotStock, MarketStats } from '../types/market';
import HeatmapChart from '../components/charts/HeatmapChart';
import EnhancedIndexChart from '../components/charts/EnhancedIndexChart';
import { formatLargeNumber } from '../utils/numberFormatter';

const { Title, Text } = Typography;
const { TabPane } = Tabs;

const MarketOverview: React.FC = () => {
  // 状态管理
  const [indices, setIndices] = useState<IndexData[]>([]);
  const [sectors, setSectors] = useState<SectorData[]>([]);
  const [hotStocks, setHotStocks] = useState<HotStock[]>([]);
  const [marketStats, setMarketStats] = useState<MarketStats | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // 获取数据
  useEffect(() => {
    const fetchMarketData = async () => {
      setLoading(true);
      try {
        const data = await getMarketOverview();
        setIndices(data.indices);
        setSectors(data.sectors);
        setHotStocks(data.hotStocks);
        setMarketStats(data.marketStats);
        setError(null);
      } catch (err) {
        console.error('获取市场概览数据失败:', err);
        setError('获取数据失败，请稍后重试');
      } finally {
        setLoading(false);
      }
    };

    fetchMarketData();
    
    // 设置定时刷新（每分钟）
    const intervalId = setInterval(() => {
      fetchMarketData();
    }, 60000);

    return () => clearInterval(intervalId);
  }, []);

  // 加载状态
  if (loading && indices.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
        <p>正在加载市场数据...</p>
      </div>
    );
  }

  // 错误处理
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

  // 热门股票表格列
  const stockColumns = [
    {
      title: '代码',
      dataIndex: 'code',
      key: 'code',
      width: 100,
    },
    {
      title: '名称',
      dataIndex: 'name',
      key: 'name',
      width: 120,
    },
    {
      title: '价格',
      dataIndex: 'price',
      key: 'price',
      width: 100,
      render: (price: number) => price.toFixed(2),
    },
    {
      title: '涨跌幅',
      dataIndex: 'change_pct',
      key: 'change_pct',
      width: 100,
      render: (change_pct: number) => (
        <span style={{ color: change_pct >= 0 ? '#3f8600' : '#cf1322' }}>
          {change_pct >= 0 ? '+' : ''}{change_pct.toFixed(2)}%
        </span>
      ),
      sorter: (a: HotStock, b: HotStock) => a.change_pct - b.change_pct,
    },
    {
      title: '成交量',
      dataIndex: 'volume',
      key: 'volume',
      width: 120,
      render: (volume: number) => formatLargeNumber(volume),
    },
    {
      title: '成交额',
      dataIndex: 'amount',
      key: 'amount',
      width: 120,
      render: (amount: number) => formatLargeNumber(amount),
    },
    {
      title: '换手率',
      dataIndex: 'turnover_rate',
      key: 'turnover_rate',
      width: 100,
      render: (turnover_rate: number) => `${turnover_rate.toFixed(2)}%`,
    },
  ];

  // 板块表格列
  const sectorColumns = [
    {
      title: '板块名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '涨跌幅',
      dataIndex: 'change_pct',
      key: 'change_pct',
      render: (change_pct: number) => (
        <span style={{ color: change_pct >= 0 ? '#3f8600' : '#cf1322' }}>
          {change_pct >= 0 ? '+' : ''}{change_pct.toFixed(2)}%
        </span>
      ),
      sorter: (a: SectorData, b: SectorData) => a.change_pct - b.change_pct,
    },
    {
      title: '平均成交量',
      dataIndex: 'avg_volume',
      key: 'avg_volume',
      render: (avg_volume: number) => formatLargeNumber(avg_volume),
    },
  ];

  // 计算涨跌比例
  const upRatio = marketStats ? (marketStats.upStocks / marketStats.totalStocks) * 100 : 0;
  const downRatio = marketStats ? (marketStats.downStocks / marketStats.totalStocks) * 100 : 0;

  return (
    <div className="market-overview-container">
      <Title level={2}>市场概览</Title>
      
      {/* 市场统计卡片 */}
      {marketStats && (
        <Row gutter={[16, 16]} className="market-stats-section">
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="市场涨跌比"
                value={upRatio.toFixed(1)}
                precision={1}
                valueStyle={{ color: '#3f8600' }}
                suffix="%"
                prefix={<RiseOutlined />}
              />
              <Progress
                percent={upRatio}
                strokeColor="#3f8600"
                trailColor="#cf1322"
                showInfo={false}
                status="active"
              />
              <Row justify="space-between">
                <Col>
                  <Text type="success">上涨: {marketStats.upStocks}</Text>
                </Col>
                <Col>
                  <Text type="danger">下跌: {marketStats.downStocks}</Text>
                </Col>
              </Row>
            </Card>
          </Col>
          
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="涨停家数"
                value={marketStats.limitUpStocks}
                valueStyle={{ color: '#cf1322' }}
                prefix={<RiseOutlined />}
              />
              <Statistic
                title="跌停家数"
                value={marketStats.limitDownStocks}
                valueStyle={{ color: '#3f8600' }}
                prefix={<FallOutlined />}
              />
            </Card>
          </Col>
          
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="总成交量"
                value={formatLargeNumber(marketStats.totalVolume)}
                valueStyle={{ color: '#1890ff' }}
              />
              <Statistic
                title="总成交额"
                value={`${formatLargeNumber(marketStats.totalAmount / 100000000)}亿`}
                valueStyle={{ color: '#1890ff' }}
              />
            </Card>
          </Col>
          
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="总股票数"
                value={marketStats.totalStocks}
                valueStyle={{ color: '#1890ff' }}
              />
              <div style={{ marginTop: '16px' }}>
                <Tag color="green" style={{ marginRight: '8px' }}>A股: {marketStats.totalStocks - 200}</Tag>
                <Tag color="blue" style={{ marginRight: '8px' }}>科创板: 120</Tag>
                <Tag color="purple">创业板: 80</Tag>
              </div>
            </Card>
          </Col>
        </Row>
      )}
      
      <div style={{ height: '24px' }} />
      
      {/* 主要指数走势 */}
      <Card title="主要指数走势" bordered={false}>
        <EnhancedIndexChart 
          indices={indices} 
          height={400}
          showHeader={true}
          defaultPeriod="day"
          defaultChartType="line"
          fullWidth={true}
        />
      </Card>
      
      <div style={{ height: '24px' }} />
      
      {/* 市场详细数据Tab */}
      <Tabs defaultActiveKey="sectors">
        <TabPane 
          tab={<span><PieChartOutlined />行业板块</span>} 
          key="sectors"
        >
          <Row gutter={[16, 16]}>
            <Col xs={24} lg={10}>
              <Card title="板块热力图" bordered={false} style={{ height: '100%' }}>
                <HeatmapChart data={sectors} />
              </Card>
            </Col>
            <Col xs={24} lg={14}>
              <Card title="板块排行榜" bordered={false} style={{ height: '100%' }}>
                <Table 
                  dataSource={sectors.sort((a, b) => b.change_pct - a.change_pct)}
                  columns={sectorColumns}
                  pagination={{ pageSize: 8 }}
                  rowKey="name"
                  size="middle"
                />
              </Card>
            </Col>
          </Row>
        </TabPane>
        
        <TabPane 
          tab={<span><BarChartOutlined />热门股票</span>} 
          key="hotStocks"
        >
          <Card title="市场活跃股票" bordered={false}>
            <Table 
              dataSource={hotStocks}
              columns={stockColumns}
              pagination={{ pageSize: 10 }}
              rowKey="code"
              size="middle"
            />
          </Card>
        </TabPane>
        
        <TabPane 
          tab={<span><AreaChartOutlined />涨跌分布</span>} 
          key="distribution"
        >
          <Card title="涨跌幅分布" bordered={false}>
            <Row gutter={[16, 16]}>
              <Col xs={24} md={12}>
                <Card title="涨幅分布" size="small">
                  <List
                    size="small"
                    dataSource={[
                      { range: '9%-10%', count: 35 },
                      { range: '7%-9%', count: 52 },
                      { range: '5%-7%', count: 87 },
                      { range: '3%-5%', count: 156 },
                      { range: '1%-3%', count: 312 },
                      { range: '0%-1%', count: 189 }
                    ]}
                    renderItem={item => (
                      <List.Item>
                        <span style={{ width: '80px' }}>{item.range}</span>
                        <Progress 
                          percent={item.count / 8} 
                          showInfo={false} 
                          strokeColor="#3f8600" 
                          style={{ flex: 1, margin: '0 12px' }}
                        />
                        <span>{item.count}家</span>
                      </List.Item>
                    )}
                  />
                </Card>
              </Col>
              <Col xs={24} md={12}>
                <Card title="跌幅分布" size="small">
                  <List
                    size="small"
                    dataSource={[
                      { range: '0%-1%', count: 231 },
                      { range: '1%-3%', count: 289 },
                      { range: '3%-5%', count: 142 },
                      { range: '5%-7%', count: 78 },
                      { range: '7%-9%', count: 43 },
                      { range: '9%-10%', count: 21 }
                    ]}
                    renderItem={item => (
                      <List.Item>
                        <span style={{ width: '80px' }}>{item.range}</span>
                        <Progress 
                          percent={item.count / 8} 
                          showInfo={false} 
                          strokeColor="#cf1322" 
                          style={{ flex: 1, margin: '0 12px' }}
                        />
                        <span>{item.count}家</span>
                      </List.Item>
                    )}
                  />
                </Card>
              </Col>
            </Row>
          </Card>
        </TabPane>
        
        <TabPane 
          tab={<span><FireOutlined />龙虎榜</span>} 
          key="topList"
        >
          <Card title="龙虎榜" bordered={false}>
            <Tabs defaultActiveKey="buy">
              <TabPane tab="买入榜" key="buy">
                <Table
                  dataSource={[
                    { code: '600587', name: '新华医疗', price: 26.75, change_pct: 7.58, amount: 45682100, institutions: ['中信证券', '国泰君安', '招商证券'] },
                    { code: '603501', name: '韦尔股份', price: 86.23, change_pct: 4.72, amount: 32541800, institutions: ['华泰证券', '中金公司', '广发证券'] },
                    { code: '688012', name: '中微公司', price: 65.89, change_pct: 5.23, amount: 28965700, institutions: ['海通证券', '国信证券', '中信建投'] },
                    { code: '600438', name: '通威股份', price: 18.25, change_pct: 3.75, amount: 26548900, institutions: ['华西证券', '东方证券', '申万宏源'] },
                    { code: '603986', name: '兆易创新', price: 118.56, change_pct: 3.87, amount: 22659400, institutions: ['中泰证券', '国海证券', '银河证券'] }
                  ]}
                  columns={[
                    { title: '代码', dataIndex: 'code', key: 'code' },
                    { title: '名称', dataIndex: 'name', key: 'name' },
                    { title: '价格', dataIndex: 'price', key: 'price', render: (price: number) => price.toFixed(2) },
                    { title: '涨跌幅', dataIndex: 'change_pct', key: 'change_pct', render: (val: number) => (
                      <span style={{ color: val >= 0 ? '#3f8600' : '#cf1322' }}>
                        {val >= 0 ? '+' : ''}{val.toFixed(2)}%
                      </span>
                    )},
                    { title: '买入金额(元)', dataIndex: 'amount', key: 'amount', render: (val: number) => formatLargeNumber(val) },
                    { title: '活跃营业部', dataIndex: 'institutions', key: 'institutions', render: (ins: string[]) => (
                      <Space>
                        {ins.map(name => <Tag key={name} color="blue">{name}</Tag>)}
                      </Space>
                    )}
                  ]}
                  pagination={false}
                  rowKey="code"
                  size="middle"
                />
              </TabPane>
              <TabPane tab="卖出榜" key="sell">
                <Table
                  dataSource={[
                    { code: '601238', name: '广汽集团', price: 12.36, change_pct: -1.12, amount: 32548700, institutions: ['招商证券', '中信证券', '国泰君安'] },
                    { code: '601628', name: '中国人寿', price: 21.58, change_pct: -1.78, amount: 28964300, institutions: ['华泰证券', '银河证券', '中金公司'] },
                    { code: '600048', name: '保利发展', price: 15.25, change_pct: -2.68, amount: 25647800, institutions: ['国信证券', '广发证券', '中信建投'] },
                    { code: '601328', name: '交通银行', price: 5.37, change_pct: -0.92, amount: 21547900, institutions: ['光大证券', '中泰证券', '海通证券'] },
                    { code: '600487', name: '亨通光电', price: 18.67, change_pct: -3.42, amount: 19854600, institutions: ['国金证券', '东方证券', '申万宏源'] }
                  ]}
                  columns={[
                    { title: '代码', dataIndex: 'code', key: 'code' },
                    { title: '名称', dataIndex: 'name', key: 'name' },
                    { title: '价格', dataIndex: 'price', key: 'price', render: (price: number) => price.toFixed(2) },
                    { title: '涨跌幅', dataIndex: 'change_pct', key: 'change_pct', render: (val: number) => (
                      <span style={{ color: val >= 0 ? '#3f8600' : '#cf1322' }}>
                        {val >= 0 ? '+' : ''}{val.toFixed(2)}%
                      </span>
                    )},
                    { title: '卖出金额(元)', dataIndex: 'amount', key: 'amount', render: (val: number) => formatLargeNumber(val) },
                    { title: '活跃营业部', dataIndex: 'institutions', key: 'institutions', render: (ins: string[]) => (
                      <Space>
                        {ins.map(name => <Tag key={name} color="red">{name}</Tag>)}
                      </Space>
                    )}
                  ]}
                  pagination={false}
                  rowKey="code"
                  size="middle"
                />
              </TabPane>
            </Tabs>
          </Card>
        </TabPane>
      </Tabs>
    </div>
  );
};

export default MarketOverview;