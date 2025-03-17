// src/components/charts/HeatmapChart.tsx
import React from 'react';
import ReactECharts from 'echarts-for-react';
import { SectorData } from '../../types/market';
import { Empty } from 'antd';

interface HeatmapChartProps {
  data: SectorData[];
}

const HeatmapChart: React.FC<HeatmapChartProps> = ({ data }) => {
  // 无数据处理
  if (!data || data.length === 0) {
    return <Empty description="暂无数据" />;
  }

  // 按涨跌幅排序
  const sortedData = [...data].sort((a, b) => b.change_pct - a.change_pct);
  
  // 准备图表数据
  const chartData = sortedData.map(item => ({
    name: item.name,
    value: item.change_pct,
    volume: item.avg_volume
  }));
  
  // 图表选项
  const option = {
    tooltip: {
      formatter: (params: any) => {
        return `${params.name}<br/>涨跌幅: ${params.value.toFixed(2)}%<br/>成交量: ${(params.data.volume / 10000).toFixed(2)}万`;
      }
    },
    series: [
      {
        type: 'treemap',
        data: chartData,
        width: '100%',
        height: '100%',
        roam: false,
        nodeClick: false,
        breadcrumb: {
          show: false
        },
        label: {
          show: true,
          formatter: '{b}\n{c}%',
          fontSize: 12
        },
        upperLabel: {
          show: false
        },
        itemStyle: {
          borderColor: '#fff',
          borderWidth: 1,
          gapWidth: 1
        },
        visualMap: {
          type: 'continuous',
          min: -5,
          max: 5,
          inRange: {
            color: ['#cf1322', '#fafafa', '#3f8600']
          }
        },
        levels: [
          {
            itemStyle: {
              borderWidth: 0,
              gapWidth: 1
            }
          },
          {
            itemStyle: {
              borderColor: '#fff',
              borderWidth: 1,
              gapWidth: 1
            }
          }
        ]
      }
    ]
  };

  return (
    <ReactECharts
      option={option}
      style={{ height: '300px' }}
      opts={{ renderer: 'canvas' }}
    />
  );
};

export default HeatmapChart;