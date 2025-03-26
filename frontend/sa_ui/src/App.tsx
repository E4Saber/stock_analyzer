// src/App.tsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Layout, ConfigProvider } from 'antd';
import zhCN from 'antd/lib/locale/zh_CN';

// Import components
import Header from './components/common/Header';
import Sidebar from './components/common/Sidebar';
import Footer from './components/common/Footer';
import Dashboard from './pages/Dashboard';
import MarketOverview from './pages/MarketOverview';
import MarketHotspot from './pages/MarketHotspot';
import StockDetail from './pages/StockDetail';
import StockDetailWithAI from './pages/StockDetailWithAI'; // 新添加的AI版本股票详情页

// Import styles
import './App.css';
import StockAmbushAnalysis from './components/widgets/StockAmbushAnalysis';

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