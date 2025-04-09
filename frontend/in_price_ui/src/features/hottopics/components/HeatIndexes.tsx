import React from 'react';
import { Card, Row, Col, Statistic, Progress, Space, Tooltip } from 'antd';
import { 
  LineChartOutlined, 
  FireOutlined, 
  RiseOutlined, 
  EyeOutlined,
  InfoCircleOutlined 
} from '@ant-design/icons';

interface HeatIndexItem {
  title: string;
  value: number;
  icon: React.ReactNode;
  color: string;
  tooltip?: string;
}

interface HeatIndexesProps {
  indexes?: HeatIndexItem[];
}

// 默认热度指标数据
const defaultIndexes: HeatIndexItem[] = [
  {
    title: "政策热度",
    value: 92,
    icon: <FireOutlined />,
    color: '#f5222d',
    tooltip: "政策相关讨论的活跃度，数值越高表示政策影响越大"
  },
  {
    title: "市场波动",
    value: 78,
    icon: <LineChartOutlined />,
    color: '#fa8c16',
    tooltip: "市场价格变动的幅度和频率，数值越高表示市场波动越剧烈"
  },
  {
    title: "情绪指数",
    value: 65,
    icon: <RiseOutlined />,
    color: '#52c41a',
    tooltip: "市场整体情绪的指标，高于50表示乐观，低于50表示悲观"
  },
  {
    title: "关注度",
    value: 88,
    icon: <EyeOutlined />,
    color: '#1890ff',
    tooltip: "市场参与者对热点的关注程度，数值越高表示关注度越高"
  }
];

// 热度指标组件 - 优化版本
const HeatIndexes: React.FC<HeatIndexesProps> = ({ 
  indexes = defaultIndexes 
}) => {
  const colSpan = 24 / indexes.length;
  
  return (
    <Card 
      title={
        <Space size="small">
          <LineChartOutlined style={{ color: '#1890ff' }} />
          <span>市场热度指标</span>
        </Space>
      } 
      className="heat-indexes-card"
      size="small"
      bodyStyle={{ padding: '10px' }}
      style={{ marginBottom: 12 }}
    >
      <Row gutter={[8, 0]}>
        {indexes.map((index, i) => (
          <Col span={colSpan} key={i}>
            <Tooltip title={index.tooltip}>
              <div>
                <Statistic
                  title={
                    <Space size={2}>
                      <span style={{ fontSize: '12px', fontWeight: 'normal' }}>{index.title}</span>
                      {index.tooltip && <InfoCircleOutlined style={{ fontSize: '12px', color: '#8c8c8c' }} />}
                    </Space>
                  }
                  value={index.value}
                  valueStyle={{ color: index.color, fontSize: '20px', fontWeight: 'bold' }}
                  prefix={<span style={{ fontSize: '14px' }}>{index.icon}</span>}
                  suffix={<span style={{ fontSize: '12px' }}>/100</span>}
                />
                <Progress 
                  percent={index.value} 
                  showInfo={false} 
                  strokeColor={index.color} 
                  trailColor="#f0f0f0"
                  strokeWidth={5}
                  style={{ marginTop: 2 }}
                />
              </div>
            </Tooltip>
          </Col>
        ))}
      </Row>
    </Card>
  );
};

export default HeatIndexes;