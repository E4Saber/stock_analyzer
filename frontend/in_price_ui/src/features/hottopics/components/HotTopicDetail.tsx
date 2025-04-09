import React from 'react';
import { Modal, Card, Typography, Space, Tag, Divider, Row, Col, Button, Statistic } from 'antd';
import { 
  FireOutlined, 
  RiseOutlined, 
  FallOutlined, 
  ClockCircleOutlined,
  ShareAltOutlined,
  BellOutlined,
  BarChartOutlined,
  LinkOutlined,
  EyeOutlined,
  HeartOutlined,
  MessageOutlined
} from '@ant-design/icons';
import { HotTopicItem, getHeatColor, getSentimentDisplay } from './HotTopicCard';

const { Title, Paragraph, Text } = Typography;

interface HotTopicDetailProps {
  topic: HotTopicItem | null;
  visible: boolean;
  onClose: () => void;
}

// 热点详情模态框组件 - 优化版本
const HotTopicDetail: React.FC<HotTopicDetailProps> = ({ 
  topic, 
  visible, 
  onClose 
}) => {
  if (!topic) return null;
  
  const sentimentDisplay = getSentimentDisplay(topic.sentiment || 0);
  
  return (
    <Modal
      title={
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Tag color={getHeatColor(topic.heat)} style={{ marginRight: 8, fontSize: '12px' }}>
            <FireOutlined /> 热度 {topic.heat}
          </Tag>
          <span style={{ fontSize: '14px' }}>热点详情</span>
        </div>
      }
      open={visible}
      onCancel={onClose}
      width={700}
      footer={[
        <Button key="subscribe" icon={<BellOutlined />} size="small">
          订阅
        </Button>,
        <Button key="share" icon={<ShareAltOutlined />} size="small">
          分享
        </Button>,
        <Button key="close" onClick={onClose} size="small">
          关闭
        </Button>
      ]}
      bodyStyle={{ padding: '16px' }}
    >
      <div className="hot-topic-detail">
        <Title level={4} style={{ fontSize: '18px', marginBottom: '8px' }}>{topic.title}</Title>
        
        <Space style={{ marginBottom: 12 }} size={8}>
          <Text type="secondary" style={{ fontSize: '12px' }}>
            <ClockCircleOutlined style={{ marginRight: 4 }} />
            {topic.timestamp}
          </Text>
          
          {topic.category && (
            <Tag color="blue" style={{ fontSize: '12px' }}>
              {topic.category === 'policy' ? '政策动向' : 
               topic.category === 'market' ? '市场波动' : 
               topic.category === 'company' ? '公司热点' : 
               topic.category === 'data' ? '经济数据' : topic.category}
            </Tag>
          )}
          
          {topic.impact && (
            <Tag color={topic.impact === 'high' ? '#f5222d' : topic.impact === 'medium' ? '#fa8c16' : '#52c41a'} style={{ fontSize: '12px' }}>
              影响程度: {topic.impact === 'high' ? '高' : topic.impact === 'medium' ? '中' : '低'}
            </Tag>
          )}
        </Space>
        
        <Divider style={{ margin: '8px 0' }} />
        
        <Paragraph style={{ fontSize: '14px', lineHeight: '1.6' }}>
          {topic.summary}
        </Paragraph>
        
        <Row gutter={[12, 12]} style={{ marginTop: 16, marginBottom: 16 }}>
          <Col span={8}>
            <Card size="small" bodyStyle={{ padding: '8px' }}>
              <Statistic
                title={<Text style={{ fontSize: '12px' }}>市场情绪</Text>}
                value={Math.abs(topic.sentiment || 0)}
                precision={0}
                valueStyle={{ color: sentimentDisplay.color, fontSize: '18px' }}
                prefix={sentimentDisplay.icon}
                suffix={<Text style={{ fontSize: '12px' }}>{topic.sentiment && topic.sentiment > 0 ? '乐观' : '悲观'}</Text>}
              />
            </Card>
          </Col>
          
          <Col span={8}>
            <Card size="small" bodyStyle={{ padding: '8px' }}>
              <Statistic
                title={<Text style={{ fontSize: '12px' }}>阅读量</Text>}
                value={topic.views || 0}
                valueStyle={{ color: '#1890ff', fontSize: '18px' }}
                prefix={<EyeOutlined />}
              />
            </Card>
          </Col>
          
          <Col span={8}>
            <Card size="small" bodyStyle={{ padding: '8px' }}>
              <Statistic
                title={<Text style={{ fontSize: '12px' }}>讨论量</Text>}
                value={topic.comments || 0}
                valueStyle={{ color: '#722ed1', fontSize: '18px' }}
                prefix={<MessageOutlined />}
              />
            </Card>
          </Col>
        </Row>
        
        {topic.tags && topic.tags.length > 0 && (
          <div style={{ marginBottom: 12 }}>
            <Title level={5} style={{ fontSize: '14px', marginBottom: '4px' }}>相关标签</Title>
            <div>
              {topic.tags.map((tag, index) => (
                <Tag key={index} style={{ margin: '2px', fontSize: '12px' }}>{tag}</Tag>
              ))}
            </div>
          </div>
        )}
        
        {topic.relatedAssets && topic.relatedAssets.length > 0 && (
          <div style={{ marginBottom: 12 }}>
            <Title level={5} style={{ fontSize: '14px', marginBottom: '4px' }}>相关资产</Title>
            <div>
              {topic.relatedAssets.map((asset, index) => (
                <Tag color="green" key={index} style={{ margin: '2px', fontSize: '12px' }}>
                  <LinkOutlined style={{ marginRight: 4 }} />
                  {asset}
                </Tag>
              ))}
            </div>
          </div>
        )}
        
        <Divider style={{ margin: '12px 0' }} />
        
        <Space style={{ marginTop: 16 }} size={8}>
          <Button icon={<BarChartOutlined />} size="small">
            查看分析报告
          </Button>
          <Button icon={<MessageOutlined />} size="small">
            查看讨论
          </Button>
          <Button icon={<HeartOutlined />} size="small">
            收藏
          </Button>
        </Space>
      </div>
    </Modal>
  );
};

export default HotTopicDetail;