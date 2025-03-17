// src/components/charts/IndicatorChartRenderer.tsx
import React, { useRef, useEffect } from 'react';
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
  onChartInit?: (type: IndicatorType, instance: any) => void;
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
  onChartInit
}) => {
  const chartRef = useRef<ReactECharts>(null);
  
  useEffect(() => {
    if (chartRef.current && onChartInit) {
      const instance = chartRef.current.getEchartsInstance();
      onChartInit(indicatorType, instance);
    }
  }, [chartRef.current, indicatorType]);

  // 生成技术指标图表选项
  const getOption = (): EChartsOption => {
    // 基础配置
    const baseOption: EChartsOption = {
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
        top: '25px',
        bottom: '15%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        boundaryGap: false,
        data: chartData.length > 0 ? chartData.map(item => item[0]) : [],
        axisLine: { lineStyle: { color: '#E0E0E0' } },
        axisLabel: {
          formatter: (value: string) => {
            // 根据周期格式化日期
            if (period === 'day' || period.includes('m')) {
              return value.substring(5); // 显示月-日
            } else if (period === 'week') {
              return value.substring(0, 10); // 显示年-月-日
            } else {
              return value.substring(0, 7); // 显示年-月
            }
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
              color: colors.MACD || '#ffffff'
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
              color: colors.DIF || '#da6ee8'
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
              color: colors.DEA || '#40a9ff'
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

  return (
    <div style={{ height, width: '100%', position: 'relative', marginBottom: '10px' }}>
      {/* 指标控制器 */}
      <div style={{ position: 'absolute', top: 0, right: 0, zIndex: 10 }}>
        <Button 
          type="text" 
          size="small" 
          icon={<CloseOutlined />} 
          onClick={() => onRemove(indicatorType)} 
        />
      </div>
      
      {loading ? (
        <div style={{ height: 'calc(100% - 25px)', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
          <Spin tip="加载中..." />
        </div>
      ) : indicatorData ? (
        <ReactECharts 
          option={getOption()} 
          style={{ height: 'calc(100% - 25px)', width: '100%' }} 
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

export default IndicatorChartRenderer;