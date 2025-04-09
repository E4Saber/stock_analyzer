import React, { useEffect } from 'react';
import { Modal, Button, Typography, Divider } from 'antd';
import { InfoCircleOutlined, RiseOutlined, FallOutlined } from '@ant-design/icons';
import './NewsDetailModal.css';

const { Title, Paragraph, Text } = Typography;

// 详细消息类型定义
export interface NewsDetail {
  time: string;
  title: string;
  content: string;
  change?: number; // 涨跌幅
  impact?: 'positive' | 'negative' | 'neutral'; // 影响
  relatedStocks?: Array<{code: string; name: string; change: number}>;
  source?: string; // 消息来源
}

interface NewsDetailModalProps {
  visible: boolean;
  newsDetail: NewsDetail | null;
  onClose: () => void;
}

const NewsDetailModal: React.FC<NewsDetailModalProps> = ({ 
  visible, 
  newsDetail, 
  onClose 
}) => {
  // 控制背景滚动
  useEffect(() => {
    if (visible) {
      // 当Modal打开时，禁止背景滚动
      document.body.classList.add('modal-open');
    } else {
      // 当Modal关闭时，恢复背景滚动
      document.body.classList.remove('modal-open');
    }
    
    // 组件卸载时清理
    return () => {
      document.body.classList.remove('modal-open');
    };
  }, [visible]);

  // 渲染股票变化的颜色和图标
  const renderChangeValue = (value: number) => {
    if (value > 0) {
      return (
        <Text type="success" strong>
          <RiseOutlined /> +{value}%
        </Text>
      );
    } else if (value < 0) {
      return (
        <Text type="danger" strong>
          <FallOutlined /> {value}%
        </Text>
      );
    } else {
      return <Text>0.00%</Text>;
    }
  };

  return (
    <Modal
      title={
        <div className="news-modal-title">
          <InfoCircleOutlined style={{ marginRight: '8px' }} />
          市场快讯
        </div>
      }
      open={visible}
      onCancel={onClose}
      footer={[
        <Button key="close" onClick={onClose} size="small">
          关闭
        </Button>
      ]}
      className="news-detail-modal"
      maskClosable={true}
      destroyOnClose={true}
    >
      {newsDetail && (
        <div className="news-detail-content">
          <div className="news-headline">
            <div className="news-time">{newsDetail.time}</div>
            <Title level={4}>{newsDetail.title}</Title>
          </div>
          
          <div className="news-change-indicator">
            <div className={`impact-indicator impact-${newsDetail.impact}`}>
              {newsDetail.impact === 'positive' ? '利好' : (newsDetail.impact === 'negative' ? '利空' : '中性')}
            </div>
            <div className="market-change">
              大盘影响: {renderChangeValue(newsDetail.change || 0)}
            </div>
          </div>
          
          <Divider />
          
          <div className="news-content">
            <Paragraph>{newsDetail.content}</Paragraph>
            <div className="news-source">来源: {newsDetail.source}</div>
          </div>
          
          {newsDetail.relatedStocks && newsDetail.relatedStocks.length > 0 && (
            <>
              <Divider orientation="left">相关标的</Divider>
              <div className="related-stocks">
                {newsDetail.relatedStocks.map((stock, index) => (
                  <div key={index} className="stock-item">
                    <div className="stock-name-code">
                      <span className="stock-name">{stock.name}</span>
                      <span className="stock-code">{stock.code}</span>
                    </div>
                    <div className="stock-change">
                      {renderChangeValue(stock.change)}
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      )}
    </Modal>
  );
};

export default NewsDetailModal;