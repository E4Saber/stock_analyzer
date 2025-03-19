// src/components/widgets/IndexCard.tsx
import React from 'react';
import { Card, Statistic } from 'antd';
import { ArrowUpOutlined, ArrowDownOutlined } from '@ant-design/icons';
import { IndexData } from '../../types/market';

interface IndexCardProps {
  index: IndexData;
  size?: 'default' | 'small';
}

const IndexCard: React.FC<IndexCardProps> = ({ index, size = 'default' }) => {
  const { name, current, change, change_pct } = index;
  
  // Determine up/down
  const isPositive = change >= 0;
  
  // Style configuration
  const valueStyle = {
    color: isPositive ? '#3f8600' : '#cf1322',
  };
  
  // Index change icon
  const prefix = isPositive ? (
    <ArrowUpOutlined />
  ) : (
    <ArrowDownOutlined />
  );
  
  return (
    <Card size={size}>
      <Statistic
        title={name}
        value={current}
        precision={2}
        valueStyle={valueStyle}
        prefix={prefix}
      />
      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '8px' }}>
        <span style={{ color: valueStyle.color }}>
          {isPositive ? '+' : ''}{change.toFixed(2)}
        </span>
        <span style={{ color: valueStyle.color }}>
          {isPositive ? '+' : ''}{change_pct.toFixed(2)}%
        </span>
      </div>
    </Card>
  );
};

export default IndexCard;