// src/components/charts/IndicatorChartRenderer.tsx
import React, { useRef, useEffect, useState, memo } from 'react';
import ReactECharts from 'echarts-for-react';
import { Empty, Spin, Button } from 'antd';
import { CloseOutlined } from '@ant-design/icons';
import type { EChartsOption } from 'echarts-for-react';
import { IndicatorType, getIndicatorTitle, getIndicatorColors } from './config/chartConfig';

interface IndicatorChartRendererProps {
  indicatorType: IndicatorType;
  indicatorData: any;
  chartData: any[];
  loading: boolean;
  height: number;
  period: string;
  onRemove: (type: IndicatorType) => void;
  onResize?: (type: IndicatorType, height: number) => void;
  onChartInit?: (instance: any) => void;
  isFirstIndicator?: boolean; // 控制是否显示关闭按钮
}

const IndicatorChartRenderer: React.FC<IndicatorChartRendererProps> = ({
  indicatorType,
  indicatorData,
  chartData,
  loading,
  height,
  period,
  onRemove,
  onResize,
  onChartInit,
  isFirstIndicator = false
}) => {
  const chartRef = useRef<ReactECharts>(null);
  const [indicatorValues, setIndicatorValues] = useState<Record<string, number>>({});
  
  useEffect(() => {
    if (chartRef.current && onChartInit) {
      const instance = chartRef.current.getEchartsInstance();
      onChartInit(instance);
    }
  }, [onChartInit]);

  // 计算当前指标值
  useEffect(() => {
    if (chartData.length > 0 && indicatorData) {
      const lastIndex = chartData.length - 1;
      const result: Record<string, number> = {};
      
      if (indicatorType === 'MACD') {
        if (indicatorData.DIF && indicatorData.DIF[lastIndex]) {
          result['DIF'] = parseFloat(indicatorData.DIF[lastIndex][1]);
        }
        if (indicatorData.DEA && indicatorData.DEA[lastIndex]) {
          result['DEA'] = parseFloat(indicatorData.DEA[lastIndex][1]);
        }
        if (indicatorData.MACD && indicatorData.MACD[lastIndex]) {
          result['MACD'] = parseFloat(indicatorData.MACD[lastIndex][1]);
        }
      } else if (indicatorType === 'KDJ') {
        if (indicatorData.K && indicatorData.K[lastIndex]) {
          result['K'] = parseFloat(indicatorData.K[lastIndex][1]);
        }
        if (indicatorData.D && indicatorData.D[lastIndex]) {
          result['D'] = parseFloat(indicatorData.D[lastIndex][1]);
        }
        if (indicatorData.J && indicatorData.J[lastIndex]) {
          result['J'] = parseFloat(indicatorData.J[lastIndex][1]);
        }
      } else if (indicatorType === 'RSI') {
        if (indicatorData.RSI6 && indicatorData.RSI6[lastIndex]) {
          result['RSI6'] = parseFloat(indicatorData.RSI6[lastIndex][1]);
        }
        if (indicatorData.RSI12 && indicatorData.RSI12[lastIndex]) {
          result['RSI12'] = parseFloat(indicatorData.RSI12[lastIndex][1]);
        }
        if (indicatorData.RSI24 && indicatorData.RSI24[lastIndex]) {
          result['RSI24'] = parseFloat(indicatorData.RSI24[lastIndex][1]);
        }
      }
      
      setIndicatorValues(result);
    }
  }, [chartData, indicatorData, indicatorType]);

  // 预处理数据，为每个日期标记是否为月首日
  const processDateLabels = () => {
    if (!chartData || chartData.length === 0) return [];
    
    const result: { value: string; isFirstOfMonth: boolean; yearMonth: string }[] = [];
    let prevYearMonth = '';
    
    chartData.forEach((item, index) => {
      const dateStr = item[0];
      if (!dateStr) return;
      
      try {
        const parts = dateStr.split('-');
        if (parts.length < 3) {
          result.push({ value: dateStr, isFirstOfMonth: false, yearMonth: '' });
          return;
        }
        
        const year = parseInt(parts[0]);
        const month = parseInt(parts[1]);
        const yearMonth = `${year}/${month}`;
        
        // 判断是否为月首日
        const isFirstOfMonth = yearMonth !== prevYearMonth;
        
        result.push({ 
          value: dateStr, 
          isFirstOfMonth, 
          yearMonth: isFirstOfMonth ? `${year.toString().substring(2)}/${month.toString().padStart(2, '0')}` : ''
        });
        
        prevYearMonth = yearMonth;
      } catch (e) {
        result.push({ value: dateStr, isFirstOfMonth: false, yearMonth: '' });
      }
    });
    
    return result;
  };

  // 生成指标图表选项
  const getOption = (): EChartsOption => {
    // 处理日期标签
    const dateLabels = processDateLabels();
    
    // 基础配置
    const baseOption: EChartsOption = {
      backgroundColor: '#ffffff',
      title: {
        text: getIndicatorTitle(indicatorType),
        left: 'center',
        textStyle: {
          fontSize: 12
        }
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'cross'
        }
      },
      grid: {
        left: '3%',
        right: '4%',
        top: '45px', // 增加顶部空间以显示指标值
        bottom: '15%',
        containLabel: true
      },
      graphic: [
        {
          type: 'text',
          left: 10,
          top: 25,
          style: {
            text: getIndicatorValueText(),
            fontSize: 12,
            fill: '#333333'
          }
        }
      ],
      xAxis: {
        type: 'category',
        boundaryGap: false,
        data: chartData.length > 0 ? chartData.map(item => item[0]) : [],
        axisLine: { lineStyle: { color: '#E0E0E0' } },
        axisLabel: {
          formatter: (value: string, index: number) => {
            // 使用预处理的数据显示月份标签
            return dateLabels[index]?.yearMonth || '';
          },
          color: '#333333',
          fontSize: 12,
          // 强制显示所有月份标签
          interval: (index: number) => {
            return dateLabels[index]?.isFirstOfMonth || false;
          }
        },
        axisTick: {
          show: true,
          alignWithLabel: true,
          interval: (index: number) => {
            return dateLabels[index]?.isFirstOfMonth || false;
          },
          lineStyle: {
            color: '#666666'
          }
        }
      },
      yAxis: {
        type: 'value',
        scale: true,
        splitLine: { lineStyle: { color: '#E0E0E0', type: 'dashed' } }
      },
      dataZoom: [
        {
          type: 'inside',
          xAxisIndex: [0],
          start: 0,
          end: 100
        }
      ],
      // 移除可能导致显示额外关闭按钮的配置
      toolbox: {
        show: false // 确保不显示工具箱
      }
    };
    
    // 获取当前指标的颜色配置
    const colors = getIndicatorColors(indicatorType);
    
    // 根据指标类型构建特定系列
    let series: any[] = [];
    
    if (indicatorType === 'MACD') {
      // MACD指标
      if (indicatorData) {
        // MACD线
        if (indicatorData.MACD) {
          series.push({
            name: 'MACD',
            type: 'line',
            data: indicatorData.MACD,
            lineStyle: {
              color: colors.MACD || '#ff00ff'
            },
            smooth: true
          });
        }
        
        // DIF线
        if (indicatorData.DIF) {
          series.push({
            name: 'DIF',
            type: 'line',
            data: indicatorData.DIF,
            lineStyle: {
              color: colors.DIF || '#ffcc00'
            },
            smooth: true
          });
        }
        
        // DEA线
        if (indicatorData.DEA) {
          series.push({
            name: 'DEA',
            type: 'line',
            data: indicatorData.DEA,
            lineStyle: {
              color: colors.DEA || '#ff6600'
            },
            smooth: true
          });
        }
        
        // MACD柱状图
        if (indicatorData.HIST) {
          series.push({
            name: 'HIST',
            type: 'bar',
            data: indicatorData.HIST.map((item: any) => {
              const value = item[1];
              return {
                value: value,
                itemStyle: {
                  color: value >= 0 ? (colors.HIST_UP || '#ef232a') : (colors.HIST_DOWN || '#14b143')
                }
              };
            }),
            barWidth: '60%'
          });
        }
      }
    } else if (indicatorType === 'KDJ') {
      // KDJ指标
      if (indicatorData) {
        // K线
        if (indicatorData.K) {
          series.push({
            name: 'K',
            type: 'line',
            data: indicatorData.K,
            lineStyle: {
              color: colors.K || '#ffc53d'
            },
            smooth: true
          });
        }
        
        // D线
        if (indicatorData.D) {
          series.push({
            name: 'D',
            type: 'line',
            data: indicatorData.D,
            lineStyle: {
              color: colors.D || '#40a9ff'
            },
            smooth: true
          });
        }
        
        // J线
        if (indicatorData.J) {
          series.push({
            name: 'J',
            type: 'line',
            data: indicatorData.J,
            lineStyle: {
              color: colors.J || '#ff4d4f'
            },
            smooth: true
          });
        }
      }
    } else if (indicatorType === 'RSI') {
      // RSI指标
      if (indicatorData) {
        // RSI6线
        if (indicatorData.RSI6) {
          series.push({
            name: 'RSI6',
            type: 'line',
            data: indicatorData.RSI6,
            lineStyle: {
              color: colors.RSI6 || '#ffc53d'
            },
            smooth: true
          });
        }
        
        // RSI12线
        if (indicatorData.RSI12) {
          series.push({
            name: 'RSI12',
            type: 'line',
            data: indicatorData.RSI12,
            lineStyle: {
              color: colors.RSI12 || '#40a9ff'
            },
            smooth: true
          });
        }
        
        // RSI24线
        if (indicatorData.RSI24) {
          series.push({
            name: 'RSI24',
            type: 'line',
            data: indicatorData.RSI24,
            lineStyle: {
              color: colors.RSI24 || '#ff4d4f'
            },
            smooth: true
          });
        }
        
        // 添加超买超卖区域标记
        series.push({
          name: '超买线',
          type: 'line',
          data: chartData.map(item => [item[0], 70]),
          lineStyle: {
            color: '#ff4d4f',
            type: 'dashed',
            width: 1
          },
          showSymbol: false
        });
        
        series.push({
          name: '超卖线',
          type: 'line',
          data: chartData.map(item => [item[0], 30]),
          lineStyle: {
            color: '#52c41a',
            type: 'dashed',
            width: 1
          },
          showSymbol: false
        });
      }
    } else if (indicatorType === 'VOL') {
      // 成交量指标
      if (chartData.length > 0 && chartData[0].length >= 6) {
        // 成交量柱状图
        series.push({
          name: '成交量',
          type: 'bar',
          data: chartData.map(item => {
            const volume = item[5];
            const open = item[1];
            const close = item[2];
            
            return {
              value: volume,
              itemStyle: {
                color: close >= open ? (colors.UP || '#ef232a') : (colors.DOWN || '#14b143')
              }
            };
          }),
          barWidth: '60%'
        });
        
        // 如果有成交量MA5
        if (indicatorData && indicatorData.MA5) {
          series.push({
            name: '成交量MA5',
            type: 'line',
            data: indicatorData.MA5,
            lineStyle: {
              color: colors.MA5 || '#ffc53d'
            },
            smooth: true
          });
        }
        
        // 如果有成交量MA10
        if (indicatorData && indicatorData.MA10) {
          series.push({
            name: '成交量MA10',
            type: 'line',
            data: indicatorData.MA10,
            lineStyle: {
              color: colors.MA10 || '#40a9ff'
            },
            smooth: true
          });
        }
      }
    }
    
    return {
      ...baseOption,
      series: series
    };
  };
  
  // 获取指标值文本
  const getIndicatorValueText = (): string => {
    if (indicatorType === 'MACD') {
      return `DIF:${indicatorValues.DIF?.toFixed(2) || '-'} DEA:${indicatorValues.DEA?.toFixed(2) || '-'} MACD:${indicatorValues.MACD?.toFixed(2) || '-'}`;
    } else if (indicatorType === 'KDJ') {
      return `K:${indicatorValues.K?.toFixed(2) || '-'} D:${indicatorValues.D?.toFixed(2) || '-'} J:${indicatorValues.J?.toFixed(2) || '-'}`;
    } else if (indicatorType === 'RSI') {
      return `RSI6:${indicatorValues.RSI6?.toFixed(2) || '-'} RSI12:${indicatorValues.RSI12?.toFixed(2) || '-'} RSI24:${indicatorValues.RSI24?.toFixed(2) || '-'}`;
    } else if (indicatorType === 'VOL') {
      return '成交量';
    }
    return getIndicatorTitle(indicatorType);
  };

  return (
    <div className="indicator-chart-container" style={{ height, width: '100%', position: 'relative', marginBottom: '10px' }}>
      {/* 指标控制器 - 只有在不是第一个指标时才显示关闭按钮 */}
      {!isFirstIndicator && (
        <div style={{ position: 'absolute', top: 0, right: 0, zIndex: 10 }}>
          <Button 
            type="text" 
            size="small" 
            icon={<CloseOutlined />} 
            onClick={() => onRemove(indicatorType)} 
          />
        </div>
      )}
      
      {loading ? (
        <div style={{ height: 'calc(100% - 25px)', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
          <Spin tip="加载中..." />
        </div>
      ) : indicatorData ? (
        <ReactECharts 
          option={getOption()} 
          style={{ height: 'calc(100% - 10px)', width: '100%' }} 
          notMerge={true}
          ref={chartRef}
        />
      ) : (
        <Empty 
          description="暂无指标数据" 
          style={{ height: 'calc(100% - 25px)', display: 'flex', flexDirection: 'column', justifyContent: 'center' }} 
        />
      )}
    </div>
  );
};

// 使用 React.memo 包装组件，避免不必要的重新渲染
export default memo(IndicatorChartRenderer, (prevProps, nextProps) => {
  // 只有在以下属性发生变化时才重新渲染（返回 false）
  // 如果返回 true，表示组件不需要重新渲染
  return (
    prevProps.indicatorType === nextProps.indicatorType &&
    prevProps.indicatorData === nextProps.indicatorData &&
    prevProps.loading === nextProps.loading &&
    prevProps.height === nextProps.height &&
    prevProps.period === nextProps.period &&
    prevProps.isFirstIndicator === nextProps.isFirstIndicator &&
    prevProps.chartData === nextProps.chartData
  );
});