// src/App.tsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Layout, ConfigProvider } from 'antd';
import zhCN from 'antd/lib/locale/zh_CN';

// Import components
import Header from '../src/share/components/common/Header';
import Footer from '../src/share/components/common/Footer';

// pages
import Homepage from './features/home/pages/Homepage';
import MarketPage from './features/market/pages/MarketPage';
import MarketOverviewPage from './features/market/pages/MarketOverviewPage';
import MarketSectorPage from './features/market/pages/MarketSectorPage';
import MacroEconomyPage from './features/macroeconomics/pages/MacroEconomyPage';
import HotTopicsPage from './features/hottopics/pages/HotTopicsPage';

// Import styles
import './App.css';
import StockListPage from './features/stocks/pages/StockListPage';
import StockDetailsPage from './features/stocks/pages/StockDetailsPage';


const { Header: AntHeader, Content, Footer: AntFooter } = Layout;

const App: React.FC = () => {
  return (
    <ConfigProvider locale={zhCN}>
      <Router>
        <Layout className="page-container">

          <Content className="content-area">
            <AntHeader>
              <Header />
            </AntHeader>
            
            <Routes>
              <Route path="/" element={<Homepage />} />
              {/* 市场相关路由 */}
              <Route path="/market" element={<MarketPage />} />
              <Route path="/market/overview" element={<MarketOverviewPage />} />
              <Route path="/market/sector" element={<MarketSectorPage />} />

              {/* 宏观经济路由 */}
              <Route path="/macro" element={<MacroEconomyPage />} />

              {/* 热点话题路由 */}
              <Route path="/hot-topics" element={<HotTopicsPage />} />

              {/* 股 */}
              <Route path="/stock/list" element={<StockListPage />} />
              <Route path="/stock/details/:stockCode" element={<StockDetailsPage />} />
            </Routes>
            
            <AntFooter>
              <Footer />
            </AntFooter>
          </Content>
          
        </Layout>
      </Router>
    </ConfigProvider>
  );
};

export default App;