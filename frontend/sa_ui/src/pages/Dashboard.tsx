// src/pages/Dashboard.tsx
import React, { useEffect, useState } from 'react';
import { Row, Col, Card, Typography, Spin, Alert } from 'antd';
import { getMarketIndices, getMarketHeatmap, getHotStocks } from '../services/marketService';
import { MarketData, HeatmapData,  } from '../types/market';
import { HotStocksResponse } from '../types/stock';
import IndexCard from '../components/widgets/IndexCard';
import IndexChart from '../components/charts/IndexChart';
import HeatmapChart from '../components/charts/HeatmapChart';
import StockTable from '../components/widgets/StockTable';
import EnhancedIndexChart from '../components/charts/EnhancedIndexChart';

const { Title } = Typography;

const Dashboard: React.FC = () => {
  // 状态管理
  const [marketData, setMarketData] = useState<MarketData | null>(null);
  const [heatmapData, setHeatmapData] = useState<HeatmapData | null>(null);
  const [hotStocks, setHotStocks] = useState<HotStocksResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // 获取数据
  useEffect(() => {
    const fetchDashboardData = async () => {
      setLoading(true);
      try {
        // 并行获取多个API数据
        const [marketResponse
          // , heatmapResponse, hotStocksResponse
        ] = await Promise.all([
          getMarketIndices(),
          // getMarketHeatmap(),
          // getHotStocks()
        ]);
        
        setMarketData(marketResponse);
        // setHeatmapData(heatmapResponse);
        // setHotStocks(hotStocksResponse);
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
  if (loading && !marketData) {
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

  return (
    <div className="dashboard-container" style={{ padding: '16px' }}>
      <Title level={2}>市场概览</Title>
      
      {/* 指数卡片区域 */}
      <Row gutter={[16, 16]}>
        {marketData?.cn_indices.map(index => (
          <Col xs={24} sm={12} md={8} lg={6} key={index.ts_code}>
            <IndexCard index={index} />
          </Col>
        ))}
      </Row>
      
      <div style={{ height: '16px' }} />
      
      {/* 增强版图表区域 */}
      {/* <Row>
        <Col span={24}>
          <Card title="指数详细走势" bordered={false}>
            {marketData && 
              <EnhancedIndexChart 
                indices={marketData.cn_indices} 
                height={500}
                defaultPeriod="day"
                defaultChartType="line"
                fullWidth={true}
              />
            }
          </Card>
        </Col>
      </Row> */}
      
      <div style={{ height: '24px' }} />
      
      {/* 全球指数区域 - 使用增强版图表 */}
      <Title level={4}>全球市场</Title>
      {/* <Row>
        <Col span={24}>
          {marketData && 
            <EnhancedIndexChart 
              indices={marketData.global_indices} 
              height={400}
              defaultPeriod="day"
              defaultChartType="line"
              fullWidth={true}
            />
          }
        </Col>
      </Row> */}
      
      <div style={{ height: '24px' }} />
      
      {/* 热门股票列表 */}
      {/* <Row>
        <Col span={24}>
          <Card title="热门股票" bordered={false}>
            {hotStocks && <StockTable stocks={hotStocks.hot_stocks} />}
          </Card>
        </Col>
      </Row> */}
    </div>
  );
};

export default Dashboard;