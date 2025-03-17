// src/components/charts/EnhancedIndexChart.tsx
import React, { useEffect, useState, useRef } from 'react';
import ReactECharts from 'echarts-for-react';
import { 
  Card, Radio, Spin, Empty, Dropdown, Button, Space, Tabs,
  Row, Col, Statistic, Typography, DatePicker, Tooltip
} from 'antd';
import { 
  LineChartOutlined, BarChartOutlined, CandlestickOutlined,
  DownOutlined, ReloadOutlined, FullscreenOutlined, 
  CaretUpOutlined, CaretDownOutlined 
} from '@ant-design/icons';
import { getStockKline } from '../../services/stockService';
import { IndexData } from '../../types/market';
import type { TabsProps } from 'antd';
import type { RadioChangeEvent } from 'antd';
import type { EChartsOption } from 'echarts-for-react';
import moment from 'moment';

const { Title, Text } = Typography;
const { RangePicker } = DatePicker;

interface EnhancedIndexChartProps {
  indices: IndexData[];
  height?: number;
  showHeader?: boolean;
  showTitle?: boolean;
  defaultPeriod?: string;
  defaultChartType?: 'line' | 'candle' | 'bar';
  fullWidth?: boolean;
}

const EnhancedIndexChart: React.FC<EnhancedIndexChartProps> = ({ 
  indices,
  height = 400,
  showHeader = true, 
  showTitle = true,
  defaultPeriod = 'day',
  defaultChartType = 'line',
  fullWidth = false
}) => {
  const [selectedIndex, setSelectedIndex] = useState<string>(indices[0]?.code || '');
  const [klineData, setKlineData] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [period, setPeriod] = useState<string>(defaultPeriod);
  const [chartType, setChartType] = useState<'line' | 'candle' | 'bar'>(defaultChartType);
  const [compareMode, setCompareMode] = useState<boolean>(false);
  const [comparedIndices, setComparedIndices] = useState<string[]>([]);
  const [comparedData, setComparedData] = useState<Record<string, any[]>>({});
  const [dateRange, setDateRange] = useState<[moment.Moment, moment.Moment] | null>(null);
  const [activeTab, setActiveTab] = useState<string>('chart');
  const [indicators, setIndicators] = useState<string[]>(['ma']);
  const [isFullscreen, setIsFullscreen] = useState<boolean>(false);
  const chartRef = useRef<any>(null);

  // 获取指数数据
  useEffect(() => {
    if (!selectedIndex) return;
    
    const fetchKlineData = async () => {
      setLoading(true);
      try {
        // 将周期映射到API需要的格式
        const periodMap: Record<string, string> = {
          'day': '1d',
          'week': '1wk',
          'month': '1mo',
          '3month': '3mo',
          '6month': '6mo',
          'year': '1y',
          '5year': '5y'
        };
        
        const apiPeriod = periodMap[period] || '1d';
        
        const response = await getStockKline(selectedIndex, apiPeriod, chartType);
        
        // 根据图表类型转换数据格式
        let chartData;
        if (chartType === 'line') {
          chartData = response.data.map((item: any) => [
            item.date,
            item.close
          ]);
        } else if (chartType === 'candle') {
          chartData = response.data.map((item: any) => [
            item.date,
            item.open,
            item.close,
            item.low,
            item.high,
            item.volume
          ]);
        } else if (chartType === 'bar') {
          chartData = response.data.map((item: any) => [
            item.date,
            item.volume,
            item.close > item.open ? 1 : -1  // 用于确定柱状图颜色
          ]);
        }
        
        // 如果设置了日期范围，过滤数据
        if (dateRange && dateRange[0] && dateRange[1]) {
          const startDate = dateRange[0].format('YYYY-MM-DD');
          const endDate = dateRange[1].format('YYYY-MM-DD');
          
          chartData = chartData.filter((item: any) => {
            const itemDate = item[0];
            return itemDate >= startDate && itemDate <= endDate;
          });
        }
        
        setKlineData(chartData);
      } catch (error) {
        console.error('获取K线数据失败:', error);
        setKlineData([]);
      } finally {
        setLoading(false);
      }
    };
    
    fetchKlineData();
    
    // 如果启用比较模式，获取比较数据
    if (compareMode && comparedIndices.length > 0) {
      fetchComparedData();
    }
  }, [selectedIndex, period, chartType, dateRange, compareMode, comparedIndices]);
  
  // 获取比较数据
  const fetchComparedData = async () => {
    const periodMap: Record<string, string> = {
      'day': '1d',
      'week': '1wk',
      'month': '1mo',
      '3month': '3mo',
      '6month': '6mo',
      'year': '1y',
      '5year': '5y'
    };
    
    const apiPeriod = periodMap[period] || '1d';
    const newComparedData: Record<string, any[]> = {};
    
    // 使用Promise.all并行获取所有比较指数的数据
    await Promise.all(
      comparedIndices.map(async (code) => {
        try {
          const response = await getStockKline(code, apiPeriod, 'line');
          
          // 标准化数据，只保留日期和收盘价
          const chartData = response.data.map((item: any) => [
            item.date,
            item.close
          ]);
          
          // 如果设置了日期范围，过滤数据
          if (dateRange && dateRange[0] && dateRange[1]) {
            const startDate = dateRange[0].format('YYYY-MM-DD');
            const endDate = dateRange[1].format('YYYY-MM-DD');
            
            newComparedData[code] = chartData.filter((item: any) => {
              const itemDate = item[0];
              return itemDate >= startDate && itemDate <= endDate;
            });
          } else {
            newComparedData[code] = chartData;
          }
        } catch (error) {
          console.error(`获取比较数据失败 (${code}):`, error);
          newComparedData[code] = [];
        }
      })
    );
    
    setComparedData(newComparedData);
  };

  // 处理指数选择变化
  const handleIndexChange = (e: RadioChangeEvent) => {
    setSelectedIndex(e.target.value);
  };

  // 处理周期选择变化
  const handlePeriodChange = (e: RadioChangeEvent) => {
    setPeriod(e.target.value);
  };
  
  // 处理图表类型变化
  const handleChartTypeChange = (type: 'line' | 'candle' | 'bar') => {
    setChartType(type);
  };
  
  // 处理比较模式切换
  const handleCompareToggle = () => {
    setCompareMode(!compareMode);
    if (!compareMode) {
      // 默认添加第二个指数作为比较
      if (indices.length > 1) {
        setComparedIndices([indices[1].code]);
      }
    } else {
      // 关闭比较模式
      setComparedIndices([]);
      setComparedData({});
    }
  };
  
  // 处理添加比较指数
  const handleAddCompareIndex = (code: string) => {
    if (!comparedIndices.includes(code)) {
      setComparedIndices([...comparedIndices, code]);
    }
  };
  
  // 处理移除比较指数
  const handleRemoveCompareIndex = (code: string) => {
    setComparedIndices(comparedIndices.filter(item => item !== code));
    
    // 从比较数据中移除
    const newComparedData = { ...comparedData };
    delete newComparedData[code];
    setComparedData(newComparedData);
  };
  
  // 处理日期范围变化
  const handleDateRangeChange = (dates: any) => {
    setDateRange(dates);
  };
  
  // 处理标签页切换
  const handleTabChange = (key: string) => {
    setActiveTab(key);
  };
  
  // 处理指标选择
  const handleIndicatorChange = (indicators: string[]) => {
    setIndicators(indicators);
  };
  
  // 切换全屏模式
  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
  };
  
  // 刷新数据
  const refreshData = () => {
    // 通过重新设置选中的指数来触发数据刷新
    const current = selectedIndex;
    setSelectedIndex('');
    setTimeout(() => {
      setSelectedIndex(current);
    }, 100);
  };

  // 生成图表选项
  const getOption = (): EChartsOption => {
    const selectedIndexInfo = indices.find(i => i.code === selectedIndex);
    const selectedName = selectedIndexInfo?.name || '';
    
    // 基础配置
    const baseOption: EChartsOption = {
      title: showTitle ? {
        text: `${selectedName}${compareMode ? '对比' : ''}走势图`,
        left: 'center',
      } : undefined,
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'cross'
        },
        formatter: (params: any) => {
          // 根据图表类型生成不同的tooltip内容
          if (chartType === 'line') {
            let tooltipText = '';
            
            // 日期信息
            const date = params[0].axisValue;
            tooltipText += `${date}<br/>`;
            
            // 主要指数及比较指数的数据
            params.forEach((param: any) => {
              const marker = param.marker;
              const seriesName = param.seriesName;
              const value = typeof param.value[1] === 'number' 
                ? param.value[1].toFixed(2) 
                : param.value[1];
                
              tooltipText += `${marker}${seriesName}: ${value}<br/>`;
            });
            
            return tooltipText;
          } else if (chartType === 'candle') {
            const param = params[0];
            const date = param.axisValue;
            const values = param.value;
            
            return `
              ${date}<br/>
              开盘: ${values[1]}<br/>
              收盘: ${values[2]}<br/>
              最低: ${values[3]}<br/>
              最高: ${values[4]}<br/>
              成交量: ${values[5]}
            `;
          } else if (chartType === 'bar') {
            const param = params[0];
            const date = param.axisValue;
            const volume = param.value[1];
            const trend = param.value[2] > 0 ? '上涨' : '下跌';
            
            return `${date}<br/>成交量: ${volume}<br/>趋势: ${trend}`;
          }
          
          return '';
        }
      },
      legend: {
        data: [selectedName, ...comparedIndices.map(code => {
          const index = indices.find(i => i.code === code);
          return index?.name || code;
        })],
        type: 'scroll',
        bottom: 10
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '15%',
        top: showTitle ? '15%' : '10%',
        containLabel: true
      },
      toolbox: {
        show: true,
        feature: {
          dataZoom: {
            yAxisIndex: 'none'
          },
          saveAsImage: {}
        }
      },
      dataZoom: [
        {
          type: 'inside',
          start: 0,
          end: 100
        },
        {
          type: 'slider',
          start: 0,
          end: 100
        }
      ],
      xAxis: {
        type: 'category',
        boundaryGap: chartType !== 'line',
        data: klineData.map(item => item[0]),
        axisLine: { lineStyle: { color: '#E0E0E0' } },
        axisLabel: {
          formatter: (value: string) => {
            // 根据周期格式化日期
            if (period === 'day' || period === 'week') {
              return value.substring(5); // 显示月-日
            } else if (period === 'month' || period === '3month') {
              return value.substring(0, 7); // 显示年-月
            } else {
              return value; // 显示完整日期
            }
          }
        }
      },
      yAxis: {
        type: 'value',
        scale: true,
        splitLine: { lineStyle: { color: '#E0E0E0', type: 'dashed' } },
        axisLabel: {
          formatter: (value: number) => {
            return value.toFixed(0);
          }
        }
      }
    };
    
    // 根据图表类型创建不同的系列
    let series = [];
    
    if (chartType === 'line') {
      // 创建主要指数的线图系列
      const mainSeries = {
        name: selectedName,
        type: 'line',
        data: klineData,
        smooth: true,
        lineStyle: {
          color: '#1890ff',
          width: 2
        },
        itemStyle: {
          color: '#1890ff'
        },
        areaStyle: compareMode ? undefined : {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              {
                offset: 0,
                color: 'rgba(24,144,255,0.3)'
              },
              {
                offset: 1,
                color: 'rgba(24,144,255,0.1)'
              }
            ]
          }
        },
        showSymbol: false,
        emphasis: {
          lineStyle: {
            width: 3
          }
        }
      };
      
      series.push(mainSeries);
      
      // 如果启用了比较模式，添加比较指数的系列
      if (compareMode && comparedIndices.length > 0) {
        // 颜色数组，用于不同的比较指数
        const colors = ['#52c41a', '#faad14', '#f5222d', '#722ed1', '#eb2f96'];
        
        comparedIndices.forEach((code, index) => {
          const indexInfo = indices.find(i => i.code === code);
          const indexName = indexInfo?.name || code;
          const color = colors[index % colors.length];
          
          // 只有当有数据时才添加系列
          if (comparedData[code] && comparedData[code].length > 0) {
            series.push({
              name: indexName,
              type: 'line',
              data: comparedData[code],
              smooth: true,
              lineStyle: {
                color: color,
                width: 2
              },
              itemStyle: {
                color: color
              },
              showSymbol: false,
              emphasis: {
                lineStyle: {
                  width: 3
                }
              }
            });
          }
        });
      }
      
      // 添加移动平均线指标
      if (indicators.includes('ma')) {
        // 计算MA5
        const ma5Data = calculateMA(5, klineData);
        series.push({
          name: 'MA5',
          type: 'line',
          data: ma5Data,
          smooth: true,
          lineStyle: {
            opacity: 0.7,
            color: '#8d4bbb'
          },
          showSymbol: false
        });
        
        // 计算MA10
        const ma10Data = calculateMA(10, klineData);
        series.push({
          name: 'MA10',
          type: 'line',
          data: ma10Data,
          smooth: true,
          lineStyle: {
            opacity: 0.7,
            color: '#ff9900'
          },
          showSymbol: false
        });
        
        // 计算MA20
        const ma20Data = calculateMA(20, klineData);
        series.push({
          name: 'MA20',
          type: 'line',
          data: ma20Data,
          smooth: true,
          lineStyle: {
            opacity: 0.7,
            color: '#cc0000'
          },
          showSymbol: false
        });
      }
    } else if (chartType === 'candle') {
      // 创建K线图系列
      series.push({
        name: selectedName,
        type: 'candlestick',
        data: klineData.map(item => [item[1], item[2], item[3], item[4]]), // 开盘、收盘、最低、最高
        itemStyle: {
          color: '#ef232a', // 阳线颜色
          color0: '#14b143', // 阴线颜色
          borderColor: '#ef232a',
          borderColor0: '#14b143'
        },
      });
      
      // 添加成交量图表
      if (klineData.length > 0 && klineData[0].length >= 6) {
        // 创建成交量坐标轴
        baseOption.yAxis = [
          {
            type: 'value',
            name: '指数',
            scale: true,
            splitLine: { lineStyle: { color: '#E0E0E0', type: 'dashed' } },
            position: 'left'
          },
          {
            type: 'value',
            name: '成交量',
            scale: true,
            splitLine: { show: false },
            position: 'right'
          }
        ];
        
        // 添加成交量系列
        series.push({
          name: '成交量',
          type: 'bar',
          yAxisIndex: 1,
          data: klineData.map(item => {
            const volume = item[5];
            const open = item[1];
            const close = item[2];
            // 根据当日涨跌设置颜色
            return {
              value: volume,
              itemStyle: {
                color: close >= open ? '#ef232a' : '#14b143'
              }
            };
          }),
        });
      }
      
      // 添加移动平均线指标
      if (indicators.includes('ma')) {
        // 使用收盘价计算MA5
        const closePrices = klineData.map(item => [item[0], item[2]]);
        const ma5Data = calculateMA(5, closePrices);
        series.push({
          name: 'MA5',
          type: 'line',
          data: ma5Data,
          smooth: true,
          lineStyle: {
            opacity: 0.7,
            color: '#8d4bbb'
          },
          showSymbol: false
        });
        
        // 计算MA10
        const ma10Data = calculateMA(10, closePrices);
        series.push({
          name: 'MA10',
          type: 'line',
          data: ma10Data,
          smooth: true,
          lineStyle: {
            opacity: 0.7,
            color: '#ff9900'
          },
          showSymbol: false
        });
        
        // 计算MA20
        const ma20Data = calculateMA(20, closePrices);
        series.push({
          name: 'MA20',
          type: 'line',
          data: ma20Data,
          smooth: true,
          lineStyle: {
            opacity: 0.7,
            color: '#cc0000'
          },
          showSymbol: false
        });
      }
    } else if (chartType === 'bar') {
      // 创建成交量柱状图系列
      series.push({
        name: '成交量',
        type: 'bar',
        data: klineData.map(item => {
          const volume = item[1];
          const trend = item[2];
          
          return {
            value: volume,
            itemStyle: {
              color: trend > 0 ? '#ef232a' : '#14b143'
            }
          };
        }),
        barWidth: '60%'
      });
    }
    
    return {
      ...baseOption,
      series: series as any[]
    };
  };
  
  // 计算移动平均线
  const calculateMA = (dayCount: number, data: any[]) => {
    const result = [];
    
    for (let i = 0; i < data.length; i++) {
      if (i < dayCount - 1) {
        result.push([data[i][0], '-']);
        continue;
      }
      
      let sum = 0;
      for (let j = 0; j < dayCount; j++) {
        const value = data[i - j][1];
        sum += Number(value);
      }
      
      result.push([
        data[i][0],
        (sum / dayCount).toFixed(2)
      ]);
    }
    
    return result;
  };

  // 生成选项卡内容
  const items: TabsProps['items'] = [
    {
      key: 'chart',
      label: '图表',
      children: (
        <div style={{ height: height - (showHeader ? 70 : 20) }}>
          {loading ? (
            <div style={{ height: '100%', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
              <Spin tip="加载中..." />
            </div>
          ) : klineData.length > 0 ? (
            <ReactECharts 
              option={getOption()} 
              style={{ height: '100%', width: '100%' }} 
              notMerge={true}
              ref={chartRef}
            />
          ) : (
            <Empty 
              description="暂无数据" 
              style={{ height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center' }} 
            />
          )}
        </div>
      ),
    },
    {
      key: 'details',
      label: '详情',
      children: (
        <div style={{ padding: '10px', height: height - (showHeader ? 70 : 20), overflow: 'auto' }}>
          {selectedIndex && indices.find(i => i.code === selectedIndex) && (
            <Row gutter={[16, 16]}>
              <Col span={24}>
                <Title level={4}>{indices.find(i => i.code === selectedIndex)?.name} 详细数据</Title>
              </Col>
              
              {/* 指数基本信息 */}
              <Col xs={24} sm={12} md={8} lg={6}>
                <Card size="small">
                  <Statistic 
                    title="当前点位" 
                    value={indices.find(i => i.code === selectedIndex)?.current || 0} 
                    precision={2}
                    valueStyle={{ color: indices.find(i => i.code === selectedIndex)?.change >= 0 ? '#3f8600' : '#cf1322' }}
                    prefix={indices.find(i => i.code === selectedIndex)?.change >= 0 ? <CaretUpOutlined /> : <CaretDownOutlined />}
                  />
                </Card>
              </Col>
              
              <Col xs={24} sm={12} md={8} lg={6}>
                <Card size="small">
                  <Statistic 
                    title="涨跌幅" 
                    value={indices.find(i => i.code === selectedIndex)?.change_percent || 0} 
                    precision={2}
                    valueStyle={{ color: indices.find(i => i.code === selectedIndex)?.change >= 0 ? '#3f8600' : '#cf1322' }}
                    suffix="%"
                  />
                </Card>
              </Col>
              
              {/* 历史数据表格 */}
              <Col span={24}>
                <Card 
                  title="历史数据" 
                  size="small"
                  extra={
                    <Space>
                      <RangePicker onChange={handleDateRangeChange} />
                    </Space>
                  }
                >
                  {/* 可以添加历史数据表格 */}
                  <div>历史数据表格将在这里显示</div>
                </Card>
              </Col>
            </Row>
          )}
        </div>
      ),
    },
  ];

  return (
    <Card
      style={{ width: fullWidth ? '100%' : 'auto', height: isFullscreen ? '100vh' : 'auto' }}
      className={isFullscreen ? 'fullscreen-chart' : ''}
      title={
        showHeader && (
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Radio.Group value={selectedIndex} onChange={handleIndexChange} buttonStyle="solid">
              {indices.map(index => (
                <Radio.Button key={index.code} value={index.code}>
                  <Tooltip title={`${index.name} ${index.current} (${index.change >= 0 ? '+' : ''}${index.change_percent}%)`}>
                    <span>
                      {index.name}
                      <span style={{ 
                        marginLeft: 5,
                        color: index.change >= 0 ? '#3f8600' : '#cf1322'
                      }}>
                        {index.change >= 0 ? '+' : ''}{index.change_percent}%
                      </span>
                    </span>
                  </Tooltip>
                </Radio.Button>
              ))}
            </Radio.Group>
            
            <Space>
              {/* 图表类型切换 */}
              <Radio.Group value={chartType} onChange={(e) => handleChartTypeChange(e.target.value)}>
                <Tooltip title="折线图">
                  <Radio.Button value="line"><LineChartOutlined /></Radio.Button>
                </Tooltip>
                <Tooltip title="K线图">
                  <Radio.Button value="candle"><CandlestickOutlined /></Radio.Button>
                </Tooltip>
                <Tooltip title="成交量">
                  <Radio.Button value="bar"><BarChartOutlined /></Radio.Button>
                </Tooltip>
              </Radio.Group>
              
              {/* 周期选择 */}
              <Radio.Group value={period} onChange={handlePeriodChange}>
                <Radio.Button value="day">日线</Radio.Button>
                <Radio.Button value="week">周线</Radio.Button>
                <Radio.Button value="month">月线</Radio.Button>
                <Radio.Button value="year">年线</Radio.Button>
              </Radio.Group>
              
              {/* 操作按钮 */}
              <Button 
                type={compareMode ? "primary" : "default"}
                onClick={handleCompareToggle}
              >
                对比
              </Button>
              
              <Dropdown 
                menu={{
                  items: indices
                    .filter(index => index.code !== selectedIndex && !comparedIndices.includes(index.code))
                    .map(index => ({
                      key: index.code,
                      label: index.name,
                      onClick: () => handleAddCompareIndex(index.code)
                    })),
                  disabled: !compareMode
                }}
                disabled={!compareMode}
              >
                <Button>
                  <Space>
                    添加对比
                    <DownOutlined />
                  </Space>
                </Button>
              </Dropdown>
              
              <Button onClick={refreshData}><ReloadOutlined /></Button>
              <Button onClick={toggleFullscreen}><FullscreenOutlined /></Button>
            </Space>
          </div>
        )
      }
      bordered={false}
    >
      {compareMode && comparedIndices.length > 0 && (
        <div style={{ marginBottom: '10px' }}>
          <Text strong>正在对比: </Text>
          {comparedIndices.map(code => {
            const index = indices.find(i => i.code === code);
            return (
              <Tag
                key={code}
                closable
                onClose={() => handleRemoveCompareIndex(code)}
                style={{ marginRight: '8px' }}
              >
                {index?.name || code}
              </Tag>
            );
          })}
        </div>
      )}
      
      <Tabs 
        activeKey={activeTab} 
        onChange={handleTabChange}
        items={items}
      />
    </Card>
  );
};

// 自定义Tag组件，包含关闭按钮
const Tag: React.FC<{
  children: React.ReactNode;
  closable?: boolean;
  onClose?: () => void;
  style?: React.CSSProperties;
}> = ({ children, closable, onClose, style }) => {
  return (
    <span 
      className="ant-tag" 
      style={{ 
        display: 'inline-block',
        padding: '0 7px',
        fontSize: '12px',
        lineHeight: '20px',
        borderRadius: '2px',
        backgroundColor: '#f0f0f0',
        border: '1px solid #d9d9d9',
        ...style
      }}
    >
      {children}
      {closable && (
        <span 
          onClick={onClose}
          style={{ 
            marginLeft: '5px',
            cursor: 'pointer'
          }}
        >
          ×
        </span>
      )}
    </span>
  );
};

export default EnhancedIndexChart;