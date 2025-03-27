// src/pages/MarketOverviewPage.tsx
import React from 'react';
import { Layout, Typography, Breadcrumb, Tabs } from 'antd';
import DashboardTab from './EconomicMonitor/DashboardTab';
import USEconomyTab from './EconomicMonitor/USEconomyTab';
import ChinaEconomyTab from './EconomicMonitor/ChinaEconomyTab';
import CrossIndicatorsTab from './EconomicMonitor/CrossIndicatorsTab';
import IndicatorDetail from './EconomicMonitor/IndicatorDetail';
import { IndicatorType } from '../types/indicator';

const { Content } = Layout;
const { Title } = Typography;
const { TabPane } = Tabs;

const EconomicMonitor: React.FC = () => {
  const [activeTab, setActiveTab] = React.useState('dashboard');
  const [selectedIndicator, setSelectedIndicator] = React.useState<IndicatorType | null>(null);
  
  // 当从仪表盘或指标列表选择一个指标时
  const handleIndicatorSelect = (indicator: IndicatorType): void => {
    setSelectedIndicator(indicator);
    
    // 自动切换到对应的tab页
    if (indicator) {
      if (indicator.region === 'us') {
        setActiveTab('us');
      } else if (indicator.region === 'china') {
        setActiveTab('china');
      } else if (indicator.region === 'cross') {
        setActiveTab('cross');
      }
    }
  };
  
  // 当切换回仪表盘时，清除选中指标
  const handleTabChange = (key: string): void => {
    setActiveTab(key);
    if (key === 'dashboard') {
      setSelectedIndicator(null);
    }
  };

  return (
    <Layout style={{ padding: '0 24px 24px' }}>
      <Breadcrumb style={{ margin: '16px 0' }}>
        <Breadcrumb.Item>首页</Breadcrumb.Item>
        <Breadcrumb.Item>市场</Breadcrumb.Item>
        <Breadcrumb.Item>市场概览</Breadcrumb.Item>
      </Breadcrumb>
      
      <Content
        style={{
          padding: 24,
          margin: 0,
          background: '#fff',
          borderRadius: 4
        }}
      >
        <Title level={4} style={{ marginBottom: 24 }}>宏观经济监测</Title>
        
        {/* 宏观经济监测模块内容 */}
        <div className="economic-monitor-container">
          <Tabs activeKey={activeTab} onChange={handleTabChange} type="card">
            <TabPane tab="仪表盘总览" key="dashboard">
              <DashboardTab onIndicatorSelect={handleIndicatorSelect} />
            </TabPane>
            
            <TabPane tab="美国经济指标" key="us">
              {selectedIndicator && selectedIndicator.region === 'us' ? (
                <IndicatorDetail 
                  indicator={selectedIndicator} 
                  onBack={() => setSelectedIndicator(null)} 
                />
              ) : (
                <USEconomyTab onIndicatorSelect={handleIndicatorSelect} />
              )}
            </TabPane>
            
            <TabPane tab="中国经济指标" key="china">
              {selectedIndicator && selectedIndicator.region === 'china' ? (
                <IndicatorDetail 
                  indicator={selectedIndicator} 
                  onBack={() => setSelectedIndicator(null)} 
                />
              ) : (
                <ChinaEconomyTab onIndicatorSelect={handleIndicatorSelect} />
              )}
            </TabPane>
            
            <TabPane tab="中美交叉指标" key="cross">
              {selectedIndicator && selectedIndicator.region === 'cross' ? (
                <IndicatorDetail 
                  indicator={selectedIndicator} 
                  onBack={() => setSelectedIndicator(null)} 
                />
              ) : (
                <CrossIndicatorsTab onIndicatorSelect={handleIndicatorSelect} />
              )}
            </TabPane>
          </Tabs>
        </div>
        
        {/* 此处可添加其他市场概览相关内容 */}
        <div style={{ marginTop: 40 }}>
          <Title level={4}>市场指数概览</Title>
          {/* 这里可以添加股指走势图表等 */}
        </div>
      </Content>
    </Layout>
  );
};

export default EconomicMonitor;