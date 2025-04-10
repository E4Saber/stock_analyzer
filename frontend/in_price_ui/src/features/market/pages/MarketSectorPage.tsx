// src/features/market/pages/MarketSectorPage.tsx
import React, { useState } from 'react';
import { Typography, Card, Row, Col, Tabs, Table, Divider, List, Tag } from 'antd';
import { ArrowUpOutlined, ArrowDownOutlined, FireOutlined, DollarOutlined, RiseOutlined } from '@ant-design/icons';
import './MarketSectorPage.css';

const { Title } = Typography;
const { TabPane } = Tabs;

// 板块数据结构 - 保持不变
const sectorData = [
  { name: '半导体', change: 3.56, marketCap: 1890, gridArea: 'semi', isRising: true },
  { name: '软件服务', change: 1.85, marketCap: 1430, gridArea: 'software', isRising: true },
  { name: '硬件设备', change: 2.12, marketCap: 1240, gridArea: 'hardware', isRising: true },
  { name: '云计算', change: 2.78, marketCap: 1118, gridArea: 'cloud', isRising: true },
  { name: '银行', change: -0.76, marketCap: 3450, gridArea: 'bank', isRising: false },
  { name: '保险', change: -0.92, marketCap: 2340, gridArea: 'insurance', isRising: false },
  { name: '证券', change: -0.45, marketCap: 1970, gridArea: 'securities', isRising: false },
  { name: '多元金融', change: -1.23, marketCap: 1141, gridArea: 'finance', isRising: false },
  { name: '生物制药', change: 2.34, marketCap: 1560, gridArea: 'pharma', isRising: true },
  { name: '医疗器械', change: 1.45, marketCap: 1230, gridArea: 'medical', isRising: true },
  { name: '医疗服务', change: 0.87, marketCap: 987, gridArea: 'healthcare', isRising: true },
  { name: '煤炭', change: -1.87, marketCap: 756, gridArea: 'coal', isRising: false },
  { name: '电力', change: -0.45, marketCap: 534, gridArea: 'power', isRising: false },
  { name: '新能源', change: 2.87, marketCap: 1165, gridArea: 'newenergy', isRising: true }
];

// 涨跌榜数据
const topGainersLosersData = [
  { sector: '半导体', change: 3.45, stocks: 34, leaders: ['中芯国际', '韦尔股份'] },
  { sector: '新能源', change: 2.87, stocks: 42, leaders: ['宁德时代', '隆基绿能'] },
  { sector: '生物医药', change: 2.34, stocks: 28, leaders: ['恒瑞医药', '药明康德'] },
  { sector: '互联网', change: 2.12, stocks: 23, leaders: ['腾讯控股', '阿里巴巴'] },
  { sector: '银行', change: -1.23, stocks: 18, leaders: ['工商银行', '招商银行'] },
  { sector: '房地产', change: -2.67, stocks: 25, leaders: ['万科A', '保利发展'] },
  { sector: '煤炭', change: -1.87, stocks: 15, leaders: ['中国神华', '陕西煤业'] },
  { sector: '航空', change: -1.56, stocks: 8, leaders: ['中国国航', '南方航空'] },
];

// 人气榜数据
const popularSectorsData = [
  { sector: '芯片', popularity: 98, hotTopics: ['国产替代', '供应链安全'] },
  { sector: 'AI', popularity: 95, hotTopics: ['大模型', '智能驾驶'] },
  { sector: '新能源车', popularity: 92, hotTopics: ['电池技术', '智能座舱'] },
  { sector: '生物科技', popularity: 87, hotTopics: ['创新药', 'CDMO'] },
  { sector: '数字经济', popularity: 85, hotTopics: ['元宇宙', '数字人民币'] },
];

// 资金榜数据
const capitalFlowData = [
  { sector: '半导体', netInflow: 34.56, percentChange: 2.34 },
  { sector: '新能源', netInflow: 28.92, percentChange: 1.87 },
  { sector: '医疗器械', netInflow: 21.45, percentChange: 1.56 },
  { sector: '人工智能', netInflow: 19.34, percentChange: 2.78 },
  { sector: '生物医药', netInflow: 17.89, percentChange: 1.23 },
  { sector: '银行', netInflow: -12.34, percentChange: -0.87 },
  { sector: '房地产', netInflow: -15.67, percentChange: -1.98 },
  { sector: '钢铁', netInflow: -8.92, percentChange: -1.45 },
];

// 潜力榜数据
const potentialSectorsData = [
  { sector: '光伏', score: 89, keyFactors: ['政策支持', '技术创新', '海外需求'] },
  { sector: '生物制药', score: 87, keyFactors: ['医保谈判', '创新药审批', '老龄化'] },
  { sector: '智能汽车', score: 85, keyFactors: ['电动化加速', '自动驾驶', '智能座舱'] },
  { sector: '数字经济', score: 83, keyFactors: ['数字人民币', '产业数字化', '元宇宙'] },
  { sector: '军工', score: 82, keyFactors: ['国防需求', '技术突破', '产业整合'] },
];

const MarketSectorPage: React.FC = () => {
  const [sectorView, setSectorView] = useState<'all' | 'gainers' | 'losers'>('all');
  
  // 涨跌榜表格列
  const topMoversColumns = [
    {
      title: '行业板块',
      dataIndex: 'sector',
      key: 'sector',
    },
    {
      title: '涨跌幅',
      dataIndex: 'change',
      key: 'change',
      sorter: (a, b) => a.change - b.change,
      render: (text) => (
        <span style={{ color: text >= 0 ? '#e60012' : '#19a15f' }}>
          {text >= 0 ? <ArrowUpOutlined /> : <ArrowDownOutlined />} {Math.abs(text).toFixed(2)}%
        </span>
      ),
    },
    {
      title: '成分股数量',
      dataIndex: 'stocks',
      key: 'stocks',
    },
    {
      title: '龙头股',
      dataIndex: 'leaders',
      key: 'leaders',
      render: (leaders) => (
        <>
          {leaders.map(stock => (
            <Tag color="blue" key={stock}>{stock}</Tag>
          ))}
        </>
      ),
    },
  ];

  // 筛选涨跌榜数据
  const getFilteredMoversData = () => {
    if (sectorView === 'gainers') {
      return topGainersLosersData.filter(item => item.change > 0).sort((a, b) => b.change - a.change);
    } else if (sectorView === 'losers') {
      return topGainersLosersData.filter(item => item.change < 0).sort((a, b) => a.change - b.change);
    }
    return topGainersLosersData.sort((a, b) => b.change - a.change);
  };

  return (
    <div className="page-content">
      <Row gutter={[16, 16]}>
        {/* 左侧热力图 */}
        <Col flex="680px">
          <Card 
            title="行业板块热力图" 
            bordered={false}
          >
            <div className="sector-heatmap">
              {sectorData.map((sector) => (
                <div 
                  key={sector.gridArea}
                  className={`sector-item ${sector.isRising ? 'rising' : 'falling'} ${sector.change >= 2 || sector.change <= -2 ? 'strong' : ''}`}
                  style={{ gridArea: sector.gridArea }}
                  data-marketcap={`市值: ${sector.marketCap}亿`}
                >
                  <div className="sector-name">{sector.name}</div>
                  <div className="sector-change">
                    {sector.isRising ? '+' : ''}{sector.change}%
                  </div>
                </div>
              ))}
            </div>
            
            {/* 图例 */}
            <div className="sector-legend">
              <div className="legend-item">
                <div className="legend-color strong-rising"></div>
                <span>涨幅 &gt;= 2%</span>
              </div>
              <div className="legend-item">
                <div className="legend-color rising"></div>
                <span>涨幅 0-2%</span>
              </div>
              <div className="legend-item">
                <div className="legend-color falling"></div>
                <span>跌幅 0-2%</span>
              </div>
              <div className="legend-item">
                <div className="legend-color strong-falling"></div>
                <span>跌幅 &gt;= 2%</span>
              </div>
            </div>
          </Card>
        </Col>
        
        {/* 右侧并列放置人气榜和潜力榜 */}
        <Col flex="auto">
          <Row gutter={[0, 16]}>
            {/* 人气榜 */}
            <Col span={24}>
              <Card 
                title={<><FireOutlined /> 行业人气榜</>} 
                bordered={false}
                bodyStyle={{ maxHeight: '200px', overflowY: 'auto' }}
              >
                <List
                  size="small"
                  dataSource={popularSectorsData}
                  renderItem={(item, index) => (
                    <List.Item style={{ padding: '4px 0' }}>
                      <div style={{ width: '100%' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                          <span style={{ fontWeight: 'bold' }}>
                            {index + 1}. {item.sector}
                          </span>
                          <span style={{ color: '#e60012' }}>
                            {item.popularity}
                          </span>
                        </div>
                        <div style={{ marginTop: 4 }}>
                          {item.hotTopics.map(topic => (
                            <Tag color="volcano" key={topic} style={{ marginBottom: 4 }}>{topic}</Tag>
                          ))}
                        </div>
                      </div>
                    </List.Item>
                  )}
                />
              </Card>
            </Col>
          
            {/* 潜力榜 */}
            <Col span={24}>
              <Card 
                title={<><RiseOutlined /> 行业潜力榜</>} 
                bordered={false}
                bodyStyle={{ maxHeight: '200px', overflowY: 'auto' }}
              >
                <List
                  size="small"
                  dataSource={potentialSectorsData}
                  renderItem={(item, index) => (
                    <List.Item style={{ padding: '4px 0' }}>
                      <div style={{ width: '100%' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                          <span style={{ fontWeight: 'bold' }}>
                            {index + 1}. {item.sector}
                          </span>
                          <span style={{ color: '#1890ff' }}>
                            {item.score}
                          </span>
                        </div>
                        <div style={{ marginTop: 4 }}>
                          {item.keyFactors.map(factor => (
                            <Tag color="blue" key={factor} style={{ marginBottom: 4 }}>{factor}</Tag>
                          ))}
                        </div>
                      </div>
                    </List.Item>
                  )}
                />
              </Card>
            </Col>
          </Row>
        </Col>
      </Row>
      
      {/* 底部布局 - 涨跌榜和资金榜 */}
      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        {/* 涨跌榜 */}
        <Col span={12}>
          <Card 
            title="行业涨跌榜" 
            bordered={false}
            extra={
              <Tabs 
                defaultActiveKey="all" 
                onChange={value => setSectorView(value as 'all' | 'gainers' | 'losers')}
                size="small"
              >
                <TabPane tab="全部" key="all" />
                <TabPane tab="上涨板块" key="gainers" />
                <TabPane tab="下跌板块" key="losers" />
              </Tabs>
            }
          >
            <Table 
              columns={topMoversColumns} 
              dataSource={getFilteredMoversData().map((item, index) => ({ ...item, key: index }))} 
              pagination={false} 
              size="middle"
            />
          </Card>
        </Col>
        
        {/* 资金榜 */}
        <Col span={12}>
          <Card title={<><DollarOutlined /> 资金流向榜</>} bordered={false}>
            <Table 
              columns={[
                {
                  title: '行业板块',
                  dataIndex: 'sector',
                  key: 'sector',
                },
                {
                  title: '净流入(亿)',
                  dataIndex: 'netInflow',
                  key: 'netInflow',
                  sorter: (a, b) => a.netInflow - b.netInflow,
                  render: (text) => (
                    <span style={{ color: text >= 0 ? '#e60012' : '#19a15f' }}>
                      {text.toFixed(2)}
                    </span>
                  ),
                },
                {
                  title: '涨跌幅',
                  dataIndex: 'percentChange',
                  key: 'percentChange',
                  render: (text) => (
                    <span style={{ color: text >= 0 ? '#e60012' : '#19a15f' }}>
                      {text >= 0 ? <ArrowUpOutlined /> : <ArrowDownOutlined />} {Math.abs(text).toFixed(2)}%
                    </span>
                  ),
                },
              ]} 
              dataSource={capitalFlowData.map((item, index) => ({ ...item, key: index }))} 
              pagination={false}
              size="middle"
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default MarketSectorPage;