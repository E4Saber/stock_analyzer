// src/components/common/Footer.tsx
import React from 'react';
import { Layout } from 'antd';

const { Footer: AntFooter } = Layout;

const Footer: React.FC = () => {
  return (
    <AntFooter style={{ textAlign: 'center', background: '#fff' }}>
      股票分析系统 ©{new Date().getFullYear()} Created with React & Ant Design
    </AntFooter>
  );
};

export default Footer;