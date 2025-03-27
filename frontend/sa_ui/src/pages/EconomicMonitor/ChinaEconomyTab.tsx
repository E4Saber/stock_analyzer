// src/pages/EconomicMonitor/ChinaEconomyTab.tsx
import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Input, Select, Tabs, List, Tag, Spin, Empty, Button } from 'antd';
import { SearchOutlined, FilterOutlined, SortAscendingOutlined, SortDescendingOutlined } from '@ant-design/icons';
import IndicatorCard from '../../components/cards/IndicatorCard';
import dashboardData from '../../mock/indicators/dashboardData';
import { IndicatorType, RegionTabProps, CategoryType } from '../../types/indicator';

const { Option } = Select;
const { TabPane } = Tabs;
const { Search } = Input;

const ChinaEconomyTab: React.FC<RegionTabProps> = ({ onIndicatorSelect }) => {
  const [loading, setLoading] = useState<boolean>(true);
  const [searchText, setSearchText] = useState<string>('');
  const [indicators, setIndicators] = useState<IndicatorType[]>([]);
  const [categoryFilter, setCategoryFilter] = useState<CategoryType | 'all'>('all');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  // 获取中国指标数据
  useEffect(() => {
    setLoading(true);
    
    // 模拟异步加载数据
    setTimeout(() => {
      // 过滤中国指标
      const chinaIndicators = dashboardData.filter(indicator => indicator.region === 'china');
      setIndicators(chinaIndicators);
      setLoading(false);
    }, 800);
  }, []);

  // 处理搜索
  const handleSearch = (value: string) => {
    setSearchText(value);
  };

  // 处理分类筛选
  const handleCategoryChange = (value: CategoryType | 'all') => {
    setCategoryFilter(value);
  };

  // 处理排序
  const handleSortChange = () => {
    setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
  };

  // 根据搜索、筛选和排序获取过滤后的指标
  const getFilteredIndicators = () => {
    let filtered = [...indicators];

    // 应用搜索过滤
    if (searchText) {
      const searchLower = searchText.toLowerCase();
      filtered = filtered.filter(indicator => 
        indicator.name.toLowerCase().includes(searchLower) ||
        indicator.category.toLowerCase().includes(searchLower)
      );
    }

    // 应用分类过滤
    if (categoryFilter !== 'all') {
      filtered = filtered.filter(indicator => indicator.category === categoryFilter);
    }

    // 应用排序
    filtered.sort((a, b) => {
      let comparisonResult = 0;
      
      // 默认按照指标名称排序
      comparisonResult = a.name.localeCompare(b.name);
      
      // 如果是降序，反转比较结果
      return sortOrder === 'asc' ? comparisonResult : -comparisonResult;
    });

    return filtered;
  };

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

  // 获取分类标签颜色
  const getCategoryColor = (category: CategoryType): string => {
    const categoryColors: Record<CategoryType, string> = {
      growth: '#1890ff',
      employment: '#52c41a',
      price: '#faad14',
      trade: '#722ed1',
      finance: '#eb2f96',
      consumption: '#fa8c16',
      production: '#13c2c2',
      other: '#8c8c8c'
    };
    
    return categoryColors[category];
  };

  // 过滤后的指标
  const filteredIndicators = getFilteredIndicators();

  return (
    <div className="china-economy-tab">
      {/* 筛选工具栏 */}
      <Card className="filter-toolbar" style={{ marginBottom: 16 }}>
        <Row gutter={16} align="middle">
          <Col span={8}>
            <Search
              placeholder="搜索指标名称或分类"
              allowClear
              enterButton={<SearchOutlined />}
              size="middle"
              onSearch={handleSearch}
              onChange={e => setSearchText(e.target.value)}
            />
          </Col>
          <Col span={6}>
            <Select
              placeholder={<><FilterOutlined /> 按分类筛选</>}
              style={{ width: '100%' }}
              onChange={handleCategoryChange}
              value={categoryFilter}
            >
              {categories.map(category => (
                <Option key={category.value} value={category.value}>
                  {category.label}
                </Option>
              ))}
            </Select>
          </Col>
          <Col span={4}>
            <Button 
              icon={sortOrder === 'asc' ? <SortAscendingOutlined /> : <SortDescendingOutlined />}
              onClick={handleSortChange}
            >
              {sortOrder === 'asc' ? '升序' : '降序'}
            </Button>
          </Col>
          <Col span={6} style={{ textAlign: 'right' }}>
            共 {filteredIndicators.length} 个指标
          </Col>
        </Row>
      </Card>

      {/* 指标展示区域 */}
      <Spin spinning={loading}>
        {filteredIndicators.length > 0 ? (
          <Tabs defaultActiveKey="grid" tabPosition="top">
            <TabPane tab="网格视图" key="grid">
              <Row gutter={[16, 16]}>
                {filteredIndicators.map(indicator => (
                  <Col xs={24} sm={12} md={8} lg={6} key={indicator.id}>
                    <IndicatorCard
                      indicator={indicator}
                      onClick={() => onIndicatorSelect(indicator)}
                    />
                  </Col>
                ))}
              </Row>
            </TabPane>
            
            <TabPane tab="列表视图" key="list">
              <List
                itemLayout="horizontal"
                dataSource={filteredIndicators}
                renderItem={indicator => (
                  <List.Item
                    key={indicator.id}
                    onClick={() => onIndicatorSelect(indicator)}
                    style={{ cursor: 'pointer' }}
                  >
                    <List.Item.Meta
                      title={
                        <div style={{ display: 'flex', alignItems: 'center' }}>
                          <span>{indicator.name}</span>
                          <Tag color={getCategoryColor(indicator.category)} style={{ marginLeft: 8 }}>
                            {indicator.category}
                          </Tag>
                        </div>
                      }
                      description={`更新时间: ${indicator.updateTime}`}
                    />
                    <div>
                      <div style={{ textAlign: 'right', fontSize: 16, fontWeight: 'bold' }}>
                        {indicator.value} {indicator.unit}
                      </div>
                      <div style={{ 
                        color: indicator.changeType === 'increase' ? '#3f8600' : '#cf1322',
                        textAlign: 'right' 
                      }}>
                        {indicator.changeType === 'increase' ? '+' : ''}{indicator.change}%
                      </div>
                    </div>
                  </List.Item>
                )}
              />
            </TabPane>
          </Tabs>
        ) : (
          <Empty description="没有找到符合条件的指标" />
        )}
      </Spin>
    </div>
  );
};

export default ChinaEconomyTab;