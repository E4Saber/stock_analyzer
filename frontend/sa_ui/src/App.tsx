// src/App.tsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Layout, ConfigProvider } from 'antd';
import zhCN from 'antd/lib/locale/zh_CN';

// Import components
import Header from './shared/components/common/Header';
import Sidebar from './shared/components/common/Sidebar';
import Footer from './shared/components/common/Footer';
import Dashboard from './features/dashboard/pages/Dashboard';
import MarketOverview from './features/marketoverview/pages/MarketOverview';
import MarketHotspot from './features/marketoverview/pages/MarketHotspot';
import StockDetail from './features/stockinsight/pages/StockDetail';
import StockDetailWithAI from './features/stockinsight/pages/StockDetailWithAI'; // 新添加的AI版本股票详情页

// Import styles
import './App.css';
import StockAmbushAnalysis from './features/stockinsight/pages/StockAmbushAnalysis';
import EconomicMonitor from './features/economicmonitor/pages/EconomicMonitor';

const { Content } = Layout;

const App: React.FC = () => {
  return (
    <ConfigProvider locale={zhCN}>
      <Router>
        <Layout style={{ minHeight: '100vh' }}>
          <Header />
          <Layout>
            <Sidebar />
            <Layout style={{ padding: '0 24px 24px' }}>
              <Content
                style={{
                  background: '#fff',
                  padding: 24,
                  margin: '16px 0',
                  minHeight: 280,
                }}
              >
                <Routes>
                  <Route path="/dashboard" element={<Dashboard />} />
                  <Route path="/market/overview" element={<MarketOverview />} />
                  <Route path="/market/hotspot" element={<MarketHotspot />} />
                  <Route path="/stocks/:code" element={<StockDetail />} />
                  <Route path='/ambush_predictive' element={<StockAmbushAnalysis />} />
                  <Route path="/economic_monitor" element={<EconomicMonitor />} />
                  <Route path="/stocks-ai/:code" element={<StockDetailWithAI />} /> {/* 新添加的AI路由 */}
                  <Route path="/" element={<Navigate to="/dashboard" replace />} />
                </Routes>
              </Content>
              <Footer />
            </Layout>
          </Layout>
        </Layout>
      </Router>
    </ConfigProvider>
  );
};

export default App;