// src/pages/Dashboard.tsx
import React, { useEffect, useState } from 'react';
import { Row, Col, Card, Typography, Spin, Alert, Tabs } from 'antd';
import { 
  RiseOutlined, FallOutlined, DashboardOutlined, 
  FireOutlined, LineChartOutlined
} from '@ant-design/icons';
import { getMinimalMarketIndices, getMarketHeatmap, getHotStocks } from '../services/mockMarketService';
import { IndexData, SectorData, HotStock } from '../types/market';
import MinimalIndexCard from '../components/widgets/MinimalIndexCard';
import HeatmapChart from '../components/charts/HeatmapChart';
import StockTable from '../components/widgets/StockTable';
import EnhancedIndexChart from '../components/charts/EnhancedIndexChart';

const { Title } = Typography;
const { TabPane } = Tabs;

const Dashboard: React.FC = () => {
  // 状态管理
  const [marketIndices, setMarketIndices] = useState<IndexData[]>([]);
  const [sectorData, setSectorData] = useState<SectorData[]>([]);
  const [hotStocks, setHotStocks] = useState<HotStock[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // 获取数据
  useEffect(() => {
    const fetchDashboardData = async () => {
      setLoading(true);
      try {
        // 并行获取多个API数据
        const [indicesResponse, heatmapResponse, hotStocksResponse] = await Promise.all([
          getMinimalMarketIndices(),
          getMarketHeatmap(),
          getHotStocks()
        ]);
        
        setMarketIndices(indicesResponse);
        setSectorData(heatmapResponse.sectors);
        setHotStocks(hotStocksResponse.hot_stocks);
        setError(null);
      } catch (err) {
        console.error('获取仪表盘数据失败:', err);
        setError('获取数据失败，请稍后重试');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();

    // 设置定时刷新（每60秒）
    const intervalId = setInterval(() => {
      fetchDashboardData();
    }, 60000);

    // 组件卸载时清除定时器
    return () => clearInterval(intervalId);
  }, []);

  // 加载状态
  if (loading && marketIndices.length === 0) {
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

  // 统计涨跌股票
  const riseCount = hotStocks.filter(stock => stock.change_pct > 0).length;
  const fallCount = hotStocks.filter(stock => stock.change_pct <= 0).length;

  return (
    <div className="dashboard-container">
      <Title level={2}>市场概览</Title>
      
      {/* 指数卡片区域 */}
      <Row gutter={[16, 16]} className="market-indices-section">
        {marketIndices.map(index => (
          <Col xs={24} sm={12} md={8} lg={6} key={index.code}>
            <MinimalIndexCard index={index} />
          </Col>
        ))}
      </Row>
      
      <div style={{ height: '24px' }} />
      
      {/* 市场统计卡片 */}
      <Row gutter={[16, 16]} className="market-stats-section">
        <Col xs={24} sm={12} md={8} lg={6}>
          <Card>
            <Row align="middle" gutter={16}>
              <Col>
                <RiseOutlined style={{ fontSize: '24px', color: '#52c41a' }} />
              </Col>
              <Col>
                <div>上涨家数</div>
                <div style={{ fontSize: '24px', fontWeight: 'bold' }}>{riseCount}</div>
              </Col>
            </Row>
          </Card>
        </Col>
        <Col xs={24} sm={12} md={8} lg={6}>
          <Card>
            <Row align="middle" gutter={16}>
              <Col>
                <FallOutlined style={{ fontSize: '24px', color: '#f5222d' }} />
              </Col>
              <Col>
                <div>下跌家数</div>
                <div style={{ fontSize: '24px', fontWeight: 'bold' }}>{fallCount}</div>
              </Col>
            </Row>
          </Card>
        </Col>
        <Col xs={24} sm={12} md={8} lg={6}>
          <Card>
            <Row align="middle" gutter={16}>
              <Col>
                <DashboardOutlined style={{ fontSize: '24px', color: '#1890ff' }} />
              </Col>
              <Col>
                <div>行业板块数</div>
                <div style={{ fontSize: '24px', fontWeight: 'bold' }}>{sectorData.length}</div>
              </Col>
            </Row>
          </Card>
        </Col>
        <Col xs={24} sm={12} md={8} lg={6}>
          <Card>
            <Row align="middle" gutter={16}>
              <Col>
                <FireOutlined style={{ fontSize: '24px', color: '#fa8c16' }} />
              </Col>
              <Col>
                <div>热门股票</div>
                <div style={{ fontSize: '24px', fontWeight: 'bold' }}>{hotStocks.length}</div>
              </Col>
            </Row>
          </Card>
        </Col>
      </Row>
      
      <div style={{ height: '24px' }} />
      
      {/* 主要内容区 */}
      <Tabs defaultActiveKey="market" className="dashboard-tabs">
        <TabPane 
          tab={<span><LineChartOutlined />指数走势</span>} 
          key="market"
        >
          <Card title="主要指数走势" bordered={false}>
            <EnhancedIndexChart 
              indices={marketIndices} 
              height={400}
              showHeader={true}
              defaultPeriod="day"
              defaultChartType="line"
              fullWidth={true}
            />
          </Card>
        </TabPane>
        
        <TabPane 
          tab={<span><RiseOutlined />板块热力图</span>} 
          key="heatmap"
        >
          <Card title="行业板块热力图" bordered={false}>
            <HeatmapChart data={sectorData} />
          </Card>
        </TabPane>
        
        <TabPane 
          tab={<span><FireOutlined />热门股票</span>} 
          key="hotStocks"
        >
          <Card title="热门股票列表" bordered={false}>
            <StockTable stocks={hotStocks} />
          </Card>
        </TabPane>
      </Tabs>
      
      <div style={{ height: '24px' }} />
      
      {/* 行业板块列表 */}
      <Card title="行业板块列表" bordered={false} className="sectors-list-card">
        <Row gutter={[16, 16]}>
          {sectorData.map(sector => (
            <Col xs={24} sm={12} md={8} lg={6} key={sector.name}>
              <Card size="small">
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span>{sector.name}</span>
                  <span style={{ 
                    color: sector.change_pct >= 0 ? '#52c41a' : '#f5222d',
                    fontWeight: 'bold'
                  }}>
                    {sector.change_pct >= 0 ? '+' : ''}{sector.change_pct.toFixed(2)}%
                  </span>
                </div>
              </Card>
            </Col>
          ))}
        </Row>
      </Card>
    </div>
  );
};

export default Dashboard;