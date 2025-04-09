import React, { useState } from 'react';
import { Typography, Card, Row, Col, Tabs, Statistic, Divider, List, Tag, Space, Button } from 'antd';
import { 
  ArrowUpOutlined, 
  ArrowDownOutlined, 
  LineChartOutlined, 
  InfoCircleOutlined, 
  GlobalOutlined,
  CalendarOutlined,
  BarChartOutlined,
  DollarOutlined,
  ShareAltOutlined
} from '@ant-design/icons';
import MacroChart from '../components/MacroEconomyChart';
import MacroEconomyNewsModal from '../components/MacroEconomyNewsModal';

// 导入CSS样式
import './MacroEconomyPage.css';

const { Title, Paragraph } = Typography;
const { TabPane } = Tabs;

// 定义各国宏观经济指标数据
const macroData = {
  china: {
    indicators: [
      { name: 'CPI同比', value: 2.3, change: 0.2, up: true },
      { name: 'PPI同比', value: -1.5, change: 0.5, up: false },
      { name: 'GDP增速', value: 5.7, change: 0.1, up: true },
      { name: '国家制造业PMI', value: 51.2, change: 0.8, up: true },
      { name: '城镇失业率', value: 5.1, change: 0.1, up: false },
      { name: '社会消费品零售总额同比', value: 3.9, change: 0.7, up: true },
    ],
    news: [
      { title: '央行下调存款准备金率0.5个百分点，释放长期资金约1万亿元', date: '2024-09-20', category: '金融政策', tag: 'policy' },
      { title: '8月工业增加值同比增长5.8%，高于市场预期', date: '2024-09-15', category: '经济数据', tag: 'data' },
      { title: '国家统计局：前三季度GDP同比增长5.7%，经济持续恢复向好', date: '2024-09-10', category: '经济数据', tag: 'data' },
      { title: '发改委：将加大基础设施投资力度，推动经济稳步增长', date: '2024-09-05', category: '政策动向', tag: 'policy' },
    ],
    updateTime: '2024-09-25 10:30'
  },
  usa: {
    indicators: [
      { name: 'CPI同比', value: 3.2, change: 0.1, up: false },
      { name: 'PPI同比', value: 2.1, change: 0.3, up: true },
      { name: 'GDP增速', value: 2.5, change: 0.2, up: true },
      { name: '制造业PMI', value: 49.7, change: 0.5, up: false },
      { name: '失业率', value: 3.9, change: 0.1, up: true },
      { name: '零售销售月环比', value: 0.7, change: 0.3, up: true },
    ],
    news: [
      { title: '美联储维持利率不变，暗示年内可能还有一次降息', date: '2024-09-18', category: '货币政策', tag: 'policy' },
      { title: '8月非农就业人数增加17万，低于预期', date: '2024-09-06', category: '就业数据', tag: 'data' },
      { title: '美国8月CPI同比上涨3.2%，通胀压力仍存', date: '2024-09-12', category: '经济数据', tag: 'data' },
      { title: '美国第二季度GDP终值上修至2.5%，高于初值', date: '2024-08-29', category: '经济数据', tag: 'data' },
    ],
    updateTime: '2024-09-24 16:45'
  },
  europe: {
    indicators: [
      { name: '欧元区CPI同比', value: 2.6, change: 0.2, up: true },
      { name: '欧元区PPI同比', value: 1.2, change: 0.4, up: false },
      { name: '欧元区GDP增速', value: 0.9, change: 0.1, up: true },
      { name: '欧元区综合PMI', value: 48.9, change: 0.3, up: false },
      { name: '欧元区失业率', value: 6.4, change: 0.1, up: false },
      { name: '欧元区零售销售同比', value: -0.5, change: 0.3, up: false },
    ],
    news: [
      { title: '欧洲央行宣布降息25个基点，为今年第二次降息', date: '2024-09-12', category: '货币政策', tag: 'policy' },
      { title: '欧元区8月综合PMI继续处于收缩区间，制造业疲软', date: '2024-09-03', category: '经济指标', tag: 'data' },
      { title: '欧盟通过2500亿欧元绿色转型投资计划', date: '2024-08-31', category: '政策动向', tag: 'policy' },
      { title: '欧盟对中国电动汽车加征临时关税，中欧贸易摩擦加剧', date: '2024-09-08', category: '国际贸易', tag: 'trade' },
    ],
    updateTime: '2024-09-22 09:15'
  },
  japan: {
    indicators: [
      { name: 'CPI同比', value: 2.8, change: 0.3, up: true },
      { name: 'PPI同比', value: 2.5, change: 0.2, up: true },
      { name: 'GDP增速', value: 1.2, change: 0.4, up: true },
      { name: '制造业PMI', value: 49.2, change: 0.6, up: false },
      { name: '失业率', value: 2.5, change: 0.1, up: false },
      { name: '零售销售同比', value: 2.1, change: 0.5, up: true },
    ],
    news: [
      { title: '日本央行维持负利率政策不变，强调通胀稳定的重要性', date: '2024-09-19', category: '货币政策', tag: 'policy' },
      { title: '日本二季度GDP环比增长0.8%，好于市场预期', date: '2024-08-15', category: '经济数据', tag: 'data' },
      { title: '日本8月出口同比增长5.3%，对美出口增长显著', date: '2024-09-21', category: '对外贸易', tag: 'trade' },
      { title: '日本政府公布经济振兴新计划，将推出5万亿日元财政刺激', date: '2024-09-05', category: '经济政策', tag: 'policy' },
    ],
    updateTime: '2024-09-23 14:20'
  }
};

// 获取标签类型的颜色类名
const getTagClassName = (tag: string) => {
  switch (tag) {
    case 'policy':
      return 'news-tag-policy';
    case 'data':
      return 'news-tag-data';
    case 'trade':
      return 'news-tag-trade';
    default:
      return '';
  }
};

const MacroEconomyPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState('china');
  // 状态控制新闻模态框的显示
  const [newsModalVisible, setNewsModalVisible] = useState(false);
  
  const handleTabChange = (key: string) => {
    setActiveTab(key);
  };

  // 打开新闻模态框
  const openNewsModal = () => {
    setNewsModalVisible(true);
  };

  // 关闭新闻模态框
  const closeNewsModal = () => {
    setNewsModalVisible(false);
  };

  // 获取当前选中国家的名称
  const getCountryName = () => {
    switch (activeTab) {
      case 'china':
        return '中国';
      case 'usa':
        return '美国';
      case 'europe':
        return '欧洲';
      case 'japan':
        return '日本';
      default:
        return '中国';
    }
  };

  // 渲染指标卡片
  const renderIndicatorCards = (countryData: any) => {
    return (
      <Row gutter={[16, 16]} className="indicator-row">
        {countryData.indicators.map((indicator: any, index: number) => (
          <Col xs={24} sm={12} md={8} lg={8} xl={4} key={index}>
            <Card 
              size="small" 
              title={indicator.name} 
              bordered
              className="macro-indicator-card"
            >
              <Statistic
                value={indicator.value}
                precision={1}
                valueStyle={{ 
                  color: indicator.up ? '#cf1322' : '#3f8600',
                  fontSize: '24px'
                }}
                prefix={indicator.up ? <ArrowUpOutlined /> : <ArrowDownOutlined />}
                suffix="%"
              />
              <div style={{ marginTop: 8 }}>
                <small style={{ color: '#8c8c8c' }}>
                  较上期{indicator.up ? '增加' : '减少'} {indicator.change}个百分点
                </small>
              </div>
            </Card>
          </Col>
        ))}
      </Row>
    );
  };

  // 渲染新闻列表
  const renderNewsList = (countryData: any) => {
    return (
      <List
        className="macro-news-list"
        itemLayout="horizontal"
        dataSource={countryData.news}
        renderItem={(item: any) => (
          <List.Item
            actions={[
              <span><CalendarOutlined style={{ marginRight: 4 }} />{item.date}</span>
            ]}
            extra={
              <Tag className={getTagClassName(item.tag)} color={item.tag === 'policy' ? 'blue' : item.tag === 'data' ? 'green' : 'orange'}>
                {item.category}
              </Tag>
            }
          >
            <List.Item.Meta
              title={<a href="#">{item.title}</a>}
            />
          </List.Item>
        )}
      />
    );
  };

  // 渲染指标趋势图部分
  const renderChartSection = (countryCode: string) => {
    return (
      <Row gutter={[16, 16]}>
        <Col span={8}>
          <MacroChart title="CPI指标趋势" chartType="CPI" countryCode={countryCode} />
        </Col>
        <Col span={8}>
          <MacroChart title="PMI指标趋势" chartType="PMI" countryCode={countryCode} />
        </Col>
        <Col span={8}>
          <MacroChart title="GDP增长趋势" chartType="GDP" countryCode={countryCode} />
        </Col>
      </Row>
    );
  };

  // 渲染国家/地区标签
  const renderCountryTab = (country: string, label: string) => {
    const iconMap: Record<string, any> = {
      'china': <GlobalOutlined style={{ color: '#1890ff' }} />,
      'usa': <GlobalOutlined style={{ color: '#722ed1' }} />,
      'europe': <GlobalOutlined style={{ color: '#eb2f96' }} />,
      'japan': <GlobalOutlined style={{ color: '#faad14' }} />
    };

    return (
      <span>
        <Space>
          {iconMap[country] || <GlobalOutlined />}
          {label}
        </Space>
      </span>
    );
  };

  // 渲染内容区域
  const renderCountryContent = (country: string) => {
    const countryData = macroData[country as keyof typeof macroData];
    const countryNames: Record<string, string> = {
      'china': '中国',
      'usa': '美国',
      'europe': '欧洲',
      'japan': '日本'
    };
    
    return (
      <>
        <Card 
          title={`${countryNames[country]}宏观经济指标`} 
          extra={
            <span className="update-time">
              <CalendarOutlined style={{ marginRight: 4 }} />
              更新时间: {countryData.updateTime}
            </span>
          }
        >
          {renderIndicatorCards(countryData)}
        </Card>
        
        <Divider orientation="left" className="section-divider">
          <Space>
            <InfoCircleOutlined />
            最新宏观经济新闻
          </Space>
        </Divider>
        
        <Card>
          {renderNewsList(countryData)}
          <div style={{ textAlign: 'right', marginTop: 16 }}>
            <Button 
              type="primary" 
              onClick={openNewsModal}
              style={{ 
                borderRadius: '4px',
                boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
                background: '#1890ff',
                transition: 'all 0.3s'
              }}
            >
              查看更多新闻
            </Button>
          </div>
        </Card>

        <Divider orientation="left" className="section-divider">
          <Space>
            <LineChartOutlined />
            指标趋势图
          </Space>
        </Divider>

        {renderChartSection(country)}
      </>
    );
  };

  return (
    <div className="page-content">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <Title level={2}>宏观经济数据</Title>
        <Space>
          <Button icon={<BarChartOutlined />}>数据对比</Button>
          <Button icon={<DollarOutlined />}>汇率查询</Button>
          <Button icon={<ShareAltOutlined />}>分享报告</Button>
        </Space>
      </div>
      
      <Tabs 
        defaultActiveKey="china" 
        onChange={handleTabChange} 
        type="card"
        className="macro-tabs"
      >
        <TabPane tab={renderCountryTab('china', '中国')} key="china">
          {renderCountryContent('china')}
        </TabPane>
        
        <TabPane tab={renderCountryTab('usa', '美国')} key="usa">
          {renderCountryContent('usa')}
        </TabPane>
        
        <TabPane tab={renderCountryTab('europe', '欧洲')} key="europe">
          {renderCountryContent('europe')}
        </TabPane>
        
        <TabPane tab={renderCountryTab('japan', '日本')} key="japan">
          {renderCountryContent('japan')}
        </TabPane>
      </Tabs>
      
      {/* 新闻模态框组件 */}
      <MacroEconomyNewsModal 
        countryCode={activeTab}
        countryName={getCountryName()}
        visible={newsModalVisible}
        onClose={closeNewsModal}
      />
    </div>
  );
};

export default MacroEconomyPage;