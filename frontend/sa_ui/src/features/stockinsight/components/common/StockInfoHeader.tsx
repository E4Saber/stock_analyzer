// src/components/StockInfoHeader.tsx
import React from 'react';
import { Row, Col, Typography, Space, Tag, Card, Tooltip } from 'antd';
import { RiseOutlined, FallOutlined, QuestionCircleOutlined } from '@ant-design/icons';
import { formatLargeNumber } from '../../../../shared/utils/numberFormatter';

const { Text, Title } = Typography;

interface StockInfoProps {
  stock: {
    name: string;
    code: string;
    current: number;
    change: number;
    change_percent: number;
    open: number;
    high: number;
    low: number;
    prevClose?: number;
    volume: number;
    amount?: number;
    pe_ttm: number;
    pe_lyr: number;
    pb: number;
    ps_ttm?: number;
    market_cap: number;
    circulating_market_cap?: number;
    total_shares?: number;
    circulating_shares?: number;
    turnover: number;
    amplitude: number;
    high_52w?: number;
    low_52w?: number;
    roa?: number;
    roe?: number;
    volume_ratio?: number;
    eps_ttm?: number;
    eps_lyr?: number;
    dividend?: number;
    dividend_yield?: number;
    forecast_pe?: number;
    forecast_eps?: number;
    industry?: string;
  };
}

// 指标说明信息
const tooltipExplanations = {
  turnover: "换手率是指在一定时间内市场中股票转手买卖的频率，计算方式为成交量/流通股本",
  volume_ratio: "量比是指当日成交总手数与近期平均成交量的比值",
  roa: "总资产收益率，表示企业的整体获利能力",
  roe: "净资产收益率，表示股东权益的收益水平",
  market_cap: "总市值是指一家上市公司的所有已发行股票的市场价值总和",
};

const StockInfoHeader: React.FC<StockInfoProps> = ({ stock }) => {
  const isUp = stock.change >= 0;
  const colorStyle = isUp ? { color: '#cf1322' } : { color: '#3f8600' };

  // 渲染指标名称
  const renderLabel = (label: string, key: string, suffix?: string) => {
    const hasTooltip = ['turnover', 'roa', 'roe', 'volume_ratio', 'market_cap'].includes(key);
    const hasSuperscript = suffix !== undefined;
    
    return (
      <Text type="secondary" style={{ display: 'flex', alignItems: 'center' }}>
        {label}
        {hasSuperscript && (
          <sup style={{ fontSize: '10px', marginLeft: '2px' }}>{suffix}</sup>
        )}
        {hasTooltip && (
          <Tooltip title={tooltipExplanations[key]}>
            <QuestionCircleOutlined style={{ fontSize: '14px', marginLeft: '4px', color: '#bfbfbf' }} />
          </Tooltip>
        )}
      </Text>
    );
  };

  // 两行显示的数据项
  const infoItems = [
    [
      { label: '最高', value: stock.high.toFixed(2), key: 'high' },
      { label: '今开', value: stock.open.toFixed(2), key: 'open' },
      { label: '成交量', value: formatLargeNumber(stock.volume) + '万', key: 'volume' },
    ],
    [
      { label: '最低', value: stock.low.toFixed(2), key: 'low' },
      { label: '昨收', value: stock.prevClose?.toFixed(2) || '-', key: 'prevClose' },
      { label: '成交额', value: (stock.amount ? stock.amount / 100000000 : '-') + '亿', key: 'amount' },
    ],
    [
      { label: '换手率', value: (stock.turnover?.toFixed(2) || '-') + '%', key: 'turnover' },
      { label: '市盈率', suffix: 'TTM', value: stock.pe_ttm?.toFixed(2) || '-', key: 'pe_ttm' },
      { label: '总市值', suffix: 'USD', value: formatLargeNumber(stock.market_cap / 100000000) + '亿', key: 'market_cap' },
    ],
    [
      { label: '振幅', value: (stock.amplitude?.toFixed(2) || '-') + '%', key: 'amplitude' },
      { label: '市盈率', suffix: 'LYR', value: stock.pe_lyr?.toFixed(2) || '-', key: 'pe_lyr' },
      { label: '流通市值', value: formatLargeNumber((stock.circulating_market_cap || 0) / 100000000) + '亿', key: 'circulating_market_cap' },
    ],
    [
      { label: '52周最高', value: stock.high_52w?.toFixed(2) || '-', key: 'high_52w' },
      { label: '市净率', value: stock.pb?.toFixed(2) || '-', key: 'pb' },
      { label: '总股本', value: formatLargeNumber((stock.total_shares || 0) / 100000000) + '亿', key: 'total_shares' },
    ],
    [
      { label: '52周最低', value: stock.low_52w?.toFixed(2) || '-', key: 'low_52w' },
      { label: '市销率', suffix: 'TTM', value: stock.ps_ttm?.toFixed(2) || '3.37', key: 'ps_ttm' },
      { label: '流通股本', value: formatLargeNumber((stock.circulating_shares || 0) / 100000000) + '亿', key: 'circulating_shares' },
    ],
    [
      { label: 'ROA', value: (stock.roa?.toFixed(2) || '-') + '%', key: 'roa' },
      { label: '每股收益', suffix: 'TTM', value: stock.eps_ttm?.toFixed(2) || '-', key: 'eps_ttm' },
      { label: '股息', value: stock.dividend?.toFixed(2) || '-', key: 'dividend' },
    ],
    [
      { label: 'ROE', value: (stock.roe?.toFixed(2) || '-') + '%', key: 'roe' },
      { label: '每股收益', suffix: 'LYR', value: stock.eps_lyr?.toFixed(2) || '-', key: 'eps_lyr' },
      { label: '股息收益率', value: (stock.dividend_yield?.toFixed(2) || '-') + '%', key: 'dividend_yield' },
    ],
    [
      { label: '量比', value: stock.volume_ratio?.toFixed(2) || '-', key: 'volume_ratio' },
      { label: '预测市盈率', value: stock.forecast_pe?.toFixed(2) || '-', key: 'forecast_pe' },
      { label: '预测每股收益', value: stock.forecast_eps?.toFixed(3) || '-', key: 'forecast_eps' },
    ],
  ];

  return (
    <Card bordered={false} style={{ marginBottom: 16 }}>
      <Row gutter={[24, 0]}>
        {/* 股票名称和当前价格 */}
        <Col xs={24} md={8}>
          <Space direction="vertical" size={8} style={{ width: '100%' }}>
            <Title level={4} style={{ margin: 0 }}>
              {stock.name} <Text type="secondary">{stock.code}</Text>
            </Title>
            <Space align="baseline">
              <Text style={{ ...colorStyle, fontSize: 32, fontWeight: 'bold' }}>
                {stock.current.toFixed(2)}
              </Text>
              <Space>
                <Tag color={isUp ? 'red' : 'green'} style={{ fontSize: 14 }}>
                  {isUp ? <RiseOutlined /> : <FallOutlined />} {isUp ? '+' : ''}{stock.change.toFixed(2)}
                </Tag>
                <Tag color={isUp ? 'red' : 'green'} style={{ fontSize: 14 }}>
                  {isUp ? '+' : ''}{stock.change_percent.toFixed(2)}%
                </Tag>
              </Space>
            </Space>
          </Space>
        </Col>

        {/* 股票信息表格 */}
        <Col xs={24} md={16}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '8px 16px' }}>
            {infoItems.flat().map((item, index) => (
              <div key={index} style={{ display: 'flex', justifyContent: 'space-between' }}>
                {renderLabel(item.label, item.key, item.suffix)}
                <Text strong>{item.value}</Text>
              </div>
            ))}
          </div>
        </Col>
      </Row>
    </Card>
  );
};

export default StockInfoHeader;