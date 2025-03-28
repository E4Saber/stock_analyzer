// src/components/charts/IndexChart.tsx
import React, { useEffect, useState } from 'react';
import ReactECharts from 'echarts-for-react';
import { IndexData } from '../../../marketoverview/types/market';
import { Empty, Spin, Radio } from 'antd';
import { getStockKline } from '../../../stockinsight/services/stockService';

interface IndexChartProps {
  indices: IndexData[];
}

const IndexChart: React.FC<IndexChartProps> = ({ indices }) => {
  const [selectedIndex, setSelectedIndex] = useState<string>(indices[0]?.ts_code || '');
  const [klineData, setKlineData] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [period, setPeriod] = useState<string>('5d');

  useEffect(() => {
    if (!selectedIndex) return;
    
    const fetchKlineData = async () => {
      setLoading(true);
      try {
        const response = await getStockKline(selectedIndex, period, 'line');
        // 转换数据格式
        const chartData = response.data.map(item => [
          item.date,
          item.close
        ]);
        setKlineData(chartData);
      } catch (error) {
        console.error('获取K线数据失败:', error);
        setKlineData([]);
      } finally {
        setLoading(false);
      }
    };
    
    fetchKlineData();
  }, [selectedIndex, period]);

  // 指数选择器
  const handleIndexChange = (e: any) => {
    setSelectedIndex(e.target.value);
  };

  // 周期选择器
  const handlePeriodChange = (e: any) => {
    setPeriod(e.target.value);
  };

  // 图表选项
  const getOption = () => {
    const selectedName = indices.find(i => i.ts_code === selectedIndex)?.name || '';
    
    return {
      title: {
        text: `${selectedName}走势图`,
        left: 'center',
      },
      tooltip: {
        trigger: 'axis',
        formatter: (params: any) => {
          const data = params[0];
          return `${data.name}<br/>${data.marker}${selectedName}: ${data.value[1]}`;
        }
      },
      xAxis: {
        type: 'category',
        data: klineData.map(item => item[0]),
        boundaryGap: false,
        axisLine: { lineStyle: { color: '#E0E0E0' } },
        axisLabel: {
          formatter: (value: string) => {
            // 简化日期显示
            return value.substring(5); // 只显示月-日
          }
        }
      },
      yAxis: {
        type: 'value',
        scale: true,
        splitLine: { lineStyle: { color: '#E0E0E0' } },
        axisLabel: {
          formatter: (value: number) => {
            return value.toFixed(0);
          }
        }
      },
      series: [
        {
          name: selectedName,
          type: 'line',
          data: klineData,
          lineStyle: {
            color: '#1890ff',
            width: 2
          },
          itemStyle: {
            color: '#1890ff'
          },
          areaStyle: {
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
        }
      ],
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      }
    };
  };

  return (
    <div>
      <div style={{ marginBottom: '16px', display: 'flex', justifyContent: 'space-between' }}>
        <Radio.Group value={selectedIndex} onChange={handleIndexChange}>
          {indices.map(index => (
            <Radio.Button key={index.ts_code} value={index.ts_code}>
              {index.name}
            </Radio.Button>
          ))}
        </Radio.Group>
        
        <Radio.Group value={period} onChange={handlePeriodChange}>
          <Radio.Button value="5d">5日</Radio.Button>
          <Radio.Button value="1mo">1月</Radio.Button>
          <Radio.Button value="3mo">3月</Radio.Button>
        </Radio.Group>
      </div>
      
      {loading ? (
        <div style={{ height: '300px', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
          <Spin tip="加载中..." />
        </div>
      ) : klineData.length > 0 ? (
        <ReactECharts option={getOption()} style={{ height: '300px' }} />
      ) : (
        <Empty description="暂无数据" style={{ height: '300px', display: 'flex', flexDirection: 'column', justifyContent: 'center' }} />
      )}
    </div>
  );
};

export default IndexChart;