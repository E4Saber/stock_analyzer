// src/components/cards/DataSummaryCard.tsx
import React from 'react';
import { Card, Statistic, Typography, Divider, Tooltip } from 'antd';
import { ArrowUpOutlined, ArrowDownOutlined, InfoCircleOutlined } from '@ant-design/icons';
import { DataSummaryCardProps, TrendType } from '../../types/indicator';

const { Text } = Typography;

const DataSummaryCard: React.FC<DataSummaryCardProps> = ({ 
  title, 
  data, 
  style 
}) => {
  const { max, min, avg, trend } = data;
  
  // 获取趋势颜色
  const getTrendColor = (trend: TrendType): string => {
    return trend === 'up' ? '#f5222d' : trend === 'down' ? '#52c41a' : '#8c8c8c';
  };
  
  // 获取趋势图标
  const getTrendIcon = (trend: TrendType) => {
    return trend === 'up' ? <ArrowUpOutlined /> : trend === 'down' ? <ArrowDownOutlined /> : null;
  };

  return (
    <Card 
      title={title || "数据概览"} 
      size="small"
      style={style}
    >
      <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
        <div>
          <Text type="secondary" style={{ marginRight: 4 }}>趋势</Text>
          <Text 
            style={{ 
              color: getTrendColor(trend),
              fontWeight: 'bold'
            }}
          >
            {getTrendIcon(trend)} {trend === 'up' ? '上升' : trend === 'down' ? '下降' : '平稳'}
          </Text>
        </div>
        
        <Divider style={{ margin: '8px 0' }} />
        
        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <div>
            <Tooltip title="时间范围内的最大值">
              <Text type="secondary" style={{ display: 'block' }}>
                最大值 <InfoCircleOutlined style={{ fontSize: 12 }} />
              </Text>
            </Tooltip>
            <Statistic 
              value={max} 
              precision={2} 
              valueStyle={{ fontSize: 16 }} 
            />
          </div>
          
          <div>
            <Tooltip title="时间范围内的最小值">
              <Text type="secondary" style={{ display: 'block' }}>
                最小值 <InfoCircleOutlined style={{ fontSize: 12 }} />
              </Text>
            </Tooltip>
            <Statistic 
              value={min} 
              precision={2} 
              valueStyle={{ fontSize: 16 }} 
            />
          </div>
        </div>
        
        <div>
          <Tooltip title="时间范围内的平均值">
            <Text type="secondary" style={{ display: 'block' }}>
              平均值 <InfoCircleOutlined style={{ fontSize: 12 }} />
            </Text>
          </Tooltip>
          <Statistic 
            value={avg} 
            precision={2} 
            valueStyle={{ fontSize: 16 }} 
          />
        </div>
      </div>
    </Card>
  );
};

export default DataSummaryCard;