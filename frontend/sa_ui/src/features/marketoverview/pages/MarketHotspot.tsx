// src/pages/MarketHotspot.tsx
import React, { useEffect, useState } from 'react';
import { 
  Row, Col, Card, Typography, Spin, Alert, List, Tag, Space, 
  Table, Divider, Tabs, Timeline, Button, Tooltip, Statistic
} from 'antd';
import { 
  FireOutlined, RiseOutlined, FallOutlined, BarChartOutlined, 
  FileTextOutlined, LinkOutlined, AppstoreOutlined, RightOutlined
} from '@ant-design/icons';
import { getMarketHotspots } from '../services/mockMarketService';
import { HotStock } from '../types/market';
import { formatLargeNumber } from '../../../shared/utils/numberFormatter';

const { Title, Text, Paragraph } = Typography;
const { TabPane } = Tabs;

interface MarketTrend {
  category: string;
  stocks: HotStock[];
  desc: string;
}

interface MarketNews {
  id: string;
  title: string;
  source: string;
  time: string;
  url: string;
}

const MarketHotspot: React.FC = () => {
  // 状态管理
  const [trends, setTrends] = useState<MarketTrend[]>([]);
  const [news, setNews] = useState<MarketNews[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // 获取数据
  useEffect(() => {
    const fetchHotspotData = async () => {
      setLoading(true);
      try {
        const data = await getMarketHotspots();
        setTrends(data.trends);
        setNews(data.news);
        setError(null);
      } catch (err) {
        console.error('获取市场热点数据失败:', err);
        setError('获取数据失败，请稍后重试');
      } finally {
        setLoading(false);
      }
    };

    fetchHotspotData();
    
    // 设置定时刷新（每5分钟）
    const intervalId = setInterval(() => {
      fetchHotspotData();
    }, 300000);

    return () => clearInterval(intervalId);
  }, []);

  // 加载状态
  if (loading && trends.length === 0) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
        <p>正在加载市场热点数据...</p>
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

  // 股票表格列
  const stockColumns = [
    {
      title: '代码',
      dataIndex: 'code',
      key: 'code',
      width: 90,
    },
    {
      title: '名称',
      dataIndex: 'name',
      key: 'name',
      width: 110,
    },
    {
      title: '价格',
      dataIndex: 'price',
      key: 'price',
      width: 90,
      render: (price: number) => price.toFixed(2),
    },
    {
      title: '涨跌幅',
      dataIndex: 'change_pct',
      key: 'change_pct',
      width: 90,
      render: (change_pct: number) => (
        <span style={{ color: change_pct >= 0 ? '#3f8600' : '#cf1322' }}>
          {change_pct >= 0 ? '+' : ''}{change_pct.toFixed(2)}%
        </span>
      ),
    },
    {
      title: '成交量',
      dataIndex: 'volume',
      key: 'volume',
      width: 100,
      render: (volume: number) => formatLargeNumber(volume),
    },
  ];

  return (
    <div className="market-hotspot-container">
      <Title level={2}>市场热点</Title>
      
      {/* 标签页 */}
      <Tabs defaultActiveKey="hotspots" className="hotspot-tabs">
        <TabPane 
          tab={<span><FireOutlined />热点板块</span>} 
          key="hotspots"
        >
          <Row gutter={[16, 16]}>
            {/* 热点板块列表 */}
            <Col xs={24} lg={16}>
              <List
                className="hotspot-list"
                itemLayout="vertical"
                dataSource={trends}
                renderItem={(item, index) => (
                  <List.Item>
                    <Card bordered={false} className="hotspot-card">
                      <Space direction="vertical" style={{ width: '100%' }}>
                        <div className="hotspot-header">
                          <Space align="center">
                            <Tag color="red" style={{ fontSize: '16px', padding: '4px 8px' }}>
                              HOT {index + 1}
                            </Tag>
                            <Title level={4} style={{ margin: 0 }}>{item.category}</Title>
                          </Space>
                        </div>
                        
                        <Divider style={{ margin: '12px 0' }} />
                        
                        <Paragraph>{item.desc}</Paragraph>
                        
                        <Table 
                          dataSource={item.stocks}
                          columns={stockColumns}
                          pagination={false}
                          rowKey="code"
                          size="small"
                          style={{ marginTop: '12px' }}
                        />
                        
                        <div style={{ textAlign: 'right', marginTop: '8px' }}>
                          <Button type="link" size="small">
                            查看更多相关股票 <RightOutlined />
                          </Button>
                        </div>
                      </Space>
                    </Card>
                  </List.Item>
                )}
              />
            </Col>
            
            {/* 市场新闻 */}
            <Col xs={24} lg={8}>
              <Card 
                title={<span><FileTextOutlined /> 最新要闻</span>} 
                bordered={false}
                className="news-card"
              >
                <Timeline mode="left">
                  {news.map(item => (
                    <Timeline.Item key={item.id} label={item.time.substring(11)}>
                      <div className="news-item">
                        <Tooltip title="点击查看详情">
                          <a href={item.url} target="_blank" rel="noopener noreferrer">
                            {item.title}
                          </a>
                        </Tooltip>
                        <div className="news-source">
                          <Text type="secondary">{item.source}</Text>
                        </div>
                      </div>
                    </Timeline.Item>
                  ))}
                </Timeline>
                
                <div style={{ textAlign: 'center', marginTop: '16px' }}>
                  <Button type="link">查看更多新闻 <RightOutlined /></Button>
                </div>
              </Card>
              
              <div style={{ marginTop: '16px' }}>
                <Card 
                  title={<span><BarChartOutlined /> 热门概念</span>} 
                  bordered={false}
                  className="concept-card"
                >
                  <Space wrap>
                    <Tag color="magenta">半导体国产化</Tag>
                    <Tag color="red">新能源汽车</Tag>
                    <Tag color="volcano">ChatGPT概念</Tag>
                    <Tag color="orange">光伏产业</Tag>
                    <Tag color="gold">储能</Tag>
                    <Tag color="lime">数字货币</Tag>
                    <Tag color="green">低碳环保</Tag>
                    <Tag color="cyan">新型显示</Tag>
                    <Tag color="blue">云计算</Tag>
                    <Tag color="geekblue">国产软件</Tag>
                    <Tag color="purple">元宇宙</Tag>
                    <Tag color="magenta">人工智能</Tag>
                    <Tag color="red">军工</Tag>
                    <Tag color="volcano">大数据</Tag>
                    <Tag color="orange">网络安全</Tag>
                  </Space>
                </Card>
              </div>
            </Col>
          </Row>
        </TabPane>
        
        <TabPane 
          tab={<span><AppstoreOutlined />资金流向</span>} 
          key="capital"
        >
          <Row gutter={[16, 16]}>
            <Col xs={24} md={12}>
              <Card title="行业资金流向" bordered={false}>
                <Table
                  dataSource={[
                    { rank: 1, sector: '半导体', amount: 25.68, ratio: 3.25 },
                    { rank: 2, sector: '新能源', amount: 18.45, ratio: 2.87 },
                    { rank: 3, sector: '医药制造', amount: 12.36, ratio: 1.95 },
                    { rank: 4, sector: '计算机', amount: 10.28, ratio: 1.56 },
                    { rank: 5, sector: '电子元件', amount: 9.76, ratio: 1.32 },
                    { rank: 6, sector: '通信设备', amount: 7.82, ratio: 0.98 },
                    { rank: 7, sector: '食品饮料', amount: 6.54, ratio: 0.87 },
                    { rank: 8, sector: '电力设备', amount: 5.87, ratio: 0.76 },
                  ]}
                  columns={[
                    { title: '排名', dataIndex: 'rank', key: 'rank', width: 70 },
                    { title: '行业', dataIndex: 'sector', key: 'sector' },
                    { title: '净流入(亿)', dataIndex: 'amount', key: 'amount', render: (val: number) => (
                      <span style={{ color: '#3f8600' }}>+{val.toFixed(2)}</span>
                    )},
                    { title: '净额占比(%)', dataIndex: 'ratio', key: 'ratio', render: (val: number) => `${val.toFixed(2)}%` },
                  ]}
                  pagination={false}
                  rowKey="rank"
                  size="middle"
                />
              </Card>
            </Col>
            <Col xs={24} md={12}>
              <Card title="行业资金流出" bordered={false}>
                <Table
                  dataSource={[
                    { rank: 1, sector: '房地产', amount: -18.65, ratio: -2.78 },
                    { rank: 2, sector: '钢铁', amount: -12.37, ratio: -1.86 },
                    { rank: 3, sector: '银行', amount: -10.45, ratio: -1.58 },
                    { rank: 4, sector: '煤炭', amount: -8.76, ratio: -1.32 },
                    { rank: 5, sector: '保险', amount: -7.54, ratio: -1.16 },
                    { rank: 6, sector: '有色金属', amount: -6.83, ratio: -1.02 },
                    { rank: 7, sector: '建筑建材', amount: -5.42, ratio: -0.83 },
                    { rank: 8, sector: '水泥', amount: -4.67, ratio: -0.72 },
                  ]}
                  columns={[
                    { title: '排名', dataIndex: 'rank', key: 'rank', width: 70 },
                    { title: '行业', dataIndex: 'sector', key: 'sector' },
                    { title: '净流出(亿)', dataIndex: 'amount', key: 'amount', render: (val: number) => (
                      <span style={{ color: '#cf1322' }}>{val.toFixed(2)}</span>
                    )},
                    { title: '净额占比(%)', dataIndex: 'ratio', key: 'ratio', render: (val: number) => `${val.toFixed(2)}%` },
                  ]}
                  pagination={false}
                  rowKey="rank"
                  size="middle"
                />
              </Card>
            </Col>
          </Row>
          
          <div style={{ height: '16px' }} />
          
          <Card title="个股资金流向排行" bordered={false}>
            <Tabs defaultActiveKey="inflow">
              <TabPane tab="流入排行" key="inflow">
                <Table
                  dataSource={[
                    { code: '603501', name: '韦尔股份', price: 86.23, change_pct: 4.72, amount: 5.68, ratio: 1.25 },
                    { code: '300750', name: '宁德时代', price: 156.83, change_pct: 1.98, amount: 4.86, ratio: 1.12 },
                    { code: '688012', name: '中微公司', price: 65.89, change_pct: 5.23, amount: 4.21, ratio: 1.05 },
                    { code: '002594', name: '比亚迪', price: 228.63, change_pct: 2.16, amount: 3.75, ratio: 0.92 },
                    { code: '600519', name: '贵州茅台', price: 1782.50, change_pct: 1.25, amount: 3.52, ratio: 0.86 },
                    { code: '603986', name: '兆易创新', price: 118.56, change_pct: 3.87, amount: 3.24, ratio: 0.78 },
                    { code: '600587', name: '新华医疗', price: 26.75, change_pct: 7.58, amount: 2.87, ratio: 0.69 },
                    { code: '603259', name: '药明康德', price: 68.32, change_pct: 3.25, amount: 2.65, ratio: 0.64 },
                    { code: '600438', name: '通威股份', price: 18.25, change_pct: 3.75, amount: 2.52, ratio: 0.61 },
                    { code: '300759', name: '康龙化成', price: 45.28, change_pct: 2.56, amount: 2.18, ratio: 0.53 },
                  ]}
                  columns={[
                    { title: '代码', dataIndex: 'code', key: 'code', width: 90 },
                    { title: '名称', dataIndex: 'name', key: 'name' },
                    { title: '价格', dataIndex: 'price', key: 'price', render: (val: number) => val.toFixed(2) },
                    { title: '涨跌幅(%)', dataIndex: 'change_pct', key: 'change_pct', render: (val: number) => (
                      <span style={{ color: val >= 0 ? '#3f8600' : '#cf1322' }}>
                        {val >= 0 ? '+' : ''}{val.toFixed(2)}%
                      </span>
                    )},
                    { title: '净流入(亿)', dataIndex: 'amount', key: 'amount', render: (val: number) => (
                      <span style={{ color: '#3f8600' }}>+{val.toFixed(2)}</span>
                    )},
                    { title: '净额占比(%)', dataIndex: 'ratio', key: 'ratio', render: (val: number) => `${val.toFixed(2)}%` },
                  ]}
                  pagination={false}
                  rowKey="code"
                  size="middle"
                />
              </TabPane>
              <TabPane tab="流出排行" key="outflow">
                <Table
                  dataSource={[
                    { code: '601238', name: '广汽集团', price: 12.36, change_pct: -1.12, amount: -3.45, ratio: -0.86 },
                    { code: '600048', name: '保利发展', price: 15.25, change_pct: -2.68, amount: -3.26, ratio: -0.82 },
                    { code: '601628', name: '中国人寿', price: 21.58, change_pct: -1.78, amount: -2.98, ratio: -0.75 },
                    { code: '600487', name: '亨通光电', price: 18.67, change_pct: -3.42, amount: -2.76, ratio: -0.69 },
                    { code: '601857', name: '中国石油', price: 5.82, change_pct: -0.85, amount: -2.54, ratio: -0.64 },
                    { code: '601328', name: '交通银行', price: 5.37, change_pct: -0.92, amount: -2.18, ratio: -0.55 },
                    { code: '601088', name: '中国神华', price: 28.74, change_pct: -1.24, amount: -1.96, ratio: -0.49 },
                    { code: '601998', name: '中信银行', price: 4.67, change_pct: -0.64, amount: -1.85, ratio: -0.46 },
                    { code: '601288', name: '农业银行', price: 3.39, change_pct: -0.59, amount: -1.73, ratio: -0.43 },
                    { code: '600019', name: '宝钢股份', price: 6.85, change_pct: -1.58, amount: -1.62, ratio: -0.41 },
                  ]}
                  columns={[
                    { title: '代码', dataIndex: 'code', key: 'code', width: 90 },
                    { title: '名称', dataIndex: 'name', key: 'name' },
                    { title: '价格', dataIndex: 'price', key: 'price', render: (val: number) => val.toFixed(2) },
                    { title: '涨跌幅(%)', dataIndex: 'change_pct', key: 'change_pct', render: (val: number) => (
                      <span style={{ color: val >= 0 ? '#3f8600' : '#cf1322' }}>
                        {val >= 0 ? '+' : ''}{val.toFixed(2)}%
                      </span>
                    )},
                    { title: '净流出(亿)', dataIndex: 'amount', key: 'amount', render: (val: number) => (
                      <span style={{ color: '#cf1322' }}>{val.toFixed(2)}</span>
                    )},
                    { title: '净额占比(%)', dataIndex: 'ratio', key: 'ratio', render: (val: number) => `${val.toFixed(2)}%` },
                  ]}
                  pagination={false}
                  rowKey="code"
                  size="middle"
                />
              </TabPane>
            </Tabs>
          </Card>
        </TabPane>
        
        <TabPane 
          tab={<span><RiseOutlined />涨停分析</span>} 
          key="limitup"
        >
          <Row gutter={[16, 16]}>
            <Col xs={24} lg={16}>
              <Card title="涨停原因分析" bordered={false}>
                <Table
                  dataSource={[
                    { 
                      reason: '半导体国产化提速', 
                      count: 12, 
                      ratio: 13.8,
                      codes: ['603501', '603986', '688012', '688536', '688981']
                    },
                    { 
                      reason: '新能源汽车产业链', 
                      count: 10, 
                      ratio: 11.5,
                      codes: ['300750', '002594', '600438', '002812', '603799']
                    },
                    { 
                      reason: '医药创新突破', 
                      count: 8, 
                      ratio: 9.2,
                      codes: ['600587', '603259', '300759', '688221', '600276']
                    },
                    { 
                      reason: '数字经济发展', 
                      count: 7, 
                      ratio: 8.0,
                      codes: ['688268', '603444', '600845', '300625', '688169']
                    },
                    { 
                      reason: '光伏新技术', 
                      count: 6, 
                      ratio: 6.9,
                      codes: ['601012', '688599', '603185', '688408', '300118']
                    }
                  ]}
                  columns={[
                    { title: '涨停原因', dataIndex: 'reason', key: 'reason' },
                    { title: '涨停家数', dataIndex: 'count', key: 'count' },
                    { title: '占比(%)', dataIndex: 'ratio', key: 'ratio', render: (val: number) => `${val.toFixed(1)}%` },
                    { title: '代表股票', dataIndex: 'codes', key: 'codes', render: (codes: string[]) => (
                      <Space wrap>
                        {codes.map(code => (
                          <Tag key={code} color="red">{code}</Tag>
                        ))}
                      </Space>
                    )},
                  ]}
                  pagination={false}
                  rowKey="reason"
                  size="middle"
                />
              </Card>
            </Col>
            <Col xs={24} lg={8}>
              <Card title="涨停板统计" bordered={false}>
                <Statistic
                  title="今日涨停数量"
                  value={87}
                  valueStyle={{ color: '#cf1322', fontSize: '28px' }}
                  prefix={<RiseOutlined />}
                  suffix="家"
                />
                <Divider style={{ margin: '16px 0' }} />
                <Row gutter={[16, 16]}>
                  <Col span={12}>
                    <Statistic
                      title="一字板数量"
                      value={32}
                      valueStyle={{ color: '#cf1322' }}
                    />
                  </Col>
                  <Col span={12}>
                    <Statistic
                      title="涨停首板"
                      value={54}
                      valueStyle={{ color: '#cf1322' }}
                    />
                  </Col>
                  <Col span={12}>
                    <Statistic
                      title="连续涨停"
                      value={18}
                      valueStyle={{ color: '#cf1322' }}
                    />
                  </Col>
                  <Col span={12}>
                    <Statistic
                      title="炸板率"
                      value="32.5%"
                      valueStyle={{ color: '#faad14' }}
                    />
                  </Col>
                </Row>
                <Divider style={{ margin: '16px 0' }} />
                <Statistic
                  title="今日跌停数量"
                  value={35}
                  valueStyle={{ color: '#3f8600', fontSize: '28px' }}
                  prefix={<FallOutlined />}
                  suffix="家"
                />
              </Card>
            </Col>
          </Row>
        </TabPane>
      </Tabs>
    </div>
  );
};

export default MarketHotspot;