// src/components/common/CompareSelector.tsx
import React, { useState, useEffect } from 'react';
import { Row, Col, Button, Checkbox, Divider, Input, List, Tag } from 'antd';
import { SearchOutlined } from '@ant-design/icons';
import { CompareSelectProps, RelatedIndicatorType, CategoryType } from '../../types/indicator';

const { Search } = Input;

const CompareSelector: React.FC<CompareSelectProps> = ({
  currentIndicator,
  relatedIndicators = [],
  selectedIndicators = [],
  onConfirm,
  onCancel,
  maxSelect = 3
}) => {
  const [selected, setSelected] = useState<RelatedIndicatorType[]>([]);
  const [searchText, setSearchText] = useState<string>('');
  const [filteredIndicators, setFilteredIndicators] = useState<RelatedIndicatorType[]>([]);
  
  // 初始化已选择的指标
  useEffect(() => {
    setSelected(selectedIndicators);
  }, [selectedIndicators]);
  
  // 根据搜索文本过滤指标
  useEffect(() => {
    if (!searchText) {
      setFilteredIndicators(relatedIndicators);
      return;
    }
    
    const filtered = relatedIndicators.filter(indicator => 
      indicator.name.toLowerCase().includes(searchText.toLowerCase()) ||
      indicator.category.toLowerCase().includes(searchText.toLowerCase())
    );
    
    setFilteredIndicators(filtered);
  }, [searchText, relatedIndicators]);
  
  // 处理指标选择/取消选择
  const handleSelectChange = (indicator: RelatedIndicatorType): void => {
    const isSelected = selected.some(item => item.id === indicator.id);
    
    if (isSelected) {
      // 如果已选中，则取消选择
      setSelected(selected.filter(item => item.id !== indicator.id));
    } else {
      // 如果未选中，检查是否已达到最大选择数量
      if (selected.length >= maxSelect) {
        return; // 已达到最大选择数量，不执行操作
      }
      // 添加到已选择列表
      setSelected([...selected, indicator]);
    }
  };
  
  // 清除所有选择
  const handleClearAll = (): void => {
    setSelected([]);
  };
  
  // 确认选择
  const handleConfirm = (): void => {
    onConfirm(selected);
  };
  
  // 获取指标分类颜色
  const getCategoryColor = (category: CategoryType): string => {
    const categoryColors: Record<CategoryType, string> = {
      growth: '#1890ff',
      employment: '#52c41a',
      price: '#faad14',
      trade: '#722ed1',
      finance: '#eb2f96',
      consumption: '#fa8c16',
      production: '#13c2c2',
      other: '#d9d9d9'
    };
    
    return categoryColors[category] || categoryColors.other;
  };

  return (
    <div className="compare-selector">
      {/* 搜索框 */}
      <Search
        placeholder="搜索指标名称或分类"
        allowClear
        enterButton={<SearchOutlined />}
        onSearch={(value: string) => setSearchText(value)}
        onChange={(e) => setSearchText(e.target.value)}
        style={{ marginBottom: 16 }}
      />
      
      {/* 已选择指标区域 */}
      <div className="selected-indicators" style={{ marginBottom: 16 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
          <h4 style={{ margin: 0 }}>已选择的指标 ({selected.length}/{maxSelect})</h4>
          {selected.length > 0 && (
            <Button type="link" size="small" onClick={handleClearAll}>
              清除所有
            </Button>
          )}
        </div>
        <div>
          {selected.length === 0 ? (
            <div style={{ color: '#999', padding: '8px 0' }}>
              尚未选择指标，请从下方列表选择要对比的指标
            </div>
          ) : (
            <Row gutter={[8, 8]}>
              {selected.map(indicator => (
                <Col key={indicator.id}>
                  <Tag 
                    closable
                    onClose={() => handleSelectChange(indicator)}
                    color={getCategoryColor(indicator.category)}
                  >
                    {indicator.name}
                  </Tag>
                </Col>
              ))}
            </Row>
          )}
        </div>
      </div>
      
      <Divider style={{ margin: '12px 0' }} />
      
      {/* 可选择的指标列表 */}
      <div style={{ height: 300, overflow: 'auto' }}>
        <List
          size="small"
          dataSource={filteredIndicators}
          renderItem={indicator => (
            <List.Item
              key={indicator.id}
              style={{ cursor: 'pointer' }}
              onClick={() => handleSelectChange(indicator)}
            >
              <Checkbox 
                checked={selected.some(item => item.id === indicator.id)}
                onChange={() => {}}
                style={{ marginRight: 8 }}
              />
              <div>
                <div>{indicator.name}</div>
                <div style={{ fontSize: 12, color: '#999' }}>
                  <Tag color={getCategoryColor(indicator.category)} style={{ fontSize: 12 }}>
                    {indicator.category}
                  </Tag>
                  {indicator.frequency}
                </div>
              </div>
            </List.Item>
          )}
          locale={{ emptyText: '没有找到匹配的指标' }}
        />
      </div>
      
      {/* 底部按钮 */}
      <div style={{ marginTop: 16, textAlign: 'right' }}>
        <Button onClick={onCancel} style={{ marginRight: 8 }}>
          取消
        </Button>
        <Button type="primary" onClick={handleConfirm} disabled={selected.length === 0}>
          确认对比 ({selected.length})
        </Button>
      </div>
    </div>
  );
};

export default CompareSelector;