import React from 'react';
import { Card, Tag, Space, Typography } from 'antd';
import { 
  FireOutlined, 
  RiseOutlined, 
  FallOutlined, 
  ClockCircleOutlined,
  EyeOutlined,
  MessageOutlined,
  HeartOutlined
} from '@ant-design/icons';

const { Text, Paragraph } = Typography;

// 接口定义
export interface HotTopicItem {
  id: string;
  title: string;
  summary?: string;
  timestamp: string;
  heat: number;
  impact?: 'high' | 'medium' | 'low';
  category: string;
  tags?: string[];
  sentiment?: number;
  relatedAssets?: string[];
  views?: number;
  comments?: number;
  likes?: number;
}

interface HotTopicCardProps {
  topic: HotTopicItem;
  size?: 'small' | 'default' | 'large';
  onClick?: (topic: HotTopicItem) => void;
}

// 获取热度对应的颜色
export const getHeatColor = (heat: number) => {
  if (heat >= 90) return '#f5222d';
  if (heat >= 80) return '#fa541c';
  if (heat >= 70) return '#fa8c16';
  if (heat >= 60) return '#faad14';
  return '#fadb14';
};

// 获取情绪值对应的颜色和图标
export const getSentimentDisplay = (sentiment: number) => {
  if (sentiment > 50) return { color: '#52c41a', icon: <RiseOutlined /> };
  if (sentiment >= 0) return { color: '#1890ff', icon: <RiseOutlined /> };
  if (sentiment >= -50) return { color: '#faad14', icon: <FallOutlined /> };
  return { color: '#f5222d', icon: <FallOutlined /> };
};

// 热点卡片组件 - 优化版本
const HotTopicCard: React.FC<HotTopicCardProps> = ({ 
  topic, 
  size = 'default',
  onClick 
}) => {
  const sentimentDisplay = getSentimentDisplay(topic.sentiment || 0);
  
  const handleClick = () => {
    if (onClick) {
      onClick(topic);
    }
  };
  
  // 获取卡片内部内容样式和行数
  const getCardStyles = () => {
    switch(size) {
      case 'large':
        return {
          titleSize: '16px',
          summaryRows: 2,
          paragraphSize: '14px',
          tagSize: '12px'
        };
      case 'small':
        return {
          titleSize: '13px',
          summaryRows: 1,
          paragraphSize: '12px',
          tagSize: '11px'
        };
      default:
        return {
          titleSize: '14px',
          summaryRows: 1,
          paragraphSize: '13px',
          tagSize: '12px'
        };
    }
  };
  
  const styles = getCardStyles();
  
  return (
    <Card 
      className={`hot-topic-card hot-topic-card-${size}`}
      style={{ 
        marginBottom: 8,
        borderLeft: `3px solid ${getHeatColor(topic.heat)}`,
        transition: 'all 0.3s',
      }}
      hoverable
      onClick={handleClick}
      size="small"
      bodyStyle={{ padding: size === 'large' ? '12px' : '8px' }}
    >
      <div className="topic-header" style={{ marginBottom: 2 }}>
        <div className="topic-title">
          <Text strong style={{ fontSize: styles.titleSize, lineHeight: '1.4', display: 'block' }}>
            {topic.title}
          </Text>
        </div>
        <div className="topic-heat">
          <Tag color={getHeatColor(topic.heat)} style={{ fontSize: '11px', padding: '0 4px', marginLeft: '4px' }}>
            <FireOutlined /> {topic.heat}
          </Tag>
        </div>
      </div>
      
      {(size === 'default' || size === 'large') && topic.summary && (
        <Paragraph 
          ellipsis={{ rows: styles.summaryRows }}
          type="secondary"
          style={{ 
            marginTop: 4, 
            marginBottom: 4, 
            fontSize: styles.paragraphSize,
            lineHeight: '1.4'
          }}
        >
          {topic.summary}
        </Paragraph>
      )}
      
      <div className="topic-footer" style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        marginTop: 4
      }}>
        <Space size={4} wrap>
          {/* 限制显示标签数量，节省空间 */}
          {topic.tags?.slice(0, size === 'large' ? 3 : 2).map((tag: string, index: number) => (
            <Tag key={index} style={{ fontSize: styles.tagSize, padding: '0 4px', margin: '0 2px 2px 0' }}>{tag}</Tag>
          ))}
        </Space>
        
        <Space size={4}>
          {topic.timestamp && (
            <Text type="secondary" style={{ fontSize: '11px' }}>
              <ClockCircleOutlined style={{ marginRight: 2 }} />
              {topic.timestamp.split(' ')[0]}
            </Text>
          )}
          
          {topic.sentiment !== undefined && size === 'large' && (
            <Tag color={sentimentDisplay.color} style={{ fontSize: '11px', padding: '0 4px' }}>
              {sentimentDisplay.icon} {Math.abs(topic.sentiment)}
            </Tag>
          )}
        </Space>
      </div>
      
      {size === 'large' && (topic.views !== undefined || topic.comments !== undefined || topic.likes !== undefined) && (
        <div className="topic-stats" style={{ marginTop: 6, display: 'flex', gap: 12 }}>
          {topic.views !== undefined && (
            <Text type="secondary" style={{ fontSize: '11px' }}>
              <EyeOutlined style={{ marginRight: 2 }} />{topic.views}
            </Text>
          )}
          {topic.comments !== undefined && (
            <Text type="secondary" style={{ fontSize: '11px' }}>
              <MessageOutlined style={{ marginRight: 2 }} />{topic.comments}
            </Text>
          )}
          {topic.likes !== undefined && (
            <Text type="secondary" style={{ fontSize: '11px' }}>
              <HeartOutlined style={{ marginRight: 2 }} />{topic.likes}
            </Text>
          )}
        </div>
      )}
    </Card>
  );
};

export default HotTopicCard;