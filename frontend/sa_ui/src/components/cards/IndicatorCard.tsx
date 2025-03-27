// src/components/cards/IndicatorCard.tsx
import React from 'react';
import { Card, Statistic, Tooltip, Badge } from 'antd';
import { ArrowUpOutlined, ArrowDownOutlined } from '@ant-design/icons';
import MiniChart from '../charts/MiniChart';
import { IndicatorCardProps, IndicatorStatus, RegionType } from '../../types/indicator';

const statusColors: Record<IndicatorStatus, string> = {
  normal: '#52c41a', // 绿色
  warning: '#faad14', // 黄色
  alert: '#f5222d', // 红色
};

const IndicatorCard: React.FC<IndicatorCardProps> = ({ indicator, onClick }) => {
  const {
    id,
    name,
    value,
    unit,
    change,
    changeType, // 'increase' or 'decrease'
    status, // 'normal', 'warning', 'alert'
    trend, // trend data for mini chart
    region, // 'us', 'china', 'cross'
    category, // 'growth', 'employment', 'price', etc.
    updateTime,
  } = indicator;
  
  // 决定变化值的显示颜色
  // 注意：有些指标上升是好的(如GDP)，有些指标上升是不好的(如失业率)
  // 这里简化处理，根据changeType直接判断颜色
  const getChangeColor = (): string => {
    if (changeType === 'increase') {
      return '#3f8600'; // 绿色，表示积极变化
    } else if (changeType === 'decrease') {
      return '#cf1322'; // 红色，表示消极变化
    }
    return 'inherit';
  };
  
  // 获取地区标识
  const getRegionLabel = (): string => {
    switch (region) {
      case 'us':
        return '美';
      case 'china':
        return '中';
      case 'cross':
        return '跨';
      default:
        return '';
    }
  };
  
  // 获取地区背景色
  const getRegionColor = (region: RegionType): string => {
    const regionColors: Record<RegionType, string> = {
      us: '#1890ff',
      china: '#f5222d',
      cross: '#722ed1'
    };
    return regionColors[region];
  };
  
  return (
    <Card
      hoverable
      onClick={() => onClick(indicator)}
      className="indicator-card"
      style={{ height: '100%' }}
      bodyStyle={{ padding: '12px' }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 8 }}>
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <Badge color={statusColors[status]} />
          <Tooltip title={`${name} - 点击查看详情`}>
            <h3 style={{ margin: '0 0 0 8px', fontSize: 16 }}>{name}</h3>
          </Tooltip>
        </div>
        <div>
          <Badge
            count={getRegionLabel()}
            style={{ 
              backgroundColor: getRegionColor(region), 
              fontSize: 12 
            }}
          />
        </div>
      </div>
      
      <Statistic 
        value={value} 
        precision={2} 
        suffix={unit}
        valueStyle={{ fontSize: 20 }}
      />
      
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 8 }}>
        <div>
          <Statistic 
            value={change} 
            precision={2}
            valueStyle={{ 
              color: getChangeColor(),
              fontSize: 14 
            }}
            prefix={changeType === 'increase' ? <ArrowUpOutlined /> : <ArrowDownOutlined />}
            suffix="%"
          />
        </div>
        <Tooltip title="更新时间">
          <small style={{ color: '#999' }}>{updateTime}</small>
        </Tooltip>
      </div>
      
      {/* 迷你趋势图 */}
      <div style={{ marginTop: 12, height: 40 }}>
        <MiniChart 
          data={trend} 
          color={getChangeColor()} 
          height={40} 
        />
      </div>
    </Card>
  );
};

export default IndicatorCard;