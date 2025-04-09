import React, { useState } from 'react';
import { Modal, List, Tag, Space, Button, Input, Select, DatePicker, Divider, Typography } from 'antd';
import { CalendarOutlined, SearchOutlined, FilterOutlined, SortAscendingOutlined } from '@ant-design/icons';

const { RangePicker } = DatePicker;
const { Option } = Select;
const { Title } = Typography;

// 新闻类型接口
interface NewsItem {
  id: string;
  title: string;
  summary?: string;
  date: string;
  category: string;
  tag: string;
  source?: string;
}

// 组件属性接口
interface MacroNewsModalProps {
  countryCode: string;
  countryName: string;
  visible: boolean;
  onClose: () => void;
}

// 模拟更多新闻数据
const getMockNewsData = (countryCode: string): NewsItem[] => {
  // 这里可以根据不同国家返回不同的新闻列表
  const baseNews: NewsItem[] = [
    {
      id: '1',
      title: '央行宣布下调存款准备金率0.5个百分点，释放长期资金约1万亿元',
      summary: '中国人民银行决定于2024年10月1日下调金融机构存款准备金率0.5个百分点，释放长期资金约1万亿元。此次下调存款准备金率，有助于为实体经济提供长期稳定的资金支持。',
      date: '2024-09-20',
      category: '金融政策',
      tag: 'policy',
      source: '中国人民银行'
    },
    {
      id: '2',
      title: '8月社会消费品零售总额同比增长5.2%，消费持续恢复',
      summary: '国家统计局数据显示，8月份，社会消费品零售总额38965亿元，同比增长5.2%，比上月加快0.3个百分点，显示消费市场持续恢复。',
      date: '2024-09-15',
      category: '经济数据',
      tag: 'data',
      source: '国家统计局'
    }
  ];
  
  // 为了演示，生成更多模拟数据
  const extraNews: NewsItem[] = [];
  for (let i = 1; i <= 15; i++) {
    const tags = ['policy', 'data', 'trade'];
    const categories = ['金融政策', '经济数据', '国际贸易', '产业政策', '就业数据'];
    const tag = tags[Math.floor(Math.random() * tags.length)];
    const category = categories[Math.floor(Math.random() * categories.length)];
    
    extraNews.push({
      id: `extra-${i}`,
      title: `${countryCode === 'china' ? '中国' : countryCode === 'usa' ? '美国' : countryCode === 'europe' ? '欧洲' : '日本'}宏观经济新闻示例 ${i}`,
      summary: `这是一条关于${countryCode === 'china' ? '中国' : countryCode === 'usa' ? '美国' : countryCode === 'europe' ? '欧洲' : '日本'}经济的模拟新闻，用于展示新闻详情模态框的效果。`,
      date: `2024-09-${Math.floor(Math.random() * 30) + 1}`,
      category,
      tag,
      source: '经济观察报'
    });
  }
  
  return [...baseNews, ...extraNews];
};

// 获取标签颜色
const getTagColor = (tag: string) => {
  switch (tag) {
    case 'policy':
      return 'blue';
    case 'data':
      return 'green';
    case 'trade':
      return 'orange';
    default:
      return 'default';
  }
};

// 新闻模态框组件
const MacroEconomyNewsModal: React.FC<MacroNewsModalProps> = ({ 
  countryCode, 
  countryName, 
  visible, 
  onClose 
}) => {
  const [newsData, setNewsData] = useState<NewsItem[]>(getMockNewsData(countryCode));
  const [searchText, setSearchText] = useState('');
  const [categoryFilter, setCategoryFilter] = useState<string | null>(null);
  
  // 搜索和筛选逻辑
  const filteredNews = newsData.filter(news => {
    const matchesSearch = !searchText || 
      news.title.toLowerCase().includes(searchText.toLowerCase()) || 
      (news.summary && news.summary.toLowerCase().includes(searchText.toLowerCase()));
    
    const matchesCategory = !categoryFilter || news.category === categoryFilter;
    
    return matchesSearch && matchesCategory;
  });
  
  // 重置筛选
  const resetFilters = () => {
    setSearchText('');
    setCategoryFilter(null);
  };
  
  // 所有可用的分类
  const categories = Array.from(new Set(newsData.map(item => item.category)));
  
  return (
    <Modal
      title={
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Title level={4}>{countryName}宏观经济新闻</Title>
          <span style={{ fontSize: '14px', color: '#8c8c8c' }}>共 {filteredNews.length} 条新闻</span>
        </div>
      }
      open={visible}
      onCancel={onClose}
      footer={null}
      width={800}
      style={{ top: 20 }}
    >
      <div style={{ marginBottom: 16 }}>
        <Space style={{ width: '100%', justifyContent: 'space-between' }}>
          <Space>
            <Input
              prefix={<SearchOutlined />}
              placeholder="搜索新闻关键词"
              value={searchText}
              onChange={e => setSearchText(e.target.value)}
              style={{ width: 220 }}
              allowClear
            />
            <Select
              placeholder="选择分类"
              style={{ width: 150 }}
              value={categoryFilter}
              onChange={value => setCategoryFilter(value)}
              allowClear
            >
              {categories.map(cat => (
                <Option key={cat} value={cat}>{cat}</Option>
              ))}
            </Select>
          </Space>
          <Button 
            icon={<FilterOutlined />} 
            onClick={resetFilters}
          >
            重置筛选
          </Button>
        </Space>
      </div>
      
      <Divider style={{ margin: '12px 0' }} />
      
      <List
        itemLayout="vertical"
        size="large"
        pagination={{
          onChange: page => {
            console.log(page);
            // 如果有分页加载逻辑，可以在这里处理
          },
          pageSize: 5,
        }}
        dataSource={filteredNews}
        renderItem={item => (
          <List.Item
            key={item.id}
            actions={[
              <Space>
                <CalendarOutlined />
                {item.date}
              </Space>,
              item.source && <span>来源: {item.source}</span>
            ]}
            extra={
              <Tag color={getTagColor(item.tag)}>
                {item.category}
              </Tag>
            }
          >
            <List.Item.Meta
              title={<a href="#">{item.title}</a>}
              description={item.summary}
            />
          </List.Item>
        )}
      />
    </Modal>
  );
};

export default MacroEconomyNewsModal;