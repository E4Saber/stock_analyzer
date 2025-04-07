import React, { useState, useRef, useEffect } from 'react';
import { Button, Tabs, Input, List, Avatar, Typography, Badge } from 'antd';
import { SendOutlined, CommentOutlined, UserOutlined, RobotOutlined } from '@ant-design/icons';
import Draggable from 'react-draggable';
import { Resizable } from 're-resizable';

const { TextArea } = Input;
const { TabPane } = Tabs;
const { Text } = Typography;

// 简化版的聊天消息组件
const ChatMessage = ({ message }) => {
  const { content, sender, isUser, timestamp } = message;

  return (
    <div style={{ 
      display: 'flex', 
      flexDirection: isUser ? 'row-reverse' : 'row',
      marginBottom: 12 
    }}>
      <Avatar 
        icon={isUser ? <UserOutlined /> : <RobotOutlined />}
        style={{ 
          backgroundColor: isUser ? '#1890ff' : '#52c41a',
          flexShrink: 0,
          marginLeft: isUser ? 8 : 0,
          marginRight: isUser ? 0 : 8
        }}
      />
      <div>
        <div style={{
          background: isUser ? '#e6f7ff' : '#f6ffed',
          padding: '8px 12px',
          borderRadius: 6,
          maxWidth: 300,
          wordBreak: 'break-word'
        }}>
          {content}
        </div>
        <Text type="secondary" style={{ fontSize: 12, display: 'block', textAlign: isUser ? 'right' : 'left' }}>
          {sender} · {timestamp}
        </Text>
      </div>
    </div>
  );
};

// 主聊天窗口组件
const SimpleChatModal = ({ pageName = '当前页面' }) => {
  // 聊天状态
  const [visible, setVisible] = useState(false);
  const [activeTab, setActiveTab] = useState('topic');
  const [topicInput, setTopicInput] = useState('');
  const [aiInput, setAiInput] = useState('');
  const [topicMessages, setTopicMessages] = useState([
    {
      id: 1,
      content: `欢迎来到"${pageName}"讨论区！`,
      sender: '系统',
      isUser: false,
      timestamp: new Date().toLocaleTimeString()
    }
  ]);
  const [aiMessages, setAiMessages] = useState([
    {
      id: 1,
      content: '您好！我是AI助手，有什么可以帮助您的吗？',
      sender: 'AI助手',
      isUser: false,
      timestamp: new Date().toLocaleTimeString()
    }
  ]);
  const [unreadTopic, setUnreadTopic] = useState(0);
  const [unreadAI, setUnreadAI] = useState(0);
  
  // 引用和状态
  const draggleRef = useRef(null);
  const topicMessagesEndRef = useRef(null);
  const aiMessagesEndRef = useRef(null);
  const [size, setSize] = useState({ width: 360, height: 480 });

  // 聊天窗口显示/隐藏
  const toggleChat = () => {
    setVisible(!visible);
    if (!visible) {
      setUnreadTopic(0);
      setUnreadAI(0);
    }
  };
  
  // 消息自动滚动到底部
  useEffect(() => {
    if (visible && activeTab === 'topic' && topicMessagesEndRef.current) {
      topicMessagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [topicMessages, visible, activeTab]);
  
  useEffect(() => {
    if (visible && activeTab === 'ai' && aiMessagesEndRef.current) {
      aiMessagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [aiMessages, visible, activeTab]);

  // 切换标签页
  const handleTabChange = (key) => {
    setActiveTab(key);
    if (key === 'topic') {
      setUnreadTopic(0);
    } else {
      setUnreadAI(0);
    }
  };

  // 发送话题讨论消息
  const sendTopicMessage = () => {
    if (topicInput.trim()) {
      const newMessage = {
        id: Date.now(),
        content: topicInput,
        sender: '我',
        isUser: true,
        timestamp: new Date().toLocaleTimeString()
      };
      setTopicMessages([...topicMessages, newMessage]);
      setTopicInput('');
      
      // 模拟其他用户回复
      setTimeout(() => {
        const reply = {
          id: Date.now() + 1,
          content: `感谢您的分享关于"${pageName}"的观点！`,
          sender: '其他用户',
          isUser: false,
          timestamp: new Date().toLocaleTimeString()
        };
        setTopicMessages(prev => [...prev, reply]);
        if (activeTab !== 'topic') {
          setUnreadTopic(prev => prev + 1);
        }
      }, 2000);
    }
  };

  // 发送AI消息
  const sendAiMessage = () => {
    if (aiInput.trim()) {
      const newMessage = {
        id: Date.now(),
        content: aiInput,
        sender: '我',
        isUser: true,
        timestamp: new Date().toLocaleTimeString()
      };
      setAiMessages([...aiMessages, newMessage]);
      setAiInput('');
      
      // 模拟AI回复
      setTimeout(() => {
        const reply = {
          id: Date.now() + 1,
          content: `我已收到您的问题，关于"${aiInput}"，我建议您可以尝试...`,
          sender: 'AI助手',
          isUser: false,
          timestamp: new Date().toLocaleTimeString()
        };
        setAiMessages(prev => [...prev, reply]);
        if (activeTab !== 'ai') {
          setUnreadAI(prev => prev + 1);
        }
      }, 1000);
    }
  };

  // 按Enter发送消息
  const handleKeyPress = (e, chatType) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (chatType === 'topic') {
        sendTopicMessage();
      } else {
        sendAiMessage();
      }
    }
  };

  return (
    <>
      {/* 悬浮按钮 */}
      <Badge count={unreadTopic + unreadAI} offset={[-5, 5]}>
        <Button
          type="primary"
          shape="circle"
          icon={<CommentOutlined />}
          onClick={toggleChat}
          style={{
            position: 'fixed',
            bottom: '30px',
            right: '30px',
            width: '50px',
            height: '50px',
            zIndex: 999,
          }}
        />
      </Badge>

      {/* 可拖拽聊天窗口 */}
      {visible && (
        <div style={{ position: 'fixed', zIndex: 1000 }}>
          <Draggable
            handle=".chat-drag-handle"
            defaultPosition={{ x: window.innerWidth - 400, y: window.innerHeight - 550 }}
          >
            <div ref={draggleRef} style={{ position: 'absolute' }}>
              <Resizable
                size={size}
                minWidth={300}
                minHeight={400}
                onResizeStop={(e, direction, ref, d) => {
                  setSize({
                    width: size.width + d.width,
                    height: size.height + d.height,
                  });
                }}
                style={{
                  background: '#fff',
                  boxShadow: '0 3px 6px -4px rgba(0,0,0,.12), 0 6px 16px 0 rgba(0,0,0,.08)',
                  borderRadius: '8px',
                  overflow: 'hidden',
                  display: 'flex',
                  flexDirection: 'column'
                }}
              >
                {/* 拖拽标题栏 */}
                <div 
                  className="chat-drag-handle"
                  style={{
                    background: '#f0f0f0',
                    padding: '10px 16px',
                    cursor: 'move',
                    borderBottom: '1px solid #e8e8e8',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center'
                  }}
                >
                  <span>聊天窗口 - {pageName}</span>
                  <Button 
                    type="text" 
                    size="small" 
                    onClick={() => setVisible(false)}
                  >
                    关闭
                  </Button>
                </div>
                
                {/* 标签页内容 */}
                <Tabs 
                  activeKey={activeTab} 
                  onChange={handleTabChange}
                  style={{ 
                    flex: 1,
                    display: 'flex', 
                    flexDirection: 'column', 
                    height: 'calc(100% - 44px)',
                    padding: '0 8px'
                  }}
                >
                  {/* 话题讨论标签页 */}
                  <TabPane 
                    tab={
                      <Badge size="small" count={unreadTopic}>
                        <span>页面讨论</span>
                      </Badge>
                    } 
                    key="topic"
                    style={{ height: '100%', display: 'flex', flexDirection: 'column' }}
                  >
                    <div style={{ 
                      flex: 1, 
                      overflowY: 'auto', 
                      padding: '10px',
                      height: 'calc(100% - 60px)'
                    }}>
                      {topicMessages.map(msg => (
                        <ChatMessage key={msg.id} message={msg} />
                      ))}
                      <div ref={topicMessagesEndRef} />
                    </div>
                    
                    <div style={{ padding: '10px', borderTop: '1px solid #f0f0f0' }}>
                      <div style={{ display: 'flex' }}>
                        <TextArea
                          value={topicInput}
                          onChange={e => setTopicInput(e.target.value)}
                          onKeyPress={e => handleKeyPress(e, 'topic')}
                          placeholder="输入讨论内容..."
                          autoSize={{ minRows: 1, maxRows: 3 }}
                          style={{ flex: 1 }}
                        />
                        <Button 
                          type="primary" 
                          icon={<SendOutlined />} 
                          onClick={sendTopicMessage}
                          disabled={!topicInput.trim()}
                          style={{ marginLeft: 8 }}
                        />
                      </div>
                    </div>
                  </TabPane>
                  
                  {/* AI助手标签页 */}
                  <TabPane 
                    tab={
                      <Badge size="small" count={unreadAI}>
                        <span>AI助手</span>
                      </Badge>
                    } 
                    key="ai"
                    style={{ height: '100%', display: 'flex', flexDirection: 'column' }}
                  >
                    <div style={{ 
                      flex: 1, 
                      overflowY: 'auto', 
                      padding: '10px',
                      height: 'calc(100% - 60px)'
                    }}>
                      {aiMessages.map(msg => (
                        <ChatMessage key={msg.id} message={msg} />
                      ))}
                      <div ref={aiMessagesEndRef} />
                    </div>
                    
                    <div style={{ padding: '10px', borderTop: '1px solid #f0f0f0' }}>
                      <div style={{ display: 'flex' }}>
                        <TextArea
                          value={aiInput}
                          onChange={e => setAiInput(e.target.value)}
                          onKeyPress={e => handleKeyPress(e, 'ai')}
                          placeholder="向AI助手提问..."
                          autoSize={{ minRows: 1, maxRows: 3 }}
                          style={{ flex: 1 }}
                        />
                        <Button 
                          type="primary" 
                          icon={<SendOutlined />} 
                          onClick={sendAiMessage}
                          disabled={!aiInput.trim()}
                          style={{ marginLeft: 8 }}
                        />
                      </div>
                    </div>
                  </TabPane>
                </Tabs>
              </Resizable>
            </div>
          </Draggable>
        </div>
      )}
    </>
  );
};

export default SimpleChatModal;