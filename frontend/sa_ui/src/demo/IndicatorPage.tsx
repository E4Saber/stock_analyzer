// src/pages/EconomicMonitor/IndicatorPage.tsx
import React, { useState } from 'react';
import { Card, Tabs, Breadcrumb, Typography, Row, Col, Statistic, Divider } from 'antd';
import { ArrowUpOutlined, ArrowDownOutlined, HomeOutlined } from '@ant-design/icons';
import { Link } from 'react-router-dom';
import IndicatorChartContainer from './IndicatorChartContainer';
import { IndicatorType } from './indicatorApi';

const { Title, Paragraph } = Typography;
const { TabPane } = Tabs;

const IndicatorPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<IndicatorType>('cpi');
  
  const handleTabChange = (key: string) => {
    setActiveTab(key as IndicatorType);
  };
  
  return (
    <div className="indicator-page">
      {/* 面包屑导航 */}
      <Breadcrumb style={{ marginBottom: '16px' }}>
        <Breadcrumb.Item>
          <Link to="/"><HomeOutlined /> 首页</Link>
        </Breadcrumb.Item>
        <Breadcrumb.Item>
          <Link to="/economic-monitor">宏观经济监测</Link>
        </Breadcrumb.Item>
        <Breadcrumb.Item>经济指标分析</Breadcrumb.Item>
      </Breadcrumb>
      
      {/* 页面标题和说明 */}
      <Title level={2}>宏观经济指标分析</Title>
      <Paragraph>
        本页面提供了中国主要宏观经济指标的可视化分析，包括CPI、GDP、货币供应量和PMI等关键指标的历史走势和对比分析。
      </Paragraph>
      
      {/* 指标选项卡 */}
      <Tabs activeKey={activeTab} onChange={handleTabChange} type="card">
        <TabPane tab="消费者价格指数(CPI)" key="cpi">
          <Card bordered={false}>
            <IndicatorChartContainer 
              indicatorType="cpi"
              height={500}
            />
          </Card>
        </TabPane>
        
        <TabPane tab="国内生产总值(GDP)" key="gdp">
          <Card bordered={false}>
            <IndicatorChartContainer 
              indicatorType="gdp"
              height={500}
            />
          </Card>
        </TabPane>
        
        <TabPane tab="货币供应量" key="m">
          <Card bordered={false}>
            <IndicatorChartContainer 
              indicatorType="m"
              height={500}
            />
          </Card>
        </TabPane>
        
        <TabPane tab="采购经理人指数(PMI)" key="pmi">
          <Card bordered={false}>
            <IndicatorChartContainer 
              indicatorType="pmi"
              height={500}
            />
          </Card>
        </TabPane>
      </Tabs>
      
      <Divider />
      
      {/* 使用说明 */}
      <Card title="使用指南" style={{ marginTop: '20px' }}>
        <Row gutter={[16, 16]}>
          <Col span={24}>
            <Paragraph>
              <strong>指标切换：</strong>通过上方选项卡可以在不同的宏观经济指标之间切换。
            </Paragraph>
            <Paragraph>
              <strong>数据系列：</strong>使用"选择数据系列"下拉菜单可以选择要显示的具体数据系列。
            </Paragraph>
            <Paragraph>
              <strong>时间筛选：</strong>使用"按年份筛选"可以查看特定年份的数据，或选择"全部"查看完整历史数据。
            </Paragraph>
            <Paragraph>
              <strong>视图模式：</strong>右上角的按钮可以切换不同的数据视图模式（实际值、同比、环比）。
            </Paragraph>
            <Paragraph>
              <strong>图表交互：</strong>可以通过下方的缩放控制器放大查看特定时间段，鼠标悬停可查看详细数据。
            </Paragraph>
          </Col>
        </Row>
      </Card>
    </div>
  );
};

// 通过URL参数指定初始选择的指标
const ParameterizedIndicatorPage: React.FC = () => {
  // 从URL获取指标类型，例如 /indicators?type=cpi
  const urlParams = new URLSearchParams(window.location.search);
  const indicatorType = urlParams.get('type') as IndicatorType || 'cpi';
  
  return (
    <div className="single-indicator-page">
      <Card bordered={false}>
        <IndicatorChartContainer 
          indicatorType={indicatorType}
          height={600}
        />
      </Card>
    </div>
  );
};

export { IndicatorPage, ParameterizedIndicatorPage };