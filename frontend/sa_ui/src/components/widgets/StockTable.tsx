// src/components/widgets/StockTable.tsx
import React from 'react';
import { Table, Tag } from 'antd';
import { ArrowUpOutlined, ArrowDownOutlined } from '@ant-design/icons';
import { Link } from 'react-router-dom';
import { HotStock } from '../../types/market';
import { formatLargeNumber } from '../../utils/numberFormatter';

interface StockTableProps {
  stocks: HotStock[];
  loading?: boolean;
  showAmount?: boolean;
  showVolume?: boolean;
  showTurnover?: boolean;
}

const StockTable: React.FC<StockTableProps> = ({ 
  stocks, 
  loading = false,
  showAmount = true,
  showVolume = true,
  showTurnover = true
}) => {
  // Define base columns
  const baseColumns = [
    {
      title: '代码',
      dataIndex: 'code',
      key: 'code',
      render: (text: string) => <Link to={`/stocks/${text}`} className="stock-table-link">{text}</Link>,
      width: 100,
    },
    {
      title: '名称',
      dataIndex: 'name',
      key: 'name',
      render: (text: string, record: HotStock) => (
        <Link to={`/stocks/${record.code}`} className="stock-table-link">{text}</Link>
      ),
      width: 120,
    },
    {
      title: '价格',
      dataIndex: 'price',
      key: 'price',
      align: 'right' as const,
      render: (price: number) => price.toFixed(2),
      width: 100,
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
      width: 120,
    }
  ];

  // Optional columns based on props
  const optionalColumns = [];

  if (showVolume && stocks.some(stock => stock.volume !== undefined)) {
    optionalColumns.push({
      title: '成交量',
      dataIndex: 'volume',
      key: 'volume',
      align: 'right' as const,
      render: (volume?: number) => volume ? formatLargeNumber(volume) : '-',
      width: 120,
    });
  }

  if (showAmount && stocks.some(stock => stock.amount !== undefined)) {
    optionalColumns.push({
      title: '成交额',
      dataIndex: 'amount',
      key: 'amount',
      align: 'right' as const,
      render: (amount?: number) => amount ? formatLargeNumber(amount) : '-',
      width: 120,
    });
  }

  if (showTurnover && stocks.some(stock => stock.turnover_rate !== undefined)) {
    optionalColumns.push({
      title: '换手率',
      dataIndex: 'turnover_rate',
      key: 'turnover_rate',
      align: 'right' as const,
      render: (turnover_rate?: number) => turnover_rate ? `${turnover_rate.toFixed(2)}%` : '-',
      width: 100,
    });
  }

  // Combine all columns
  const columns = [...baseColumns, ...optionalColumns];

  return (
    <Table
      columns={columns}
      dataSource={stocks.map(stock => ({ ...stock, key: stock.code }))}
      pagination={{ pageSize: 10 }}
      loading={loading}
      size="middle"
      scroll={{ x: 'max-content' }}
    />
  );
};

export default StockTable;