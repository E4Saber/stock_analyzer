// src/components/widgets/AIAssistantTrigger.tsx
import React, { useState, useEffect } from 'react';
import { Button, Badge, Tooltip } from 'antd';
import { RobotOutlined } from '@ant-design/icons';
import AIAssistantFloat from './AIAssistantFloat';
import { StockData } from '../../types/market';

interface AIAssistantTriggerProps {
  currentStock?: StockData;
  position?: 'top-right' | 'bottom-right' | 'bottom-left' | 'top-left';
}

/**
 * AI助手触发按钮，控制悬浮窗的显示与隐藏
 */
const AIAssistantTrigger: React.FC<AIAssistantTriggerProps> = ({
  currentStock,
  position = 'bottom-right'
}) => {
  // 状态
  const [visible, setVisible] = useState<boolean>(false);
  const [minimized, setMinimized] = useState<boolean>(false);
  
  // 根据位置计算样式
  const getPositionStyle = (): React.CSSProperties => {
    switch (position) {
      case 'top-right':
        return { top: '20px', right: '20px' };
      case 'bottom-left':
        return { bottom: '20px', left: '20px' };
      case 'top-left':
        return { top: '20px', left: '20px' };
      case 'bottom-right':
      default:
        return { bottom: '20px', right: '20px' };
    }
  };
  
  // 当股票变更时，如果悬浮窗可见，则将其打开（如果之前是最小化状态）
  useEffect(() => {
    if (currentStock && visible && minimized) {
      setMinimized(false);
    }
  }, [currentStock]);
  
  // 处理显示/隐藏
  const toggleVisibility = () => {
    setVisible(!visible);
    if (!visible) {
      setMinimized(false); // 显示时恢复完整窗口
    }
  };
  
  // 处理最小化
  const handleMinimize = () => {
    setMinimized(true);
  };
  
  // 处理关闭
  const handleClose = () => {
    setVisible(false);
  };
  
  // 位置样式
  const positionStyle = getPositionStyle();
  
  return (
    <>
      {/* 触发按钮 */}
      <div 
        style={{ 
          position: 'fixed',
          zIndex: 999,
          ...positionStyle
        }}
      >
        <Tooltip title="AI分析助手" placement="left">
          <Badge dot={currentStock !== undefined}>
            <Button
              type="primary"
              shape="circle"
              icon={<RobotOutlined />}
              onClick={toggleVisibility}
              size="large"
              style={{ 
                boxShadow: '0 2px 8px rgba(0, 0, 0, 0.15)',
                width: '48px',
                height: '48px'
              }}
            />
          </Badge>
        </Tooltip>
      </div>
      
      {/* AI分析悬浮窗 */}
      <AIAssistantFloat
        currentStock={currentStock}
        visible={visible}
        onClose={handleClose}
        onMinimize={handleMinimize}
      />
    </>
  );
};

export default AIAssistantTrigger;