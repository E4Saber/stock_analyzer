// src/pages/MarketOverviewPage.tsx
import React from 'react';
import { Layout, Typography, Breadcrumb, Tabs, Modal } from 'antd';
// import DashboardTab from './parts/DashboardTab';
// import USEconomyTab from './parts/USEconomyTab';
// import ChinaEconomyTab from './parts/ChinaEconomyTab';
// import CrossIndicatorsTab from './parts/CrossIndicatorsTab';
// import IndicatorDetail from './parts/IndicatorDetail';
import { IndicatorType } from '../types/indicator';

const { Content } = Layout;
const { Title } = Typography;
const { TabPane } = Tabs;

const EconomicMonitor: React.FC = () => {
  const [activeTab, setActiveTab] = React.useState('dashboard');
  const [selectedIndicator, setSelectedIndicator] = React.useState<IndicatorType | null>(null);
  const [isModalVisible, setIsModalVisible] = React.useState(false);
  
  // 当从仪表盘或指标列表选择一个指标时
  const handleIndicatorSelect = (indicator: IndicatorType): void => {
    setSelectedIndicator(indicator);
    setIsModalVisible(true);
    
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

  // 关闭Modal
  const handleModalClose = () => {
    setIsModalVisible(false);
  };

  return (
    <Layout style={{ padding: '0 24px 24px' }}>
      
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
          <Tabs activeKey={activeTab} onChange={handleTabChange} type="card" destroyInactiveTabPane={true}>
            <TabPane tab="仪表盘总览" key="dashboard">
              {/* <DashboardTab onIndicatorSelect={handleIndicatorSelect} /> */}
            </TabPane>
            
            <TabPane tab="美国经济指标" key="us">
              {/* <USEconomyTab onIndicatorSelect={handleIndicatorSelect} /> */}
            </TabPane>
            
            <TabPane tab="中国经济指标" key="china">
              {/* <ChinaEconomyTab onIndicatorSelect={handleIndicatorSelect} /> */}
            </TabPane>
            
            <TabPane tab="中美交叉指标" key="cross">
              {/* <CrossIndicatorsTab onIndicatorSelect={handleIndicatorSelect} /> */}
            </TabPane>
          </Tabs>
        </div>
        
        {/* 指标详情Modal */}
        <Modal
          title={selectedIndicator?.name || "指标详情"}
          visible={isModalVisible}
          onCancel={handleModalClose}
          footer={null}
          width={1200}
          style={{ top: 20 }}
          destroyOnClose={true}
          bodyStyle={{ padding: '0', maxHeight: '80vh', overflow: 'auto' }}
        >
          {selectedIndicator && (
            <IndicatorDetail 
              indicator={selectedIndicator} 
              onBack={handleModalClose} 
            />
          )}
        </Modal>
        
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