import React from 'react';
import { Card, List, Typography, Space, Button, Avatar, Tag } from 'antd';
import { UserOutlined, LikeOutlined, MessageOutlined } from '@ant-design/icons';

const { Text } = Typography;

export interface ExpertOpinionItem {
  id: string;
  avatar?: string;
  name: string;
  title: string;
  content: string;
  date?: string;
  expertise?: string;
  likes?: number;
  comments?: number;
}

interface ExpertOpinionsProps {
  opinions: ExpertOpinionItem[];
  title?: string;
  showMore?: boolean;
  onViewMore?: () => void;
  onViewOpinion?: (id: string) => void;
  className?: string;
}

// 专家观点组件 - 优化版本
const ExpertOpinions: React.FC<ExpertOpinionsProps> = ({ 
  opinions, 
  title = '专家观点',
  showMore = true,
  onViewMore,
  onViewOpinion,
  className
}) => {
  const handleViewOpinion = (id: string) => {
    if (onViewOpinion) {
      onViewOpinion(id);
    }
  };
  
  return (
    <Card 
      title={
        <Space size="small">
          <UserOutlined style={{ color: '#1890ff' }} />
          <span>{title}</span>
        </Space>
      }
      className={className}
      size="small"
      bodyStyle={{ padding: '8px' }}
    >
      <List
        itemLayout="horizontal"
        dataSource={opinions}
        size="small"
        split={false}
        renderItem={(item) => (
          <List.Item
            style={{ padding: '4px 0' }}
            actions={[
              item.likes !== undefined && (
                <Space size={2}>
                  <LikeOutlined style={{ fontSize: '11px' }} />
                  <Text type="secondary" style={{ fontSize: '11px' }}>{item.likes}</Text>
                </Space>
              ),
              item.comments !== undefined && (
                <Space size={2}>
                  <MessageOutlined style={{ fontSize: '11px' }} />
                  <Text type="secondary" style={{ fontSize: '11px' }}>{item.comments}</Text>
                </Space>
              )
            ].filter(Boolean)}
          >
            <List.Item.Meta
              avatar={
                <Avatar src={item.avatar || null} size="small">
                  {!item.avatar && <UserOutlined />}
                </Avatar>
              }
              title={
                <div style={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: '4px' }}>
                  <a 
                    href="#" 
                    onClick={(e) => {
                      e.preventDefault();
                      handleViewOpinion(item.id);
                    }}
                    style={{ fontSize: '13px', fontWeight: 'bold' }}
                  >
                    {item.title}
                  </a>
                  {item.expertise && (
                    <Tag color="blue" style={{ fontSize: '10px', padding: '0 4px', margin: 0 }}>{item.expertise}</Tag>
                  )}
                </div>
              }
              description={
                <div>
                  <Space style={{ marginBottom: 2 }} size={4}>
                    <Text type="secondary" style={{ fontSize: '11px' }}>{item.name}</Text>
                    {item.date && <Text type="secondary" style={{ fontSize: '11px' }}>{item.date}</Text>}
                  </Space>
                  <div>
                    <Text ellipsis={{ rows: 2 }} style={{ fontSize: '12px', lineHeight: '1.4' }}>
                      {item.content}
                    </Text>
                  </div>
                </div>
              }
            />
          </List.Item>
        )}
      />
      
      {showMore && (
        <div style={{ textAlign: 'center', marginTop: 8 }}>
          <Button 
            type="link" 
            onClick={onViewMore}
            size="small"
            style={{ fontSize: '12px', padding: '0 4px', height: '22px' }}
          >
            查看更多观点
          </Button>
        </div>
      )}
    </Card>
  );
};

export default ExpertOpinions;