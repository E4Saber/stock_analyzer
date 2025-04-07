import React from 'react';
import { Layout, Menu, Typography } from 'antd';
import SimpleChatModal from './SimpleChatModal';

const { Header, Content, Sider } = Layout;
const { Title, Paragraph } = Typography;

// 示例页面
const ExamplePage = () => {
  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ background: '#fff', padding: '0 20px' }}>
        <div style={{ display: 'flex', alignItems: 'center', height: '100%' }}>
          <div style={{ color: '#1890ff', fontWeight: 'bold', fontSize: '18px' }}>
            示例应用
          </div>
        </div>
      </Header>
      
      <Layout>
        <Sider width={200} style={{ background: '#fff' }}>
          <Menu
            mode="inline"
            defaultSelectedKeys={['dashboard']}
            style={{ height: '100%', borderRight: 0 }}
          >
            <Menu.Item key="dashboard">首页</Menu.Item>
            <Menu.Item key="analytics">数据分析</Menu.Item>
            <Menu.Item key="settings">设置</Menu.Item>
          </Menu>
        </Sider>
        
        <Content style={{ padding: '24px', background: '#fff' }}>
          <Title level={2}>数据分析页面</Title>
          
          <Paragraph>
            这是数据分析页面的内容。您可以在这个页面上查看各种数据分析结果和图表。
          </Paragraph>
          
          <div style={{ 
            border: '1px solid #eee',
            padding: '20px',
            borderRadius: '4px',
            marginBottom: '20px'
          }}>
            <Title level={4}>月度销售报告</Title>
            <div style={{ 
              height: '200px', 
              background: '#f5f5f5', 
              display: 'flex', 
              justifyContent: 'center', 
              alignItems: 'center' 
            }}>
              [这里是销售图表]
            </div>
          </div>
          
          <div style={{ 
            border: '1px solid #eee',
            padding: '20px',
            borderRadius: '4px'
          }}>
            <Title level={4}>用户增长统计</Title>
            <div style={{ 
              height: '200px', 
              background: '#f5f5f5', 
              display: 'flex', 
              justifyContent: 'center', 
              alignItems: 'center' 
            }}>
              [这里是用户增长图表]
            </div>
          </div>
          
          {/* 聊天模态窗口组件 */}
          <SimpleChatModal pageName="数据分析" />
        </Content>
      </Layout>
    </Layout>
  );
};

export default ExamplePage;

// ==========================================================
// 在非React应用中挂载聊天组件的示例
// ==========================================================

// 创建一个独立的函数来挂载聊天组件
import { createRoot } from 'react-dom/client';

export const mountChatModal = (containerId, pageName) => {
  const container = document.getElementById(containerId) || document.createElement('div');
  
  if (!document.getElementById(containerId)) {
    container.id = containerId;
    document.body.appendChild(container);
  }
  
  const root = createRoot(container);
  root.render(<SimpleChatModal pageName={pageName} />);
  
  return {
    unmount: () => {
      root.unmount();
      if (document.getElementById(containerId)) {
        document.body.removeChild(container);
      }
    }
  };
};

// 使用示例 - 可以放在任何JS文件中
// document.addEventListener('DOMContentLoaded', () => {
//   const pageName = document.title || '未命名页面';
//   mountChatModal('chat-container', pageName);
// });