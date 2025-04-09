import React from 'react';
import { Card } from 'antd';

interface MacroChartProps {
  title: string;
  chartType: 'CPI' | 'PMI' | 'GDP' | 'other';
  countryCode: string;
}

const MacroEconomyChart: React.FC<MacroChartProps> = ({ title, chartType, countryCode }) => {
  // 在实际项目中，这里会根据chartType和countryCode加载对应的数据
  // 并使用ECharts、Recharts等库来渲染图表
  
  // 模拟不同类型图表的颜色
  const getChartColor = () => {
    switch (chartType) {
      case 'CPI':
        return '#ff7875';
      case 'PMI':
        return '#73d13d';
      case 'GDP':
        return '#40a9ff';
      default:
        return '#ffc53d';
    }
  };

  return (
    <Card 
      title={title} 
      bordered={false}
      className="macro-chart-card"
    >
      <div 
        className="chart-container"
        style={{ 
          background: `linear-gradient(to bottom, rgba(255,255,255,0.9), rgba(255,255,255,0.6))`,
          borderLeft: `4px solid ${getChartColor()}`
        }}
      >
        <div style={{ textAlign: 'center' }}>
          <p style={{ color: '#8c8c8c' }}>
            {chartType} 趋势图将在此处显示
            <br />
            <small>({countryCode} 地区数据)</small>
          </p>
        </div>
      </div>
    </Card>
  );
};

export default MacroEconomyChart;