// src/components/charts/MainChartRenderer.tsx
import React, { useRef, useEffect } from 'react';
import ReactECharts from 'echarts-for-react';
import { Empty, Spin } from 'antd';
import type { EChartsOption } from 'echarts-for-react';
import { ChartType, IndicatorType, StockData } from './config/chartConfig';

interface MainChartRendererProps {
  selectedStock: string;
  chartData: any[];
  loading: boolean;
  chartType: ChartType;
  chartHeight: number;
  period: string;
  showTitle: boolean;
  compareMode: boolean;
  comparedStocks: string[];
  comparedData: Record<string, any[]>;
  indicatorData: Record<IndicatorType, any>;
  stocks: StockData[];
  onChartInit?: (instance: any) => void;
}

const MainChartRenderer: React.FC<MainChartRendererProps> = ({
  selectedStock,
  chartData,
  loading,
  chartType,
  chartHeight,
  period,
  showTitle,
  compareMode,
  comparedStocks,
  comparedData,
  indicatorData,
  stocks,
  onChartInit
}) => {
  const chartRef = useRef<ReactECharts>(null);
  
  useEffect(() => {
    if (chartRef.current && onChartInit) {
      const instance = chartRef.current.getEchartsInstance();
      onChartInit(instance);
    }
  }, [chartRef.current]);

  // 生成主图表选项
  const getOption = (): EChartsOption => {
    const selectedStockInfo = stocks.find(s => s.code === selectedStock);
    const selectedName = selectedStockInfo?.name || '';
    
    // 基础配置
    const baseOption: EChartsOption = {
      title: showTitle ? {
        text: `${selectedName} (${selectedStock})${compareMode ? ' - 对比图' : ''}`,
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
            
            // 主要股票及比较股票的数据
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
              <div style="font-weight: bold">${date}</div>
              <div>开盘: ${values[1].toFixed(2)}</div>
              <div>收盘: ${values[2].toFixed(2)}</div>
              <div>最低: ${values[3].toFixed(2)}</div>
              <div>最高: ${values[4].toFixed(2)}</div>
              <div>成交量: ${values[5]}</div>
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
        data: [selectedName, ...comparedStocks.map(code => {
          const stock = stocks.find(s => s.code === code);
          return stock?.name || code;
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
          xAxisIndex: [0],
          start: 0,
          end: 100
        },
        {
          type: 'slider',
          xAxisIndex: [0],
          start: 0,
          end: 100,
          bottom: 50
        }
      ],
      xAxis: {
        type: 'category',
        boundaryGap: chartType !== 'line',
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
        splitLine: { lineStyle: { color: '#E0E0E0', type: 'dashed' } },
        axisLabel: {
          formatter: (value: number) => {
            return value.toFixed(2);
          }
        }
      }
    };
    
    // 根据图表类型创建不同的系列
    let series: any[] = [];
    
    if (chartType === 'line') {
      // 创建主要股票的线图系列
      const mainSeries = {
        name: selectedName,
        type: 'line',
        data: chartData,
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
      
      // 如果启用了比较模式，添加比较股票的系列
      if (compareMode && comparedStocks.length > 0) {
        // 颜色数组，用于不同的比较股票
        const colors = ['#52c41a', '#faad14', '#f5222d', '#722ed1', '#eb2f96'];
        
        comparedStocks.forEach((code, index) => {
          const stockInfo = stocks.find(s => s.code === code);
          const stockName = stockInfo?.name || code;
          const color = colors[index % colors.length];
          
          // 只有当有数据时才添加系列
          if (comparedData[code] && comparedData[code].length > 0) {
            series.push({
              name: stockName,
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
      if (indicatorData && indicatorData['MA']) {
        const maData = indicatorData['MA'];
        
        // 添加MA5
        if (maData.MA5) {
          series.push({
            name: 'MA5',
            type: 'line',
            data: maData.MA5,
            smooth: true,
            lineStyle: {
              opacity: 0.7,
              color: '#8d4bbb'
            },
            showSymbol: false
          });
        }
        
        // 添加MA10
        if (maData.MA10) {
          series.push({
            name: 'MA10',
            type: 'line',
            data: maData.MA10,
            smooth: true,
            lineStyle: {
              opacity: 0.7,
              color: '#ff9900'
            },
            showSymbol: false
          });
        }
        
        // 添加MA20
        if (maData.MA20) {
          series.push({
            name: 'MA20',
            type: 'line',
            data: maData.MA20,
            smooth: true,
            lineStyle: {
              opacity: 0.7,
              color: '#cc0000'
            },
            showSymbol: false
          });
        }
      }
    } else if (chartType === 'candle') {
      // 创建K线图系列
      if (chartData.length > 0) {
        series.push({
          name: selectedName,
          type: 'candlestick',
          data: chartData.map(item => [item[1], item[2], item[3], item[4]]), // 开盘、收盘、最低、最高
          itemStyle: {
            color: '#ef232a', // 阳线颜色
            color0: '#14b143', // 阴线颜色
            borderColor: '#ef232a',
            borderColor0: '#14b143'
          },
        });
      }
      
      // 添加布林带指标
      if (indicatorData && indicatorData['BOLL']) {
        const bollData = indicatorData['BOLL'];
        
        // 添加上轨
        if (bollData.UPPER) {
          series.push({
            name: 'BOLL上轨',
            type: 'line',
            data: bollData.UPPER,
            smooth: true,
            lineStyle: {
              opacity: 0.7,
              color: '#ff9900'
            },
            showSymbol: false
          });
        }
        
        // 添加中轨
        if (bollData.MID) {
          series.push({
            name: 'BOLL中轨',
            type: 'line',
            data: bollData.MID,
            smooth: true,
            lineStyle: {
              opacity: 0.7,
              color: '#8d4bbb'
            },
            showSymbol: false
          });
        }
        
        // 添加下轨
        if (bollData.LOWER) {
          series.push({
            name: 'BOLL下轨',
            type: 'line',
            data: bollData.LOWER,
            smooth: true,
            lineStyle: {
              opacity: 0.7,
              color: '#ff9900'
            },
            showSymbol: false
          });
        }
      }
      
      // 添加移动平均线指标
      if (indicatorData && indicatorData['MA']) {
        const maData = indicatorData['MA'];
        
        // 添加MA5
        if (maData.MA5) {
          series.push({
            name: 'MA5',
            type: 'line',
            data: maData.MA5,
            smooth: true,
            lineStyle: {
              opacity: 0.7,
              color: '#8d4bbb'
            },
            showSymbol: false
          });
        }
        
        // 添加其他MA线...这里可以根据需要添加
      }
    } else if (chartType === 'bar') {
      // 创建成交量柱状图系列
      if (chartData.length > 0) {
        series.push({
          name: '成交量',
          type: 'bar',
          data: chartData.map(item => {
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
    }
    
    return {
      ...baseOption,
      series: series
    };
  };

  return (
    <div style={{ height: chartHeight, width: '100%' }}>
      {loading ? (
        <div style={{ height: '100%', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
          <Spin tip="加载中..." />
        </div>
      ) : chartData.length > 0 ? (
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
  );
};

export default MainChartRenderer;