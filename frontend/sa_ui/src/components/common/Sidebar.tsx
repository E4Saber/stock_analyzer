// src/components/common/Sidebar.tsx
import React, { useState } from 'react';
import { Layout, Menu } from 'antd';
import {
  DashboardOutlined,
  LineChartOutlined,
  StockOutlined,
  HeartOutlined,
  SettingOutlined,
  BarChartOutlined,
  FireOutlined
} from '@ant-design/icons';
import { Link, useLocation } from 'react-router-dom';
import type { MenuProps } from 'antd';

const { Sider } = Layout;
type MenuItem = Required<MenuProps>['items'][number];

const Sidebar: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false);
  const location = useLocation();
  
  // Determine selected menu item based on current path
  const getSelectedKey = () => {
    const path = location.pathname;
    if (path.startsWith('/dashboard')) return ['dashboard'];
    if (path.startsWith('/market/overview')) return ['market_overview'];
    if (path.startsWith('/market/hotspot')) return ['market_hotspot'];
    if (path.startsWith('/stocks')) return ['stock_detail'];
    if (path.startsWith('/watchlist')) return ['watchlist'];
    if (path.startsWith('/settings')) return ['settings'];
    return ['dashboard'];
  };

  // Define menu items using the items property
  const items: MenuItem[] = [
    {
      key: 'dashboard',
      icon: <DashboardOutlined />,
      label: <Link to="/dashboard">首页</Link>
    },
    {
      key: 'market',
      icon: <LineChartOutlined />,
      label: '市场',
      children: [
        {
          key: 'market_overview',
          icon: <BarChartOutlined />,
          label: <Link to="/market/overview">市场概览</Link>
        },
        {
          key: 'market_hotspot',
          icon: <FireOutlined />,
          label: <Link to="/market/hotspot">市场热点</Link>
        }
      ]
    },
    {
      key: 'stock_detail',
      icon: <StockOutlined />,
      label: <Link to="/stocks/600519">股票详情</Link>
    },
    {
      key: 'watchlist',
      icon: <HeartOutlined />,
      label: <Link to="/watchlist">自选股</Link>
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: <Link to="/settings">系统设置</Link>
    }
  ];

  return (
    <Sider
      collapsible
      collapsed={collapsed}
      onCollapse={setCollapsed}
      width={200}
      style={{ background: '#fff' }}
    >
      <div style={{
        height: '64px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        margin: '16px 0',
      }}>
        <span style={{
          fontSize: collapsed ? '14px' : '18px',
          fontWeight: 'bold',
          color: '#1890ff',
          whiteSpace: 'nowrap',
          overflow: 'hidden',
          textOverflow: 'ellipsis'
        }}>
          {collapsed ? '股票' : '股票分析系统'}
        </span>
      </div>
      
      <Menu
        mode="inline"
        selectedKeys={getSelectedKey()}
        style={{ height: 'calc(100% - 96px)', borderRight: 0 }}
        items={items}
      />
    </Sider>
  );
};

export default Sidebar;