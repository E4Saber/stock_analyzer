// src/features/stock/pages/StockListPage.tsx
import React, { useState, useEffect } from 'react';
import { 
  Input, 
  Table, 
  Tag, 
  Button, 
  Space, 
  Select, 
  Tooltip, 
  Pagination, 
  Tabs,
  Card,
  Row,
  Col
} from 'antd';
import { 
  SearchOutlined, 
  FilterOutlined, 
  SortAscendingOutlined, 
  SortDescendingOutlined, 
  StarOutlined, 
  StarFilled,
  InfoCircleOutlined,
  ArrowUpOutlined,
  ArrowDownOutlined
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import './StockListPage.css';

const { Search } = Input;

// 模拟股票数据接口
interface StockData {
  id: string;
  name: string;
  code: string;
  valueScore: number; // 价投分
  riskLevel: number; // 风险度 (1-5)
  changePercent: number; // 涨跌幅
  changeAmount: number; // 涨跌额
  price: number; // 当前价格
  netFlow: {
    day3: number;
    day5: number;
    day10: number;
    day15: number;
    day30: number;
  };
  industry: string; // 所属行业
  pe: number; // 市盈率
  pb: number; // 市净率
  isFavorite: boolean; // 是否收藏
}

// 表格列定义
const getColumns = (handleFavorite: (stockId: string) => void, navigate: any) => [
  {
    title: '收藏',
    dataIndex: 'isFavorite',
    key: 'isFavorite',
    width: 80,
    render: (_: any, record: StockData) => (
      <Button 
        type="text" 
        icon={record.isFavorite ? <StarFilled style={{ color: '#faad14' }} /> : <StarOutlined />} 
        onClick={(e) => {
          e.stopPropagation();
          handleFavorite(record.id);
        }}
      />
    ),
  },
  {
    title: '名称',
    dataIndex: 'name',
    key: 'name',
    sorter: (a: StockData, b: StockData) => a.name.localeCompare(b.name),
    render: (text: string, record: StockData) => (
      <a onClick={() => navigate(`/stock/details/${record.code}`)}>{text}</a>
    ),
  },
  {
    title: '代码',
    dataIndex: 'code',
    key: 'code',
    width: 120,
  },
  {
    title: <span>价投分 <Tooltip title="价值投资综合评分，越高越具投资价值"><InfoCircleOutlined /></Tooltip></span>,
    dataIndex: 'valueScore',
    key: 'valueScore',
    sorter: (a: StockData, b: StockData) => a.valueScore - b.valueScore,
    width: 100,
    render: (score: number) => {
      let color = 'green';
      if (score < 60) {
        color = 'red';
      } else if (score < 80) {
        color = 'orange';
      }
      return <Tag color={color}>{score}</Tag>;
    }
  },
  {
    title: <span>风险度 <Tooltip title="1-5级，数字越高风险越大"><InfoCircleOutlined /></Tooltip></span>,
    dataIndex: 'riskLevel',
    key: 'riskLevel',
    sorter: (a: StockData, b: StockData) => a.riskLevel - b.riskLevel,
    width: 100,
    render: (level: number) => {
      const colors = ['green', 'lime', 'gold', 'orange', 'red'];
      return <Tag color={colors[level-1]}>{level}级</Tag>;
    }
  },
  {
    title: '现价',
    dataIndex: 'price',
    key: 'price',
    sorter: (a: StockData, b: StockData) => a.price - b.price,
    width: 100,
  },
  {
    title: '涨跌幅',
    dataIndex: 'changePercent',
    key: 'changePercent',
    sorter: (a: StockData, b: StockData) => a.changePercent - b.changePercent,
    width: 100,
    render: (percent: number) => {
      const isPositive = percent >= 0;
      return (
        <span style={{ color: isPositive ? '#52c41a' : '#f5222d' }}>
          {isPositive ? <ArrowUpOutlined /> : <ArrowDownOutlined />}
          {Math.abs(percent).toFixed(2)}%
        </span>
      );
    }
  },
  {
    title: '涨跌额',
    dataIndex: 'changeAmount',
    key: 'changeAmount',
    sorter: (a: StockData, b: StockData) => a.changeAmount - b.changeAmount,
    width: 100,
    render: (amount: number) => {
      const isPositive = amount >= 0;
      return (
        <span style={{ color: isPositive ? '#52c41a' : '#f5222d' }}>
          {isPositive ? '+' : ''}
          {amount.toFixed(2)}
        </span>
      );
    }
  },
  {
    title: '行业',
    dataIndex: 'industry',
    key: 'industry',
    filters: [
      { text: '科技', value: '科技' },
      { text: '金融', value: '金融' },
      { text: '消费', value: '消费' },
      { text: '医药', value: '医药' },
      { text: '能源', value: '能源' },
    ],
    onFilter: (value: string, record: StockData) => record.industry === value,
    width: 120,
  },
  {
    title: '市盈率',
    dataIndex: 'pe',
    key: 'pe',
    sorter: (a: StockData, b: StockData) => a.pe - b.pe,
    width: 100,
  },
  {
    title: '市净率',
    dataIndex: 'pb',
    key: 'pb',
    sorter: (a: StockData, b: StockData) => a.pb - b.pb,
    width: 100,
  },
  {
    title: <div>净流入/流出 <Tooltip title="资金净流入/流出情况"><InfoCircleOutlined /></Tooltip></div>,
    children: [
      {
        title: '3日',
        dataIndex: ['netFlow', 'day3'],
        key: 'netFlow3',
        width: 100,
        render: (value: number) => renderNetFlow(value),
        sorter: (a: StockData, b: StockData) => a.netFlow.day3 - b.netFlow.day3,
      },
      {
        title: '5日',
        dataIndex: ['netFlow', 'day5'],
        key: 'netFlow5',
        width: 100,
        render: (value: number) => renderNetFlow(value),
        sorter: (a: StockData, b: StockData) => a.netFlow.day5 - b.netFlow.day5,
      },
      {
        title: '10日',
        dataIndex: ['netFlow', 'day10'],
        key: 'netFlow10',
        width: 100,
        render: (value: number) => renderNetFlow(value),
        sorter: (a: StockData, b: StockData) => a.netFlow.day10 - b.netFlow.day10,
      },
      {
        title: '15日',
        dataIndex: ['netFlow', 'day15'],
        key: 'netFlow15',
        width: 100,
        render: (value: number) => renderNetFlow(value),
        sorter: (a: StockData, b: StockData) => a.netFlow.day15 - b.netFlow.day15,
      },
      {
        title: '30日',
        dataIndex: ['netFlow', 'day30'],
        key: 'netFlow30',
        width: 100,
        render: (value: number) => renderNetFlow(value),
        sorter: (a: StockData, b: StockData) => a.netFlow.day30 - b.netFlow.day30,
      },
    ],
  },
];

// 渲染资金净流入/流出
const renderNetFlow = (value: number) => {
  // 转换为亿元显示
  const displayValue = (value / 100000000).toFixed(2);
  const isPositive = value >= 0;
  return (
    <span style={{ color: isPositive ? '#52c41a' : '#f5222d' }}>
      {isPositive ? '+' : ''}
      {displayValue}亿
    </span>
  );
};

// 生成模拟数据
const generateMockData = (): StockData[] => {
  const industries = ['科技', '金融', '消费', '医药', '能源', '制造', '材料', '地产'];
  const names = [
    '阿里巴巴', '腾讯控股', '贵州茅台', '平安保险', '宁德时代', 
    '招商银行', '格力电器', '中国石油', '恒瑞医药', '五粮液',
    '美的集团', '中国中免', '伊利股份', '万华化学', '海康威视',
    '中国平安', '隆基绿能', '中兴通讯', '比亚迪', '华为科技'
  ];
  
  const mockData: StockData[] = [];
  
  for (let i = 0; i < 100; i++) {
    const random = Math.random();
    const nameIndex = i % names.length;
    const industry = industries[Math.floor(Math.random() * industries.length)];
    const changePercent = (random * 10 - 5).toFixed(2);
    const price = Math.floor(100 + random * 1900);
    const changeAmount = price * parseFloat(changePercent) / 100;
    
    mockData.push({
      id: `stock-${i}`,
      name: names[nameIndex],
      code: `${600000 + i}`,
      valueScore: Math.floor(40 + random * 60),
      riskLevel: Math.floor(1 + random * 5),
      changePercent: parseFloat(changePercent),
      changeAmount: parseFloat(changeAmount.toFixed(2)),
      price: price,
      netFlow: {
        day3: Math.floor(random * 2000000000 - 1000000000),
        day5: Math.floor(random * 3000000000 - 1500000000),
        day10: Math.floor(random * 5000000000 - 2500000000),
        day15: Math.floor(random * 7000000000 - 3500000000),
        day30: Math.floor(random * 10000000000 - 5000000000),
      },
      industry: industry,
      pe: parseFloat((5 + random * 45).toFixed(2)),
      pb: parseFloat((0.5 + random * 9.5).toFixed(2)),
      isFavorite: false
    });
  }
  
  return mockData;
};

// 热门搜索标签
const hotSearchTags = ['贵州茅台', '宁德时代', '腾讯控股', '隆基绿能', '中国平安', '华为科技'];

const { TabPane } = Tabs;

const StockListPage: React.FC = () => {
  const [stocks, setStocks] = useState<StockData[]>([]);
  const [filteredStocks, setFilteredStocks] = useState<StockData[]>([]);
  const [searchText, setSearchText] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);
  const [activeTab, setActiveTab] = useState<string>('all');
  const navigate = useNavigate();
  
  // 初始化数据
  useEffect(() => {
    // 模拟API请求
    setTimeout(() => {
      const data = generateMockData();
      setStocks(data);
      setFilteredStocks(data);
      setLoading(false);
    }, 500);
  }, []);
  
  // 处理搜索
  const handleSearch = (value: string) => {
    setSearchText(value);
    if (!value) {
      setFilteredStocks(stocks);
      return;
    }
    
    const filtered = stocks.filter(
      stock => 
        stock.name.includes(value) || 
        stock.code.includes(value)
    );
    setFilteredStocks(filtered);
  };
  
  // 处理快速搜索标签点击
  const handleTagClick = (tag: string) => {
    setSearchText(tag);
    handleSearch(tag);
  };
  
  // 处理收藏
  const handleFavorite = (stockId: string) => {
    const updatedStocks = stocks.map(stock => 
      stock.id === stockId ? { ...stock, isFavorite: !stock.isFavorite } : stock
    );
    setStocks(updatedStocks);
    
    // 更新过滤后的列表
    if (searchText) {
      const filtered = updatedStocks.filter(
        stock => 
          stock.name.includes(searchText) || 
          stock.code.includes(searchText)
      );
      setFilteredStocks(filtered);
    } else {
      setFilteredStocks(updatedStocks);
    }
  };
  
  // 处理Tab切换
  const handleTabChange = (key: string) => {
    setActiveTab(key);
    
    if (key === 'all') {
      // 全部股票
      setFilteredStocks(stocks);
    } else if (key === 'favorites') {
      // 收藏的股票
      setFilteredStocks(stocks.filter(stock => stock.isFavorite));
    } else if (key === 'rising') {
      // 上涨的股票
      setFilteredStocks(stocks.filter(stock => stock.changePercent > 0));
    } else if (key === 'falling') {
      // 下跌的股票
      setFilteredStocks(stocks.filter(stock => stock.changePercent < 0));
    } else if (key === 'highValue') {
      // 高价值股票（价投分 >= 80）
      setFilteredStocks(stocks.filter(stock => stock.valueScore >= 80));
    } else if (key === 'lowRisk') {
      // 低风险股票（风险等级 <= 2）
      setFilteredStocks(stocks.filter(stock => stock.riskLevel <= 2));
    }
  };
  
  // 获取表格列定义
  const columns = getColumns(handleFavorite, navigate);
  
  return (
    <div className="stock-list-page">
      
      {/* 搜索区域 */}
      <Card className="stock-search-section">
        <Row>
          <Col span={24}>
            <Search
                placeholder="输入股票名称或代码搜索"
                allowClear
                enterButton={<><SearchOutlined /> 搜索</>}
                size="large"
                onSearch={handleSearch}
            />
          </Col>
          <Col span={24}>
            <div className="hot-search-tags">
              <span className="tag-label">热门搜索: </span>
              {hotSearchTags.map(tag => (
                <Tag 
                  key={tag} 
                  color="blue" 
                  onClick={() => handleTagClick(tag)}
                  style={{ cursor: 'pointer' }}
                >
                  {tag}
                </Tag>
              ))}
            </div>
          </Col>
        </Row>
      </Card>
      
      {/* 表格展示区域 */}
      <Card className="stock-table-section">
        <Tabs 
          activeKey={activeTab} 
          onChange={handleTabChange}
          className="stock-tabs"
        >
          <TabPane tab="全部股票" key="all" />
          <TabPane tab="我的收藏" key="favorites" />
          <TabPane tab="上涨股票" key="rising" />
          <TabPane tab="下跌股票" key="falling" />
          <TabPane tab="高价值股" key="highValue" />
          <TabPane tab="低风险股" key="lowRisk" />
        </Tabs>
        
        <div className="table-actions">
          <Space>
            <Select
              placeholder="选择行业筛选"
              style={{ width: 150 }}
              allowClear
              onChange={(value) => {
                if (!value) {
                  // 清除筛选
                  if (activeTab === 'all') {
                    setFilteredStocks(stocks);
                  } else {
                    handleTabChange(activeTab);
                  }
                } else {
                  // 应用行业筛选
                  const industryFiltered = filteredStocks.filter(
                    stock => stock.industry === value
                  );
                  setFilteredStocks(industryFiltered);
                }
              }}
            >
              <Select.Option value="科技">科技</Select.Option>
              <Select.Option value="金融">金融</Select.Option>
              <Select.Option value="消费">消费</Select.Option>
              <Select.Option value="医药">医药</Select.Option>
              <Select.Option value="能源">能源</Select.Option>
              <Select.Option value="制造">制造</Select.Option>
              <Select.Option value="材料">材料</Select.Option>
              <Select.Option value="地产">地产</Select.Option>
            </Select>
            
            <Tooltip title="按价投分降序">
              <Button 
                icon={<SortDescendingOutlined />} 
                onClick={() => {
                  const sorted = [...filteredStocks].sort((a, b) => b.valueScore - a.valueScore);
                  setFilteredStocks(sorted);
                }}
              >
                价值排序
              </Button>
            </Tooltip>
            
            <Tooltip title="按涨跌幅降序">
              <Button 
                icon={<SortDescendingOutlined />} 
                onClick={() => {
                  const sorted = [...filteredStocks].sort((a, b) => b.changePercent - a.changePercent);
                  setFilteredStocks(sorted);
                }}
              >
                涨幅排序
              </Button>
            </Tooltip>
          </Space>
          
          <div>
            <span>共 {filteredStocks.length} 只股票</span>
          </div>
        </div>
        
        <Table 
          columns={columns}
          dataSource={filteredStocks}
          rowKey="id"
          loading={loading}
          pagination={{
            defaultPageSize: 20,
            showSizeChanger: true,
            pageSizeOptions: ['10', '20', '50', '100'],
            showTotal: (total) => `共 ${total} 条记录`,
          }}
          scroll={{ x: 1500 }}
          size="middle"
          onRow={(record) => {
            return {
              onClick: () => navigate(`/stock/details/${record.code}`),
              style: { cursor: 'pointer' }
            };
          }}
        />
      </Card>
    </div>
  );
};

export default StockListPage;