// src/components/common/Header.tsx
import React from 'react';
import { Layout, Menu, Input, Space, Button, Typography } from 'antd';
import { SearchOutlined, BellOutlined, UserOutlined } from '@ant-design/icons';
import { Link } from 'react-router-dom';

const { Header: AntHeader } = Layout;
const { Title } = Typography;
const { Search } = Input;

const Header: React.FC = () => {
  return (
    <AntHeader style={{ 
      background: '#fff', 
      padding: '0 20px', 
      display: 'flex', 
      alignItems: 'center', 
      justifyContent: 'space-between',
      boxShadow: '0 2px 8px rgba(0, 0, 0, 0.06)'
    }}>
      <div style={{ display: 'flex', alignItems: 'center' }}>
        <Link to="/">
          <Title level={3} style={{ margin: 0, marginRight: '24px' }}>股票分析系统</Title>
        </Link>
      </div>
      
      <div style={{ flex: 1, maxWidth: '400px' }}>
        <Search
          placeholder="搜索股票代码/名称"
          allowClear
          enterButton={<SearchOutlined />}
          size="middle"
        />
      </div>
      
      <Space>
        <Button type="text" icon={<BellOutlined />} />
        <Button type="text" icon={<UserOutlined />} />
      </Space>
    </AntHeader>
  );
};

export default Header;

