// src/components/common/Sidebar.tsx
import React, { useState } from 'react';
import { Layout, Menu } from 'antd';
import {
  DashboardOutlined,
  LineChartOutlined,
  StockOutlined,
  HeartOutlined,
  SettingOutlined
} from '@ant-design/icons';
import { Link, useLocation } from 'react-router-dom';

const { Sider } = Layout;

const Sidebar: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false);
  const location = useLocation();
  
  // 根据当前路径确定选中的菜单项
  const getSelectedKey = () => {
    const path = location.pathname;
    if (path.includes('/dashboard')) return ['dashboard'];
    if (path.includes('/market')) return ['market'];
    if (path.includes('/stocks')) return ['stocks'];
    if (path.includes('/watchlist')) return ['watchlist'];
    if (path.includes('/settings')) return ['settings'];
    return ['dashboard'];
  };

  const menuItems = [
    { key: 'dashboard', icon: <DashboardOutlined />, label: <Link to="/dashboard">首页</Link> },
    { key: 'market', icon: <LineChartOutlined />, label: <Link to="/market">市场概览</Link> },
    { key: 'stocks', icon: <StockOutlined />, label: <Link to="/stocks">股票详情</Link> },
    { key: 'watchlist', icon: <HeartOutlined />, label: <Link to="/watchlist">自选股</Link> },
    { key: 'settings', icon: <SettingOutlined />, label: <Link to="/settings">系统设置</Link> },
  ];

  return (
    <Sider
      collapsible
      collapsed={collapsed}
      onCollapse={setCollapsed}
      width={200}
      style={{ background: '#fff' }}
    >
      <Menu
        mode="inline"
        selectedKeys={getSelectedKey()}
        style={{ height: '100%', borderRight: 0 }}
        items={menuItems}
      >
        {/* <Menu.Item key="dashboard" icon={<DashboardOutlined />}> 废弃
          <Link to="/dashboard">首页</Link>
        </Menu.Item>
        <Menu.Item key="market" icon={<LineChartOutlined />}>
          <Link to="/market">市场概览</Link>
        </Menu.Item>
        <Menu.Item key="stocks" icon={<StockOutlined />}>
          <Link to="/stocks">股票详情</Link>
        </Menu.Item>
        <Menu.Item key="watchlist" icon={<HeartOutlined />}>
          <Link to="/watchlist">自选股</Link>
        </Menu.Item>
        <Menu.Item key="settings" icon={<SettingOutlined />}>
          <Link to="/settings">系统设置</Link>
        </Menu.Item> */}
      </Menu>
    </Sider>
  );
};

export default Sidebar;