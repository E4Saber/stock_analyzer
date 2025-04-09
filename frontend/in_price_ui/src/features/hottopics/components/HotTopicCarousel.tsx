import React from 'react';
import { Card, Carousel, Button, Tag, Space, Typography } from 'antd';
import { ThunderboltOutlined, FireOutlined } from '@ant-design/icons';
import { HotTopicItem, getHeatColor } from './HotTopicCard';

const { Title, Paragraph } = Typography;

// 获取影响力对应的标签颜色
export const getImpactColor = (impact: string) => {
  if (impact === 'high') return '#f5222d';
  if (impact === 'medium') return '#fa8c16';
  return '#52c41a';
};

interface HotTopicCarouselProps {
  topics: HotTopicItem[];
  onViewDetail?: (topicId: string) => void;
}

// 热点轮播组件 - 优化版本
const HotTopicCarousel: React.FC<HotTopicCarouselProps> = ({ topics, onViewDetail }) => {
  const handleViewDetail = (topicId: string) => {
    if (onViewDetail) {
      onViewDetail(topicId);
    }
  };

  return (
    <Card 
      className="hot-carousel-card"
      title={
        <Space size="small">
          <ThunderboltOutlined style={{ color: '#f5222d' }} />
          <span>头条热点</span>
        </Space>
      }
      size="small"
      bodyStyle={{ padding: '10px' }}
      style={{ marginBottom: 12 }}
    >
      <Carousel autoplay style={{ height: 180 }}>
        {topics.slice(0, 4).map((topic, index) => (
          <div key={index}>
            <div style={{ padding: '0 8px' }}>
              <div style={{ marginBottom: 8 }}>
                <Title level={4} style={{ marginBottom: 6, fontSize: '16px' }}>{topic.title}</Title>
                <Paragraph 
                  ellipsis={{ rows: 2 }} 
                  style={{ fontSize: '13px', lineHeight: '1.5', marginBottom: 8 }}
                >
                  {topic.summary}
                </Paragraph>
              </div>
              
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Space size={4}>
                  {topic.tags?.slice(0, 3).map((tag: string, i: number) => (
                    <Tag key={i} style={{ margin: '0 2px 2px 0', fontSize: '11px', padding: '0 4px' }}>{tag}</Tag>
                  ))}
                  
                  {topic.impact && (
                    <Tag color={getImpactColor(topic.impact)} style={{ fontSize: '11px', padding: '0 4px' }}>
                      {topic.impact === 'high' ? '高' : topic.impact === 'medium' ? '中' : '低'}
                    </Tag>
                  )}
                </Space>
                
                <Space size={4}>
                  <Tag color={getHeatColor(topic.heat)} style={{ fontSize: '11px', padding: '0 4px' }}>
                    <FireOutlined /> {topic.heat}
                  </Tag>
                  <Button 
                    type="primary" 
                    size="small"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleViewDetail(topic.id);
                    }}
                    style={{ height: '24px', fontSize: '12px', padding: '0 8px' }}
                  >
                    详情
                  </Button>
                </Space>
              </div>
            </div>
          </div>
        ))}
      </Carousel>
    </Card>
  );
};

export default HotTopicCarousel;