import React from 'react';
import { Card, Timeline, Tag, Space, Typography } from 'antd';
import { ClockCircleOutlined, FireOutlined } from '@ant-design/icons';
import { HotTopicItem, getHeatColor } from './HotTopicCard';

import './HotTopicTimeline.css';


const { Text } = Typography;

interface HotTopicTimelineProps {
  topics: HotTopicItem[];
  limit?: number;
  onClickTopic?: (topic: HotTopicItem) => void;
}

// 热点时间轴组件 - 修复右侧重叠问题
const HotTopicTimeline: React.FC<HotTopicTimelineProps> = ({ 
  topics, 
  limit = 5,
  onClickTopic 
}) => {
  // 按日期先后顺序排序
  const sortedTopics = [...topics].sort((a, b) => 
    new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
  );
  
  const handleTopicClick = (topic: HotTopicItem) => {
    if (onClickTopic) {
      onClickTopic(topic);
    }
  };
  
  return (
    <Card 
      title={
        <Space size="small">
          <ClockCircleOutlined style={{ color: '#722ed1' }} />
          <span>热点时间轴</span>
        </Space>
      }
      className="timeline-card"
      size="small"
      bodyStyle={{ padding: '8px', overflowX: 'hidden' }}
    >
      {/* 自定义时间轴，不使用默认的左侧标签功能 */}
      <div style={{ position: 'relative', paddingRight: '40px' }}>
        {/* 垂直线 */}
        <div 
          style={{ 
            position: 'absolute', 
            right: '20px', 
            top: '0', 
            bottom: '0', 
            width: '1px', 
            backgroundColor: '#f0f0f0',
            zIndex: 1
          }} 
        />
        
        {/* 时间轴项目 */}
        {sortedTopics.slice(0, limit).map((topic, index) => (
          <div 
            key={index} 
            style={{ 
              position: 'relative', 
              marginBottom: '16px',
              paddingRight: '30px'
            }}
          >
            {/* 右侧圆点 */}
            <div 
              style={{ 
                position: 'absolute', 
                right: '-20px', 
                top: '10px', 
                width: '10px', 
                height: '10px', 
                borderRadius: '50%', 
                backgroundColor: getHeatColor(topic.heat),
                zIndex: 2
              }} 
            />
            
            {/* 右侧热度标签 */}
            <div 
              style={{ 
                position: 'absolute', 
                right: '-35px', 
                top: '8px', 
                zIndex: 2
              }}
            >
              <Tag 
                color={getHeatColor(topic.heat)} 
                style={{ 
                  fontSize: '11px', 
                  padding: '0 4px', 
                  minWidth: '30px', 
                  textAlign: 'center',
                  marginRight: 0
                }}
              >
                {topic.heat}
              </Tag>
            </div>
            
            {/* 内容卡片 */}
            <div 
              style={{ 
                backgroundColor: '#f9f9f9', 
                padding: '8px', 
                borderRadius: '4px',
                cursor: 'pointer',
                transition: 'background-color 0.3s',
                marginRight: '10px' // 为右侧的圆点和热度标签留出空间
              }}
              onClick={() => handleTopicClick(topic)}
              onMouseOver={(e) => (e.currentTarget.style.backgroundColor = '#f0f0f0')}
              onMouseOut={(e) => (e.currentTarget.style.backgroundColor = '#f9f9f9')}
            >
              {/* 时间戳 */}
              <div style={{ marginBottom: '4px' }}>
                <Text type="secondary" style={{ fontSize: '11px' }}>
                  <ClockCircleOutlined style={{ marginRight: 4 }} />
                  {topic.timestamp.split(' ')[0]}
                </Text>
              </div>
              
              {/* 标题 */}
              <Text strong style={{ fontSize: '13px', lineHeight: 1.4, display: 'block' }}>
                {/* 限制标题长度 */}
                {topic.title.length > 24 ? `${topic.title.substring(0, 24)}...` : topic.title}
              </Text>
              
              {/* 标签 */}
              <div style={{ marginTop: '4px' }}>
                <Space size={4} wrap>
                  {/* 只显示前两个标签，节省空间 */}
                  {topic.tags?.slice(0, 2).map((tag: string, i: number) => (
                    <Tag key={i} style={{ fontSize: '11px', padding: '0 4px', margin: '0 2px 2px 0' }}>{tag}</Tag>
                  ))}
                </Space>
              </div>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
};

export default HotTopicTimeline;