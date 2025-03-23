// src/components/charts/MainChartRenderer.tsx
import React, { useRef, useEffect, useState, memo } from 'react';
import ReactECharts from 'echarts-for-react';
import { Empty, Spin } from 'antd';
import type { EChartsOption } from 'echarts-for-react';
import { StockData } from './config/chartConfig';

// 更新后的接口定义
interface MainChartRendererProps {
  selectedStock: string;
  chartData: any[];
  loading: boolean;
  chartHeight: number;
  period: string;
  showTitle: boolean;
  stocks: StockData[];
  indicatorData?: Record<string, any>; 
  mainIndicator?: string; // 主图指标类型
  onChartInit?: (instance: any) => void;
}

const MainChartRenderer: React.FC<MainChartRendererProps> = ({
  selectedStock,
  chartData,
  loading,
  chartHeight,
  period,
  showTitle,
  stocks,
  indicatorData,
  mainIndicator = 'MA',
  onChartInit
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
    if (chartData.length > 0 && mainIndicator === 'MA' && indicatorData?.MA) {
      const lastIndex = chartData.length - 1;
      const result: Record<string, number> = {};
      
      // 获取MA5值
      if (indicatorData.MA.MA5 && indicatorData.MA.MA5[lastIndex]) {
        result['MA5'] = parseFloat(indicatorData.MA.MA5[lastIndex][1]);
      }
      
      // 获取MA10值
      if (indicatorData.MA.MA10 && indicatorData.MA.MA10[lastIndex]) {
        result['MA10'] = parseFloat(indicatorData.MA.MA10[lastIndex][1]);
      }
      
      // 获取MA20值
      if (indicatorData.MA.MA20 && indicatorData.MA.MA20[lastIndex]) {
        result['MA20'] = parseFloat(indicatorData.MA.MA20[lastIndex][1]);
      }
      
      // 获取MA30值
      if (indicatorData.MA.MA30 && indicatorData.MA.MA30[lastIndex]) {
        result['MA30'] = parseFloat(indicatorData.MA.MA30[lastIndex][1]);
      }
      
      setIndicatorValues(result);
    } else if (chartData.length > 0 && mainIndicator === 'BOLL' && indicatorData?.BOLL) {
      const lastIndex = chartData.length - 1;
      const result: Record<string, number> = {};
      
      // 获取BOLL上轨
      if (indicatorData.BOLL.UPPER && indicatorData.BOLL.UPPER[lastIndex]) {
        result['UPPER'] = parseFloat(indicatorData.BOLL.UPPER[lastIndex][1]);
      }
      
      // 获取BOLL中轨
      if (indicatorData.BOLL.MID && indicatorData.BOLL.MID[lastIndex]) {
        result['MID'] = parseFloat(indicatorData.BOLL.MID[lastIndex][1]);
      }
      
      // 获取BOLL下轨
      if (indicatorData.BOLL.LOWER && indicatorData.BOLL.LOWER[lastIndex]) {
        result['LOWER'] = parseFloat(indicatorData.BOLL.LOWER[lastIndex][1]);
      }
      
      setIndicatorValues(result);
    }
  }, [chartData, indicatorData, mainIndicator]);

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

  // 生成图表选项
  const getOption = (): EChartsOption => {
    const selectedStockInfo = stocks.find(s => s.code === selectedStock);
    const selectedName = selectedStockInfo?.name || '';
    
    // 处理日期标签
    const dateLabels = processDateLabels();
    
    // 基础配置
    const baseOption: EChartsOption = {
      backgroundColor: '#ffffff',
      title: showTitle ? {
        text: `${selectedName} (${selectedStock})`,
        left: 'center',
      } : undefined,
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'cross'
        },
        formatter: (params: any) => {
          let tooltipText = '';
          
          // 如果是K线数据
          if (params[0] && params[0].seriesType === 'candlestick') {
            const param = params[0];
            const date = param.axisValue;
            const values = param.value;
            
            tooltipText = `
              <div style="font-weight: bold">${date}</div>
              <div>开盘: ${values[1].toFixed(2)}</div>
              <div>收盘: ${values[2].toFixed(2)}</div>
              <div>最低: ${values[3].toFixed(2)}</div>
              <div>最高: ${values[4].toFixed(2)}</div>
            `;
            
            // 添加MA线或BOLL线数据
            for (let i = 1; i < params.length; i++) {
              const indicatorParam = params[i];
              if (indicatorParam.value[1] !== '-') {
                tooltipText += `<div>${indicatorParam.marker}${indicatorParam.seriesName}: ${indicatorParam.value[1]}</div>`;
              }
            }
            
            return tooltipText;
          }
          
          // 默认情况
          return '';
        }
      },
      legend: {
        data: mainIndicator === 'MA' 
          ? [selectedName, 'MA5', 'MA10', 'MA20', 'MA30']
          : mainIndicator === 'BOLL'
            ? [selectedName, 'BOLL上轨', 'BOLL中轨', 'BOLL下轨']
            : [selectedName],
        type: 'scroll',
        bottom: 10
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '15%',
        top: '50px', // 增加顶部空间以显示指标值
        containLabel: true
      },
      graphic: mainIndicator === 'MA' ? [
        {
          type: 'text',
          left: 10,
          top: 10,
          style: {
            text: `MA5:${indicatorValues.MA5?.toFixed(2) || '-'} `,
            fontSize: 12,
            fill: '#8d4bbb'
          }
        },
        {
          type: 'text',
          left: 95,
          top: 10,
          style: {
            text: `MA10:${indicatorValues.MA10?.toFixed(2) || '-'} `,
            fontSize: 12,
            fill: '#ff9900'
          }
        },
        {
          type: 'text',
          left: 185,
          top: 10,
          style: {
            text: `MA20:${indicatorValues.MA20?.toFixed(2) || '-'} `,
            fontSize: 12,
            fill: '#cc0000'
          }
        },
        {
          type: 'text',
          left: 275,
          top: 10,
          style: {
            text: `MA30:${indicatorValues.MA30?.toFixed(2) || '-'}`,
            fontSize: 12,
            fill: '#00994e'
          }
        }
      ] : mainIndicator === 'BOLL' ? [
        {
          type: 'text',
          left: 10,
          top: 10,
          style: {
            text: `UPPER:${indicatorValues.UPPER?.toFixed(2) || '-'} `,
            fontSize: 12,
            fill: '#ff9900'
          }
        },
        {
          type: 'text',
          left: 95,
          top: 10,
          style: {
            text: `MID:${indicatorValues.MID?.toFixed(2) || '-'} `,
            fontSize: 12,
            fill: '#8d4bbb'
          }
        },
        {
          type: 'text',
          left: 175,
          top: 10,
          style: {
            text: `LOWER:${indicatorValues.LOWER?.toFixed(2) || '-'}`,
            fontSize: 12,
            fill: '#ff9900'
          }
        }
      ] : [],
      toolbox: {
        show: false,
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
        boundaryGap: true,
        data: dateLabels.map(item => item.value),
        axisLine: { lineStyle: { color: '#E0E0E0' } },
        axisLabel: {
          formatter: (value: string, index: number) => {
            // 使用预处理的数据显示月份标签
            return dateLabels[index]?.yearMonth || '';
          },
          color: '#333333',
          fontWeight: 'bold',
          fontSize: 12,
          align: 'center',
          margin: 14,
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
        splitLine: { lineStyle: { color: '#E0E0E0', type: 'dashed' } },
        axisLabel: {
          formatter: (value: number) => {
            return value.toFixed(2);
          }
        }
      }
    };
    
    // 为K线图和MA线定义系列
    let series: any[] = [];
    
    // K线图系列
    if (chartData.length > 0) {
      series.push({
        name: selectedName,
        type: 'candlestick',
        data: chartData.map(item => [item[1], item[2], item[3], item[4]]), // 开盘, 收盘, 最低, 最高
        itemStyle: {
          color: '#ef232a', // 上涨蜡烛颜色
          color0: '#14b143', // 下跌蜡烛颜色
          borderColor: '#ef232a',
          borderColor0: '#14b143'
        },
      });
      
      // 仅当指标为MA时添加MA线
      if (mainIndicator === 'MA' && indicatorData?.MA) {
        // 添加MA5线
        if (indicatorData.MA.MA5) {
          series.push({
            name: 'MA5',
            type: 'line',
            data: indicatorData.MA.MA5,
            smooth: true,
            lineStyle: {
              opacity: 0.8,
              color: '#8d4bbb',
              width: 1.5
            },
            itemStyle: {
              color: '#8d4bbb'
            },
            showSymbol: false
          });
        }
        
        // 添加MA10线
        if (indicatorData.MA.MA10) {
          series.push({
            name: 'MA10',
            type: 'line',
            data: indicatorData.MA.MA10,
            smooth: true,
            lineStyle: {
              opacity: 0.8,
              color: '#ff9900',
              width: 1.5
            },
            itemStyle: {
              color: '#ff9900'
            },
            showSymbol: false
          });
        }
        
        // 添加MA20线
        if (indicatorData.MA.MA20) {
          series.push({
            name: 'MA20',
            type: 'line',
            data: indicatorData.MA.MA20,
            smooth: true,
            lineStyle: {
              opacity: 0.8,
              color: '#cc0000',
              width: 1.5
            },
            itemStyle: {
              color: '#cc0000'
            },
            showSymbol: false
          });
        }
        
        // 添加MA30线
        if (indicatorData.MA.MA30) {
          series.push({
            name: 'MA30',
            type: 'line',
            data: indicatorData.MA.MA30,
            smooth: true,
            lineStyle: {
              opacity: 0.8,
              color: '#00994e',
              width: 1.5
            },
            itemStyle: {
              color: '#00994e'
            },
            showSymbol: false
          });
        }
      }
      // 如果需要，在这里添加其他主图指标的条件判断和相应的系列配置
      // 例如BOLL指标
      else if (mainIndicator === 'BOLL' && indicatorData?.BOLL) {
        // 添加BOLL上轨
        if (indicatorData.BOLL.UPPER) {
          series.push({
            name: 'BOLL上轨',
            type: 'line',
            data: indicatorData.BOLL.UPPER,
            smooth: true,
            lineStyle: {
              opacity: 0.7,
              color: '#ff9900',
              width: 1.5
            },
            itemStyle: {
              color: '#ff9900'
            },
            showSymbol: false
          });
        }
        
        // 添加BOLL中轨
        if (indicatorData.BOLL.MID) {
          series.push({
            name: 'BOLL中轨',
            type: 'line',
            data: indicatorData.BOLL.MID,
            smooth: true,
            lineStyle: {
              opacity: 0.7,
              color: '#8d4bbb',
              width: 1.5
            },
            itemStyle: {
              color: '#8d4bbb'
            },
            showSymbol: false
          });
        }
        
        // 添加BOLL下轨
        if (indicatorData.BOLL.LOWER) {
          series.push({
            name: 'BOLL下轨',
            type: 'line',
            data: indicatorData.BOLL.LOWER,
            smooth: true,
            lineStyle: {
              opacity: 0.7,
              color: '#ff9900',
              width: 1.5
            },
            itemStyle: {
              color: '#ff9900'
            },
            showSymbol: false
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
    <div style={{ height: chartHeight, width: '100%', position: 'relative' }}>
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

// 使用 React.memo 包装组件，避免不必要的重新渲染
export default memo(MainChartRenderer, (prevProps, nextProps) => {
  // 只有在以下属性发生变化时才重新渲染
  return (
    prevProps.selectedStock === nextProps.selectedStock &&
    prevProps.chartData === nextProps.chartData &&
    prevProps.loading === nextProps.loading &&
    prevProps.chartHeight === nextProps.chartHeight &&
    prevProps.period === nextProps.period &&
    prevProps.showTitle === nextProps.showTitle &&
    prevProps.indicatorData === nextProps.indicatorData &&
    prevProps.mainIndicator === nextProps.mainIndicator
  );
});