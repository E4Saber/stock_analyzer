// src/pages/EconomicMonitor/DashboardTab.tsx
import React, { useEffect, useState } from 'react';
import { Row, Col, Select, Alert, Spin } from 'antd';
import { InfoCircleOutlined, ReloadOutlined } from '@ant-design/icons';
import IndicatorCard from '../../components/cards/IndicatorCard';
import dashboardData from '../../mock/indicators/dashboardData';
import { 
  IndicatorType, 
  DashboardTabProps, 
  RegionType, 
  CategoryType, 
  TimeRangeType 
} from '../../types/indicator';

const { Option } = Select;

const DashboardTab: React.FC<DashboardTabProps> = ({ onIndicatorSelect }) => {
  const [loading, setLoading] = useState<boolean>(true);
  const [timeRange, setTimeRange] = useState<TimeRangeType>('1y'); // 默认显示一年数据
  const [region, setRegion] = useState<RegionType | 'all'>('all'); // 默认显示所有地区
  const [categoryFilter, setCategoryFilter] = useState<CategoryType | 'all'>('all'); // 默认显示所有分类
  const [displayData, setDisplayData] = useState<IndicatorType[]>([]);
  
  // 模拟加载数据
  useEffect(() => {
    setLoading(true);
    
    // 模拟异步加载数据
    setTimeout(() => {
      // 过滤数据
      let filteredData = [...dashboardData];
      
      if (region !== 'all') {
        filteredData = filteredData.filter(item => item.region === region);
      }
      
      if (categoryFilter !== 'all') {
        filteredData = filteredData.filter(item => item.category === categoryFilter);
      }
      
      // 只显示前12个指标
      setDisplayData(filteredData.slice(0, 12));
      setLoading(false);
    }, 800);
  }, [timeRange, region, categoryFilter]);
  
  // 指标分类选项
  const categories = [
    { value: 'all', label: '所有分类' },
    { value: 'growth', label: '经济增长' },
    { value: 'employment', label: '就业市场' },
    { value: 'price', label: '物价水平' },
    { value: 'trade', label: '贸易数据' },
    { value: 'finance', label: '金融指标' },
    { value: 'consumption', label: '消费指标' },
    { value: 'production', label: '生产指标' }
  ];
  
  // 地区选项
  const regions = [
    { value: 'all', label: '所有地区' },
    { value: 'us', label: '美国' },
    { value: 'china', label: '中国' },
    { value: 'cross', label: '中美交叉' }
  ];
  
  // 时间范围选项
  const timeRanges = [
    { value: '1m', label: '近1个月' },
    { value: '3m', label: '近3个月' },
    { value: '6m', label: '近6个月' },
    { value: '1y', label: '近1年' },
    { value: '3y', label: '近3年' }
  ];

  return (
    <div className="dashboard-container">
      {/* 顶部筛选区域 */}
      <div className="dashboard-header" style={{ marginBottom: 16 }}>
        <Row gutter={16} align="middle">
          <Col span={6}>
            <Select 
              value={region}
              onChange={(value: RegionType | 'all') => setRegion(value)}
              style={{ width: '100%' }}
              placeholder="选择地区"
            >
              {regions.map(item => (
                <Option key={item.value} value={item.value}>{item.label}</Option>
              ))}
            </Select>
          </Col>
          <Col span={6}>
            <Select 
              value={categoryFilter}
              onChange={(value: CategoryType | 'all') => setCategoryFilter(value)}
              style={{ width: '100%' }}
              placeholder="选择指标分类"
            >
              {categories.map(item => (
                <Option key={item.value} value={item.value}>{item.label}</Option>
              ))}
            </Select>
          </Col>
          <Col span={8}>
            <Select 
              value={timeRange}
              onChange={(value: TimeRangeType) => setTimeRange(value)}
              style={{ width: '100%' }}
              placeholder="选择时间范围"
            >
              {timeRanges.map(item => (
                <Option key={item.value} value={item.value as TimeRangeType}>{item.label}</Option>
              ))}
            </Select>
          </Col>
          <Col span={4} style={{ textAlign: 'right' }}>
            <ReloadOutlined 
              style={{ fontSize: 18, cursor: 'pointer' }} 
              onClick={() => {
                setLoading(true);
                setTimeout(() => setLoading(false), 800);
              }}
            />
          </Col>
        </Row>
      </div>
      
      {/* 异常指标提醒 */}
      {displayData.some(item => item.status === 'warning' || item.status === 'alert') && (
        <Alert 
          message="指标异常提醒" 
          description="有5个指标出现异常波动，请关注详情。" 
          type="warning" 
          showIcon 
          style={{ marginBottom: 16 }}
        />
      )}
      
      {/* 指标卡片网格 */}
      <Spin spinning={loading}>
        <Row gutter={[16, 16]}>
          {displayData.map(indicator => (
            <Col xs={24} sm={12} md={8} lg={6} xl={6} key={indicator.id}>
              <IndicatorCard 
                indicator={indicator}
                onClick={() => onIndicatorSelect(indicator)}
              />
            </Col>
          ))}
        </Row>
      </Spin>
      
      {/* 底部数据更新信息 */}
      <div style={{ marginTop: 24, textAlign: 'right' }}>
        <span style={{ color: '#999' }}>
          <InfoCircleOutlined /> 数据更新时间: 2023-04-15 08:30
        </span>
      </div>
    </div>
  );
};

export default DashboardTab;