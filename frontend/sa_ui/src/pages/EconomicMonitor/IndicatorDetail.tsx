// src/pages/EconomicMonitor/IndicatorDetail.jsx
import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Button, Tabs, Table, Statistic, Tag, Select, Radio, Divider, Spin, Typography, Tooltip, Modal } from 'antd';
import { ArrowLeftOutlined, InfoCircleOutlined, DownloadOutlined, SyncOutlined, LineChartOutlined, BarChartOutlined, CompressOutlined } from '@ant-design/icons';
import { LineChart, BarChart, ComparisonChart, MiniChart } from '../../components/charts/index';
import DataSummaryCard from '../../components/cards/IndicatorCard';
import CompareSelector from '../../components/widgets/CompareSelector';
import { getIndicatorData, getRelatedIndicators } from '../../services/mock/indicators';

const { TabPane } = Tabs;
const { Title, Paragraph, Text } = Typography;
const { Option } = Select;

const IndicatorDetail = ({ indicator, onBack }) => {
  const [loading, setLoading] = useState(true);
  const [indicatorData, setIndicatorData] = useState(null);
  const [relatedIndicators, setRelatedIndicators] = useState([]);
  const [timeRange, setTimeRange] = useState('1y');
  const [displayType, setDisplayType] = useState('line');
  const [compareMode, setCompareMode] = useState('yoy'); // 同比(yoy)或环比(mom)
  const [selectedRelatedIndicators, setSelectedRelatedIndicators] = useState([]);
  const [isCompareModalVisible, setIsCompareModalVisible] = useState(false);
  
  // 加载指标数据
  useEffect(() => {
    if (!indicator) return;
    
    setLoading(true);
    
    // 模拟异步加载数据
    setTimeout(() => {
      const data = getIndicatorData(indicator.id, timeRange);
      const related = getRelatedIndicators(indicator.id);
      
      setIndicatorData(data);
      setRelatedIndicators(related);
      setLoading(false);
    }, 800);
  }, [indicator, timeRange]);
  
  // 处理时间范围变更
  const handleTimeRangeChange = (value) => {
    setTimeRange(value);
  };
  
  // 处理显示类型变更（折线图/柱状图）
  const handleDisplayTypeChange = (e) => {
    setDisplayType(e.target.value);
  };
  
  // 处理同比/环比切换
  const handleCompareModeChange = (value) => {
    setCompareMode(value);
  };
  
  // 打开对比指标选择器
  const handleCompareClick = () => {
    setIsCompareModalVisible(true);
  };
  
  // 确认选择对比指标
  const handleCompareConfirm = (selectedIndicators) => {
    setSelectedRelatedIndicators(selectedIndicators);
    setIsCompareModalVisible(false);
  };
  
  // 渲染主图表
  const renderMainChart = () => {
    if (!indicatorData) return null;
    
    const chartProps = {
      data: indicatorData.chartData,
      title: indicator.name,
      compareMode: compareMode,
      height: 400,
      showTooltip: true,
      showLegend: selectedRelatedIndicators.length > 0,
      compareWith: selectedRelatedIndicators,
    };
    
    return displayType === 'line' ? (
      <LineChart {...chartProps} />
    ) : (
      <BarChart {...chartProps} />
    );
  };
  
  // 渲染数据表格
  const renderDataTable = () => {
    if (!indicatorData) return null;
    
    const columns = [
      {
        title: '日期',
        dataIndex: 'date',
        key: 'date',
        width: 120,
      },
      {
        title: '数值',
        dataIndex: 'value',
        key: 'value',
        width: 120,
        render: (text) => Number(text).toFixed(2),
      },
      {
        title: '同比(%)',
        dataIndex: 'yoy',
        key: 'yoy',
        width: 120,
        render: (text) => {
          const value = Number(text);
          const color = value >= 0 ? '#52c41a' : '#f5222d';
          return <span style={{ color }}>{value >= 0 ? '+' : ''}{value.toFixed(2)}%</span>;
        },
      },
      {
        title: '环比(%)',
        dataIndex: 'mom',
        key: 'mom',
        width: 120,
        render: (text) => {
          const value = Number(text);
          const color = value >= 0 ? '#52c41a' : '#f5222d';
          return <span style={{ color }}>{value >= 0 ? '+' : ''}{value.toFixed(2)}%</span>;
        },
      },
    ];
    
    return (
      <Table 
        columns={columns} 
        dataSource={indicatorData.tableData} 
        rowKey="date"
        size="small"
        pagination={{ pageSize: 10 }}
      />
    );
  };

  return (
    <div className="indicator-detail">
      {/* 返回按钮和指标标题 */}
      <div style={{ marginBottom: 16 }}>
        <Button 
          type="link" 
          icon={<ArrowLeftOutlined />} 
          onClick={onBack}
          style={{ paddingLeft: 0 }}
        >
          返回指标列表
        </Button>
        <Divider type="vertical" />
        <Text>当前指标：</Text>
        <Text strong>{indicator?.name}</Text>
        <Tag color={indicator?.status === 'normal' ? 'green' : indicator?.status === 'warning' ? 'orange' : 'red'} style={{ marginLeft: 8 }}>
          {indicator?.status === 'normal' ? '正常' : indicator?.status === 'warning' ? '警告' : '异常'}
        </Tag>
      </div>
      
      <Spin spinning={loading}>
        {indicatorData && (
          <>
            {/* 顶部信息卡片 */}
            <Card style={{ marginBottom: 16 }}>
              <Row gutter={16} align="middle">
                <Col span={6}>
                  <Statistic 
                    title="最新值" 
                    value={indicatorData.current} 
                    precision={2}
                    suffix={indicatorData.unit}
                  />
                </Col>
                <Col span={6}>
                  <Statistic 
                    title="同比变化" 
                    value={indicatorData.yoy} 
                    precision={2}
                    valueStyle={{ color: indicatorData.yoy >= 0 ? '#3f8600' : '#cf1322' }}
                    prefix={indicatorData.yoy >= 0 ? '+' : ''}
                    suffix="%"
                  />
                </Col>
                <Col span={6}>
                  <Statistic 
                    title="环比变化" 
                    value={indicatorData.mom} 
                    precision={2}
                    valueStyle={{ color: indicatorData.mom >= 0 ? '#3f8600' : '#cf1322' }}
                    prefix={indicatorData.mom >= 0 ? '+' : ''}
                    suffix="%"
                  />
                </Col>
                <Col span={6}>
                  <Row>
                    <Col span={12}>
                      <Statistic 
                        title="预期值" 
                        value={indicatorData.expected} 
                        precision={2}
                        suffix={indicatorData.unit}
                        valueStyle={{ fontSize: '14px' }}
                      />
                    </Col>
                    <Col span={12}>
                      <Statistic 
                        title="数据来源" 
                        value={indicatorData.source}
                        valueStyle={{ fontSize: '14px' }}
                      />
                      <Text type="secondary" style={{ fontSize: '12px' }}>
                        {indicatorData.updateTime} 更新
                      </Text>
                    </Col>
                  </Row>
                </Col>
              </Row>
            </Card>
            
            {/* 主要内容区域 */}
            <Row gutter={16}>
              {/* 主图表区域 */}
              <Col span={18}>
                <Card>
                  <div className="chart-toolbar" style={{ marginBottom: 16 }}>
                    <Row justify="space-between" align="middle">
                      <Col>
                        <Select 
                          value={timeRange} 
                          onChange={handleTimeRangeChange}
                          style={{ width: 120, marginRight: 16 }}
                        >
                          <Option value="1m">近1个月</Option>
                          <Option value="3m">近3个月</Option>
                          <Option value="6m">近6个月</Option>
                          <Option value="1y">近1年</Option>
                          <Option value="3y">近3年</Option>
                          <Option value="5y">近5年</Option>
                        </Select>
                        
                        <Select 
                          value={compareMode} 
                          onChange={handleCompareModeChange}
                          style={{ width: 120, marginRight: 16 }}
                        >
                          <Option value="yoy">同比</Option>
                          <Option value="mom">环比</Option>
                          <Option value="actual">实际值</Option>
                        </Select>
                        
                        <Radio.Group 
                          value={displayType} 
                          onChange={handleDisplayTypeChange}
                          style={{ marginRight: 16 }}
                        >
                          <Radio.Button value="line"><LineChartOutlined /> 折线图</Radio.Button>
                          <Radio.Button value="bar"><BarChartOutlined /> 柱状图</Radio.Button>
                        </Radio.Group>
                      </Col>
                      
                      <Col>
                        <Button 
                          type="primary" 
                          icon={<CompressOutlined />} 
                          onClick={handleCompareClick}
                          style={{ marginRight: 8 }}
                        >
                          对比
                        </Button>
                        <Button 
                          icon={<DownloadOutlined />} 
                          style={{ marginRight: 8 }}
                        >
                          导出
                        </Button>
                        <Button 
                          icon={<SyncOutlined />} 
                        >
                          刷新
                        </Button>
                      </Col>
                    </Row>
                  </div>
                  
                  {/* 主图表 */}
                  <div className="main-chart">
                    {renderMainChart()}
                  </div>
                  
                  {/* 表格/数据视图 */}
                  <Tabs defaultActiveKey="chart" style={{ marginTop: 16 }}>
                    <TabPane tab="图表" key="chart">
                      {/* 图表已在上方显示 */}
                    </TabPane>
                    <TabPane tab="数据表格" key="table">
                      {renderDataTable()}
                    </TabPane>
                  </Tabs>
                </Card>
              </Col>
              
              {/* 右侧补充信息面板 */}
              <Col span={6}>
                {/* 数据概览卡片 */}
                <DataSummaryCard 
                  title="数据概览"
                  data={{
                    max: indicatorData.max,
                    min: indicatorData.min,
                    avg: indicatorData.avg,
                    trend: indicatorData.trend
                  }}
                  style={{ marginBottom: 16 }}
                />
                
                {/* 相关指标 */}
                <Card title="相关指标" style={{ marginBottom: 16 }}>
                  {relatedIndicators.map(item => (
                    <div key={item.id} style={{ marginBottom: 16 }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                        <Text>{item.name}</Text>
                        <Text>{item.current} {item.unit}</Text>
                      </div>
                      <MiniChart 
                        data={item.chartData} 
                        height={40} 
                        color={item.trend === 'up' ? '#f5222d' : '#52c41a'} 
                      />
                    </div>
                  ))}
                </Card>
                
                {/* 指标说明 */}
                <Card title="指标说明">
                  <Paragraph>
                    {indicatorData.description}
                  </Paragraph>
                  <Divider />
                  <Title level={5}>更新频率</Title>
                  <Paragraph>{indicatorData.frequency}</Paragraph>
                  <Title level={5}>数据来源</Title>
                  <Paragraph>{indicatorData.source}</Paragraph>
                </Card>
              </Col>
            </Row>
          </>
        )}
      </Spin>
      
      {/* 对比指标选择弹窗 */}
      <Modal
        title="选择对比指标"
        visible={isCompareModalVisible}
        onCancel={() => setIsCompareModalVisible(false)}
        footer={null}
        width={700}
      >
        <CompareSelector 
          currentIndicator={indicator}
          relatedIndicators={relatedIndicators}
          selectedIndicators={selectedRelatedIndicators}
          onConfirm={handleCompareConfirm}
          onCancel={() => setIsCompareModalVisible(false)}
        />
      </Modal>
    </div>
  );
};

export default IndicatorDetail;