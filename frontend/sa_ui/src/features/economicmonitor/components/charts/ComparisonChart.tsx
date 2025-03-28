// src/components/charts/ComparisonChart.tsx
import React, { useEffect, useRef } from 'react';
import * as echarts from 'echarts/core';
import { LineChart, BarChart } from 'echarts/charts';
import { GridComponent, TooltipComponent, LegendComponent, TitleComponent, ToolboxComponent, DataZoomComponent } from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';
import { generateComparisonOptions } from '../../utils/chartOptions';
import { DataPoint, RelatedIndicatorType, CompareModeType } from '../../types/indicator';

// 注册必要的组件
echarts.use([
  LineChart,
  BarChart,
  GridComponent,
  TooltipComponent,
  LegendComponent,
  TitleComponent,
  ToolboxComponent,
  DataZoomComponent,
  CanvasRenderer
]);

interface ComparisonChartProps {
  data: DataPoint[];
  compareWith: RelatedIndicatorType[];
  title?: string;
  height?: number;
  compareMode?: CompareModeType;
}

const ComparisonChart: React.FC<ComparisonChartProps> = ({
  data,
  compareWith,
  title,
  height = 400,
  compareMode = 'actual',
}) => {
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
  
  // 更新图表数据
  useEffect(() => {
    if (chartInstance.current && data && compareWith) {
      // 生成对比图表选项
      const options = generateComparisonOptions({
        data,
        compareWith,
        title,
        compareMode,
      });
      
      // 设置图表选项
      chartInstance.current.setOption(options, true);
    }
  }, [data, compareWith, title, compareMode]);
  
  return (
    <div 
      ref={chartRef} 
      style={{ width: '100%', height: `${height}px` }}
    />
  );
};

export default ComparisonChart;