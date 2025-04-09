// src/components/layout/Header.tsx
import React, { useState, useEffect } from 'react';
import { Avatar, Switch, Dropdown, Menu, Space } from 'antd';
import { 
  StockOutlined, 
  GlobalOutlined, 
  FireOutlined, 
  LineChartOutlined,
  CommentOutlined,
  UserOutlined,
  BulbOutlined,
  BulbFilled,
  DownOutlined,
  BarChartOutlined,
  FundOutlined
} from '@ant-design/icons';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import './Header.css';

const Header: React.FC = () => {
  const [darkMode, setDarkMode] = useState<boolean>(false);
  const location = useLocation();
  const navigate = useNavigate();
  
  // 主题切换处理函数
  const toggleTheme = () => {
    setDarkMode(!darkMode);
  };

  // 监听主题变化并应用到文档
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', darkMode ? 'dark' : 'light');
  }, [darkMode]);

  // 确定当前活动的导航项
  const isActive = (path: string) => {
    return location.pathname.startsWith(path);
  };

  // 市场二级菜单
  const marketMenuItems = [
    {
      key: '/market/overview',
      label: '市场概览',
      icon: <BarChartOutlined />
    },
    {
      key: '/market/sector',
      label: '行业板块',
      icon: <FundOutlined />
    },
    {
      key: '/market/index',
      label: '指数分析',
      icon: <LineChartOutlined />
    }
  ];

  // 股票二级菜单
  const stockMenuItems = [
    {
      key: '/stock/list',
      label: '股票一览',
      icon: <BarChartOutlined />
    },
    {
      key: '/stock/details',
      label: '个股详情',
      icon: <LineChartOutlined />
    }
  ];
  
  const handleMenuClick = ({ key }: { key: string }) => {
    navigate(key);
  };

  return (
    <header className="inprice-header">
      <div className="inprice-nav">
        <div className="inprice-logo">
          <Link to="/">
            <LineChartOutlined style={{ marginRight: '8px' }} /> In Price
          </Link>
        </div>
        
        <Link to="/macro">
          <div className={`nav-item ${isActive('/macro') ? 'active' : ''}`}>
            <GlobalOutlined style={{ marginRight: '6px' }} /> 宏观
          </div>
        </Link>
        
        <Link to="/hot-topics">
          <div className={`nav-item ${isActive('/hot') ? 'active' : ''}`}>
            <FireOutlined style={{ marginRight: '6px' }} /> 热点
          </div>
        </Link>
        
        <Dropdown 
          menu={{ 
            items: marketMenuItems, 
            onClick: handleMenuClick 
          }} 
          placement="bottom"
        >
          <div className={`nav-item dropdown-nav-item ${isActive('/market') ? 'active' : ''}`}>
            <Space>
              <StockOutlined /> 市场
              <DownOutlined style={{ fontSize: '12px' }} />
            </Space>
          </div>
        </Dropdown>

        <Dropdown 
          menu={{ 
            items: stockMenuItems, 
            onClick: handleMenuClick 
          }} 
          placement="bottom"
        >
          <div className={`nav-item dropdown-nav-item ${isActive('/stock') ? 'active' : ''}`}>
            <Space>
              <StockOutlined /> 股
              <DownOutlined style={{ fontSize: '12px' }} />
            </Space>
          </div>
        </Dropdown>
        
        <Link to="/quant">
          <div className={`nav-item ${isActive('/quant') ? 'active' : ''}`}>
            <LineChartOutlined style={{ marginRight: '6px' }} /> 量化
          </div>
        </Link>
        
        <Link to="/forum">
          <div className={`nav-item ${isActive('/forum') ? 'active' : ''}`}>
            <CommentOutlined style={{ marginRight: '6px' }} /> 论坛
          </div>
        </Link>
      </div>
      
      <div className="right-nav">
        <div className="theme-switcher">
          <Switch
            checked={darkMode}
            onChange={toggleTheme}
            checkedChildren={<BulbFilled />}
            unCheckedChildren={<BulbOutlined />}
            className="theme-switch"
          />
        </div>
        <Avatar 
          size={40} 
          icon={<UserOutlined />} 
          style={{ backgroundColor: '#1890ff', cursor: 'pointer', marginLeft: '16px' }} 
        />
      </div>
    </header>
  );
};

export default Header;