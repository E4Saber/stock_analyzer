// src/components/widgets/IndexCardMinimal.tsx
import React from 'react';
import { Card, Statistic } from 'antd';
import { ArrowUpOutlined, ArrowDownOutlined } from '@ant-design/icons';
import { MinimalIndexData } from '../../types/market';

interface MinimalIndexCardProps {
  index: MinimalIndexData;
}

const MinimalIndexCard: React.FC<MinimalIndexCardProps> = ({ index }) => {
  const { name, current, change, change_pct } = index;
  
  // 判断涨跌
  const isPositive = change >= 0;
  
  // 样式配置
  const valueStyle = {
    color: isPositive ? '#3f8600' : '#cf1322',
  };
  
  // 指数涨跌图标
  const prefix = isPositive ? (
    <ArrowUpOutlined />
  ) : (
    <ArrowDownOutlined />
  );
  
  return (
    <Card>
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

export default MinimalIndexCard;