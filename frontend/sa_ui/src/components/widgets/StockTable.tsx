// src/components/widgets/StockTable.tsx
import React from 'react';
import { Table, Tag } from 'antd';
import { ArrowUpOutlined, ArrowDownOutlined } from '@ant-design/icons';
import { Link } from 'react-router-dom';
import { HotStock } from '../../types/market';

interface StockTableProps {
  stocks: HotStock[];
  loading?: boolean;
}

const StockTable: React.FC<StockTableProps> = ({ stocks, loading = false }) => {
  const columns = [
    {
      title: '代码',
      dataIndex: 'code',
      key: 'code',
      render: (text: string) => <Link to={`/stocks/${text}`}>{text}</Link>,
    },
    {
      title: '名称',
      dataIndex: 'name',
      key: 'name',
      render: (text: string, record: HotStock) => (
        <Link to={`/stocks/${record.code}`}>{text}</Link>
      ),
    },
    {
      title: '价格',
      dataIndex: 'price',
      key: 'price',
      align: 'right' as const,
      render: (price: number) => price.toFixed(2),
    },
    {
      title: '涨跌幅',
      dataIndex: 'change_pct',
      key: 'change_pct',
      align: 'right' as const,
      render: (change_pct: number) => {
        const isPositive = change_pct >= 0;
        const color = isPositive ? '#3f8600' : '#cf1322';
        const icon = isPositive ? <ArrowUpOutlined /> : <ArrowDownOutlined />;
        
        return (
          <Tag color={isPositive ? 'green' : 'red'} style={{ minWidth: '80px', textAlign: 'center' }}>
            {icon} {isPositive ? '+' : ''}{change_pct.toFixed(2)}%
          </Tag>
        );
      },
      sorter: (a: HotStock, b: HotStock) => a.change_pct - b.change_pct,
    },
  ];

  return (
    <Table
      columns={columns}
      dataSource={stocks.map(stock => ({ ...stock, key: stock.code }))}
      pagination={{ pageSize: 10 }}
      loading={loading}
      size="middle"
    />
  );
};

export default StockTable;