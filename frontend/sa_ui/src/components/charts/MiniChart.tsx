// src/components/charts/MiniChart.tsx
import React, { useEffect, useRef } from 'react';
import * as echarts from 'echarts/core';
import { LineChart } from 'echarts/charts';
import { GridComponent } from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';
import { MiniChartProps, DataPoint, TrendPoint } from '../../types/indicator';

// 注册必要的组件
echarts.use([LineChart, GridComponent, CanvasRenderer]);

const MiniChart: React.FC<MiniChartProps> = ({ data, height = 40, color = '#1890ff' }) => {
  const chartRef = useRef<HTMLDivElement>(null);
  const chartInstance = useRef<echarts.ECharts | null>(null);
  
  // 初始化图表
  useEffect(() => {
    if (chartRef.current) {
      // 如果已经有实例，先销毁
      if (chartInstance.current) {
        chartInstance.current.dispose();
      }
      
      // 创建新实例
      chartInstance.current = echarts.init(chartRef.current);
      
      // 窗口大小变化时自动调整大小
      const handleResize = () => {
        chartInstance.current && chartInstance.current.resize();
      };
      
      window.addEventListener('resize', handleResize);
      
      // 组件卸载时清理
      return () => {
        window.removeEventListener('resize', handleResize);
        chartInstance.current && chartInstance.current.dispose();
      };
    }
  }, []);
  
  // 确定数据结构类型并提取数据
  const processData = (
    data: DataPoint[] | TrendPoint[]
  ): { xData: (string | number)[]; yData: number[] } => {
    // 判断是DataPoint[]还是TrendPoint[]类型的数据
    const isDataPoint = (item: DataPoint | TrendPoint): item is DataPoint => 
      'date' in item && 'value' in item;
    
    // 提取x轴和y轴数据
    if (data.length > 0 && isDataPoint(data[0])) {
      // DataPoint类型数据处理
      return {
        xData: (data as DataPoint[]).map(item => item.date),
        yData: (data as DataPoint[]).map(item => item.value)
      };
    } else {
      // TrendPoint类型数据处理
      return {
        xData: (data as TrendPoint[]).map(item => item.x),
        yData: (data as TrendPoint[]).map(item => item.y)
      };
    }
  };
  
  // 更新图表数据
  useEffect(() => {
    if (chartInstance.current && data && data.length > 0) {
      // 处理数据
      const { xData, yData } = processData(data);
      
      // 极简风格的迷你图表配置
      const options: echarts.EChartsOption = {
        grid: {
          left: 0,
          right: 0,
          top: 0,
          bottom: 0
        },
        xAxis: {
          type: 'category',
          show: false,
          data: xData
        },
        yAxis: {
          type: 'value',
          show: false
        },
        series: [{
          data: yData,
          type: 'line',
          smooth: true,
          symbol: 'none',
          lineStyle: {
            color: color,
            width: 2
          },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              {
                offset: 0,
                color: echarts.color.modifyAlpha(color, 0.3)
              },
              {
                offset: 1,
                color: echarts.color.modifyAlpha(color, 0.05)
              }
            ])
          }
        }],
        animation: false
      };
      
      // 设置图表选项
      chartInstance.current.setOption(options, true);
    }
  }, [data, color]);
  
  return (
    <div 
      ref={chartRef} 
      style={{ width: '100%', height: `${height}px` }}
    />
  );
};

export default MiniChart;