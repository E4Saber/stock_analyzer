// src/App.tsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Layout, ConfigProvider } from 'antd';
import zhCN from 'antd/lib/locale/zh_CN';

// Import components
import Header from '../src/share/components/common/Header';
import Footer from '../src/share/components/common/Footer';

// pages
import Homepage from '../src/features/home/pages/Homepage';
import MarketPage from '../src/features/market/pages/MarketPage';
import MarketOverviewPage from '../src/features/market/pages/MarketOverviewPage';
import MacroEconomyPage from '../src/features/macroeconomics/pages/MacroEconomyPage';
import HotTopicsPage from '../src/features/hottopics/pages/HotTopicsPage';

// Import styles
import './App.css';
import StockListPage from './features/stocks/pages/StockListPage';
// 如果使用单独的导航样式文件，取消下面的注释
// import './styles/navigation.css';

const { Header: AntHeader, Content, Footer: AntFooter } = Layout;

const App: React.FC = () => {
  return (
    <ConfigProvider locale={zhCN}>
      <Router>
        <Layout className="page-container">
          <AntHeader>
            <Header />
          </AntHeader>

          <Content className="content-area">
            <Routes>
              <Route path="/" element={<Homepage />} />
              {/* 市场相关路由 */}
              <Route path="/market" element={<MarketPage />} />
              <Route path="/market/overview" element={<MarketOverviewPage />} />
              
              {/* 宏观经济路由 */}
              <Route path="/macro" element={<MacroEconomyPage />} />

              {/* 热点话题路由 */}
              <Route path="/hot-topics" element={<HotTopicsPage />} />

              {/* 股 */}
              <Route path="/stock/list" element={<StockListPage />} />
            </Routes>
          </Content>
          
          <AntFooter>
            <Footer />
          </AntFooter>
        </Layout>
      </Router>
    </ConfigProvider>
  );
};

export default App;