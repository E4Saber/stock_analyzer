// src/utils/chartOptions.ts
/**
 * 图表配置生成工具
 * 封装了生成各种类型图表配置的函数
 */
import * as echarts from 'echarts/core';
import { 
  DataPoint, 
  ChartOptionsParams, 
  CompareModeType, 
  RelatedIndicatorType 
} from '../types/indicator';

interface SeriesItem {
  name: string;
  type: 'line' | 'bar';
  data: [string, number][];
  smooth: boolean;
  symbol: string;
  symbolSize: number;
  lineStyle?: {
    width: number;
  };
  itemStyle?: {
    color?: string;
    borderRadius?: number[];
  };
  barMaxWidth?: number;
}

// 生成折线图配置
export const generateLineOptions = ({
  data,
  title,
  compareMode = 'actual', // 'actual', 'yoy', 'mom'
  showTooltip = true,
  showLegend = false,
  showDataZoom = false,
  showToolbox = false,
  compareWith = [], // 用于对比的其他指标数据
}: ChartOptionsParams): echarts.EChartsOption => {
  // 根据比较模式确定使用的数据字段和单位
  const getValueField = (): keyof DataPoint => {
    switch (compareMode) {
      case 'yoy':
        return 'yoy';
      case 'mom':
        return 'mom';
      default:
        return 'value';
    }
  };
  
  const getUnit = (): string => {
    if (compareMode === 'yoy' || compareMode === 'mom') {
      return '%';
    }
    return (data && data.length > 0 && 'unit' in data[0]) ? (data[0] as any).unit || '' : '';
  };
  
  const valueField = getValueField();
  const unit = getUnit();
  
  // 准备主数据系列
  const mainSeries: SeriesItem = {
    name: title || '数据',
    type: 'line',
    data: data.map(item => [item.date, item[valueField]]),
    smooth: true,
    symbol: 'emptyCircle',
    symbolSize: 4,
    lineStyle: {
      width: 2
    },
    itemStyle: {
      color: '#1890ff'
    }
  };
  
  // 准备对比数据系列
  const compareSeries: SeriesItem[] = compareWith.map(item => ({
    name: item.name,
    type: 'line',
    data: (item.chartData as DataPoint[]).map(dataPoint => [dataPoint.date, dataPoint[valueField]]),
    smooth: true,
    symbol: 'emptyCircle',
    symbolSize: 4,
    lineStyle: {
      width: 2
    }
  }));
  
  // 合并所有数据系列
  const series: SeriesItem[] = [mainSeries, ...compareSeries];
  
  // 构建基本选项
  const options: echarts.EChartsOption = {
    title: {
      text: title,
      show: !!title,
      left: 'center',
      textStyle: {
        fontSize: 16,
        fontWeight: 'normal'
      }
    },
    tooltip: {
      trigger: 'axis',
      formatter: function(params: any) {
        // 构建tooltip内容
        let result = `<div style="font-weight:bold;margin-bottom:5px;">${params[0].axisValue}</div>`;
        
        params.forEach((param: any) => {
          result += `
            <div style="margin: 3px 0;">
              <span style="display:inline-block;margin-right:5px;border-radius:50%;width:10px;height:10px;background-color:${param.color};"></span>
              <span>${param.seriesName}: </span>
              <span style="float:right;margin-left:20px;font-weight:bold;">
                ${param.value[1].toFixed(2)}${unit}
              </span>
            </div>
          `;
        });
        
        return result;
      },
      axisPointer: {
        type: 'cross',
        label: {
          backgroundColor: '#6a7985'
        }
      },
      show: showTooltip
    },
    legend: {
      data: series.map(item => item.name),
      type: 'scroll',
      bottom: 0,
      show: showLegend || compareWith.length > 0
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: showLegend ? '10%' : '3%',
      top: '8%',
      containLabel: true
    },
    xAxis: {
      type: 'time',
      boundaryGap: false,
      axisLine: {
        lineStyle: {
          color: '#ddd'
        }
      },
      axisLabel: {
        formatter: '{yyyy}-{MM}'
      },
      splitLine: {
        show: true,
        lineStyle: {
          type: 'dashed',
          color: '#eee'
        }
      }
    },
    yAxis: {
      type: 'value',
      axisLine: {
        show: false
      },
      axisTick: {
        show: false
      },
      axisLabel: {
        formatter: `{value}${unit}`
      },
      splitLine: {
        lineStyle: {
          type: 'dashed',
          color: '#eee'
        }
      }
    },
    series: series
  };
  
  // 添加数据缩放组件（可选）
  if (showDataZoom) {
    options.dataZoom = [
      {
        type: 'inside',
        start: 0,
        end: 100
      },
      {
        type: 'slider',
        start: 0,
        end: 100,
        height: 20,
        bottom: 0,
        borderColor: '#ddd',
        fillerColor: 'rgba(24, 144, 255, 0.1)',
        handleStyle: {
          color: '#1890ff'
        }
      }
    ];
  }
  
  // 添加工具箱组件（可选）
  if (showToolbox) {
    options.toolbox = {
      feature: {
        dataZoom: {
          yAxisIndex: 'none'
        },
        restore: {},
        saveAsImage: {}
      },
      right: 20,
      top: 20
    };
  }
  
  return options;
};

// 生成柱状图配置
export const generateBarOptions = (params: ChartOptionsParams): echarts.EChartsOption => {
  // 使用类似折线图的逻辑，但修改图表类型为柱状图
  const lineOptions = generateLineOptions(params);
  
  // 将series类型更改为bar
  if (lineOptions.series) {
    lineOptions.series = (lineOptions.series as SeriesItem[]).map(series => ({
      ...series,
      type: 'bar',
      barMaxWidth: 30, // 限制柱状的最大宽度
      itemStyle: {
        borderRadius: [3, 3, 0, 0] // 给柱状图顶部添加圆角
      }
    })) as any;
  }
  
  // 为柱状图特别调整的一些配置
  if (lineOptions.xAxis && typeof lineOptions.xAxis === 'object') {
    lineOptions.xAxis = {
      ...lineOptions.xAxis,
      boundaryGap: true
    };
  }
  
  return lineOptions;
};

// 生成对比图表配置
export const generateComparisonOptions = ({
  data,
  compareWith,
  title,
  compareMode = 'actual', // 'actual', 'yoy', 'mom'
}: {
  data: DataPoint[];
  compareWith: RelatedIndicatorType[];
  title?: string;
  compareMode?: CompareModeType;
}): echarts.EChartsOption => {
  // 对比图表可能需要更复杂的配置
  // 这里使用折线图配置作为基础，但可以根据需要进行进一步定制
  return generateLineOptions({
    data,
    title,
    compareMode,
    showTooltip: true,
    showLegend: true,
    showDataZoom: true,
    showToolbox: true,
    compareWith
  });
};