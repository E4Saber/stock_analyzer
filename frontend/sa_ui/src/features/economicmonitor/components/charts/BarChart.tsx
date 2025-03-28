// src/components/charts/BarChart.tsx
import React, { useEffect, useRef } from 'react';
import * as echarts from 'echarts/core';
import { BarChart as EChartsBarChart } from 'echarts/charts';
import { GridComponent, TooltipComponent, LegendComponent, TitleComponent, ToolboxComponent, DataZoomComponent } from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';
import { generateBarOptions } from '../../utils/chartOptions';
import { BarChartProps } from '../../types/indicator';

// 注册必要的组件
echarts.use([
  EChartsBarChart,
  GridComponent,
  TooltipComponent,
  LegendComponent,
  TitleComponent,
  ToolboxComponent,
  DataZoomComponent,
  CanvasRenderer
]);

const BarChart: React.FC<BarChartProps> = ({
  data,
  title,
  height = 300,
  compareMode = 'actual', // 'actual', 'yoy', 'mom'
  showTooltip = true,
  showLegend = false,
  showDataZoom = false,
  showToolbox = false,
  compareWith = [], // 用于对比的其他指标数据
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
    if (chartInstance.current && data) {
      // 生成图表选项
      const options = generateBarOptions({
        data,
        title,
        compareMode,
        showTooltip,
        showLegend,
        showDataZoom,
        showToolbox,
        compareWith,
      });
      
      // 设置图表选项
      chartInstance.current.setOption(options, true);
    }
  }, [data, title, compareMode, showTooltip, showLegend, showDataZoom, showToolbox, compareWith]);
  
  return (
    <div 
      ref={chartRef} 
      style={{ width: '100%', height: `${height}px` }}
    />
  );
};

export default BarChart;