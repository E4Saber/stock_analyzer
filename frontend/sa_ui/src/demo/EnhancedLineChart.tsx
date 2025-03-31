import React, { useEffect, useRef, useState } from 'react';
import * as echarts from 'echarts/core';
import { LineChart as EChartsLineChart } from 'echarts/charts';
import { 
  GridComponent, 
  TooltipComponent, 
  LegendComponent, 
  TitleComponent, 
  ToolboxComponent, 
  DataZoomComponent 
} from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';

// 注册必要的组件
echarts.use([
  EChartsLineChart,
  GridComponent,
  TooltipComponent,
  LegendComponent,
  TitleComponent,
  ToolboxComponent,
  DataZoomComponent,
  CanvasRenderer
]);

export interface CPIDataPoint {
  date: string;      // 日期，格式如"2023-04"
  value: number;     // CPI值
  yoy?: number;      // 同比变化百分比
  mom?: number;      // 环比变化百分比
}

export interface CPISeriesData {
  name: string;      // 数据系列名称
  color: string;     // 线条颜色
  data: CPIDataPoint[]; // 数据点
}

export type CompareMode = 'actual' | 'yoy' | 'mom';

export interface EnhancedLineChartProps {
  series: CPISeriesData[];       // 所有数据系列 
  title?: string;                // 图表标题
  height?: number;               // 图表高度
  compareMode?: CompareMode;     // 比较模式: 'actual' | 'yoy' | 'mom'
  showTooltip?: boolean;         // 是否显示悬浮提示
  showLegend?: boolean;          // 是否显示图例
  showDataZoom?: boolean;        // 是否显示数据缩放
  showToolbox?: boolean;         // 是否显示工具箱
  smooth?: boolean;              // 是否平滑曲线
  markLine?: boolean;            // 是否显示标记线(均值等)
  enableCompareModes?: boolean;  // 是否启用比较模式选项
}

const EnhancedLineChart: React.FC<EnhancedLineChartProps> = ({
  series,
  title = 'CPI走势图',
  height = 400,
  compareMode = 'actual',
  showTooltip = true,
  showLegend = true,
  showDataZoom = true,
  showToolbox = true,
  smooth = true,
  markLine = false,
  enableCompareModes = true,
}) => {
  const chartRef = useRef<HTMLDivElement>(null);
  const chartInstance = useRef<echarts.ECharts | null>(null);
  const [currentCompareMode, setCurrentCompareMode] = useState<CompareMode>(compareMode);
  const [zoomRatio, setZoomRatio] = useState<number>(100);  // 跟踪缩放比例
  
  // 处理比较模式变更
  const handleCompareModeChange = (mode: CompareMode) => {
    setCurrentCompareMode(mode);
  };
  
  // 主动调整图表大小的函数
  const resizeChart = () => {
    if (chartInstance.current) {
      chartInstance.current.resize();
    }
  };

  // 监听容器大小变化
  useEffect(() => {
    if (typeof ResizeObserver !== 'undefined') {
      const container = chartRef.current;
      if (container) {
        const observer = new ResizeObserver(() => {
          resizeChart();
        });
        
        observer.observe(container);
        
        return () => {
          observer.disconnect();
        };
      }
    }
  }, []);
  
  // 在组件属性更新后也调整图表大小
  useEffect(() => {
    resizeChart();
  }, [height, showLegend]);
  
  // 初始化图表
  useEffect(() => {
    if (chartRef.current) {
      // 销毁之前的实例
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
      
      // 设置图表实例的事件监听
      if (chartInstance.current) {
        // 监听图例选择变化
        chartInstance.current.on('legendselectchanged', () => {
          chartInstance.current && chartInstance.current.resize();
        });
        
        // 监听缩放事件
        chartInstance.current.on('datazoom', (params) => {
          // 获取当前缩放比例
          const zoomEnd = params.batch ? params.batch[0].end : params.end || 100;
          const zoomStart = params.batch ? params.batch[0].start : params.start || 0;
          const newZoomRatio = zoomEnd - zoomStart;
          
          // 更新状态
          setZoomRatio(newZoomRatio);
          
          // 当缩放比例变化时更新坐标轴标签
          updateAxisLabels(newZoomRatio);
        });
      }
      
      // 清理函数
      return () => {
        window.removeEventListener('resize', handleResize);
        if (chartInstance.current) {
          chartInstance.current.dispose();
        }
      };
    }
  }, []);
  
  // 根据缩放比例获取轴标签配置
  const getAxisLabelConfig = (allDates: string[], currentZoomRatio: number) => {
    return {
      formatter: (value: string) => {
        if (!value.includes('-')) return value;
        
        const parts = value.split('-');
        const year = parts[0];
        const month = parts[1];

        // 基于缩放比例调整标签显示策略
        if (currentZoomRatio > 80) {
          // 未缩放或缩放很少时，只显示年份标签（在1月处）
          return month === '01' ? year : '';
        } else if (currentZoomRatio > 50) {
          // 中等缩放程度，显示季度标签
          return ['01', '04', '07', '10'].includes(month) ? `${year.substr(2)}/${month}` : '';
        } else if (currentZoomRatio > 30) {
          // 较大缩放程度，每两个月显示一次
          return parseInt(month) % 2 === 1 ? `${year.substr(2)}/${month}` : '';
        } else {
          // 高度放大，显示所有月份
          return `${year.substr(2)}/${month}`;
        }
      },
      margin: 15,
      rotate: 45,  // 标签倾斜以节省空间
      hideOverlap: true,
      interval: 'auto'  // 允许echarts自动调整间隔
    };
  };
  
  // 更新坐标轴标签的函数
  const updateAxisLabels = (currentZoomRatio: number) => {
    if (chartInstance.current && series && series.length > 0) {
      // 获取所有日期
      const allDates = Array.from(
        new Set(
          series.flatMap(s => s.data.map(d => d.date))
        )
      ).sort();
      
      // 更新坐标轴标签
      chartInstance.current.setOption({
        xAxis: {
          axisLabel: getAxisLabelConfig(allDates, currentZoomRatio)
        }
      });
    }
  };

  // 更新图表数据
  useEffect(() => {
    if (chartInstance.current && series && series.length > 0) {
      // 获取所有系列的日期，并去重排序
      const allDates = Array.from(
        new Set(
          series.flatMap(s => s.data.map(d => d.date))
        )
      ).sort();
      
      // 处理显示模式(实际值/同比/环比)
      const valueKey = currentCompareMode === 'yoy' 
        ? 'yoy' 
        : currentCompareMode === 'mom' 
          ? 'mom' 
          : 'value';
      
      // 格式化标题
      let formattedTitle = title;
      if (currentCompareMode === 'yoy') {
        formattedTitle += ' - 同比(%)';
      } else if (currentCompareMode === 'mom') {
        formattedTitle += ' - 环比(%)';
      }
      // 实际值模式不添加后缀
      
      // 构建ECharts系列数据
      const seriesData = series.map(s => {
        // 创建数据映射以便快速查找
        const dataMap = new Map(s.data.map(d => [d.date, d]));
        
        return {
          name: s.name,
          type: 'line',
          data: allDates.map(date => {
            const dataPoint = dataMap.get(date);
            if (dataPoint) {
              return [date, dataPoint[valueKey]];
            }
            return [date, null]; // 对于没有数据的日期，用null代替
          }),
          smooth: smooth,
          itemStyle: {
            color: s.color
          },
          markLine: markLine ? {
            data: [
              { type: 'average', name: '平均值' }
            ]
          } : undefined
        };
      });
      
      // 构建图表配置项
      const options = {
        title: {
          text: formattedTitle,
          left: 'center', 
          top: 10,      // 确保标题在顶部有适当的空间
          textStyle: {
            fontSize: 16,
            fontWeight: 'normal'
          }
        },
        backgroundColor: 'transparent',  // 透明背景，避免遮挡自定义按钮
        tooltip: showTooltip ? {
          trigger: 'axis',
          formatter: (params: any) => {
            let tooltip = `<div style="font-weight:bold;margin-bottom:5px;">${params[0].axisValue}</div>`;
            params.forEach((param: any) => {
              tooltip += `<div style="margin: 3px 0;">
                <span style="display:inline-block;width:10px;height:10px;border-radius:50%;background-color:${param.color};margin-right:5px;"></span>
                <span>${param.seriesName}: </span>
                <span style="float:right;font-weight:bold;margin-left:15px;">
                  ${param.value[1] !== null ? param.value[1].toFixed(2) : '-'}
                  ${currentCompareMode !== 'actual' ? '%' : ''}
                </span>
              </div>`;
            });
            return tooltip;
          }
        } : false,
        legend: showLegend ? {
          data: series.map(s => s.name),
          orient: 'vertical',
          left: '0%',   // 将图例移到最左侧
          top: 'middle',
          textStyle: {
            fontSize: 12
          },
          itemGap: 12,  // 增加图例项之间的间距
          itemStyle: {
            borderWidth: 0  // 移除图例标记的边框
          },
          formatter: name => {
            // 控制图例文本长度，防止过长
            return name.length > 10 ? name.slice(0, 10) + '...' : name;
          }
        } : false,
        grid: {
          left: showLegend ? '10%' : '3%',  // 减小左侧空白区域
          right: '8%',         // 增加右侧边距，为按钮留出更多空间
          top: '60px',         // 使用固定像素值而不是百分比
          bottom: showDataZoom ? '15%' : '10%',
          containLabel: true   // 确保坐标轴标签包含在内
        },
        toolbox: showToolbox ? {
          feature: {
            saveAsImage: { title: '保存为图片' },
            dataView: { title: '数据视图', lang: ['数据视图', '关闭', '刷新'] },
            restore: { title: '还原' },
            dataZoom: { title: { zoom: '区域缩放', back: '区域还原' } },
          },
          right: 60
        } : false,
        dataZoom: showDataZoom ? [
          { 
            type: 'slider', 
            show: true, 
            xAxisIndex: [0], 
            start: 0, 
            end: 100,
            labelFormatter: (value: number) => {
              // 自定义缩放滑块的标签格式
              const dateStr = allDates[Math.floor(value / 100 * (allDates.length - 1))];
              if (dateStr && dateStr.includes('-')) {
                const parts = dateStr.split('-');
                return `${parts[0].substr(2)}/${parts[1]}`;
              }
              return '';
            }
          },
          { 
            type: 'inside', 
            xAxisIndex: [0], 
            start: 0, 
            end: 100 
          }
        ] : [],
        xAxis: {
          type: 'category',
          data: allDates,
          boundaryGap: false,
          axisLabel: getAxisLabelConfig(allDates, zoomRatio),
          axisTick: {
            alignWithLabel: true,  // 刻度线与标签对齐
          },
          // 确保坐标轴指示器显示完整信息
          axisPointer: {
            label: {
              formatter: (params: any) => {
                if (params.value && params.value.includes('-')) {
                  const parts = params.value.split('-');
                  return `${parts[0]}年${parts[1]}月`;
                }
                return params.value;
              },
              show: true
            }
          }
        },
        yAxis: {
          type: 'value',
          axisLabel: {
            formatter: (value: number) => {
              return currentCompareMode !== 'actual' 
                ? `${value.toFixed(1)}%` 
                : value.toFixed(1);
            }
          }
        },
        series: seriesData
      };
      
      // 设置图表选项
      chartInstance.current.setOption(options, true);
      
      // 手动调整大小以确保正确渲染
      setTimeout(() => {
        resizeChart();
      }, 50);
    }
  }, [series, title, currentCompareMode, showTooltip, showLegend, showDataZoom, showToolbox, smooth, markLine]);

  return (
    <div style={{ width: '100%' }}>
      {/* 比较模式按钮组 - 放在ECharts外部 */}
      {enableCompareModes && (
        <div style={{
          display: 'flex',
          justifyContent: 'flex-end',
          marginBottom: '10px'
        }}>
          <div style={{ 
            display: 'flex',
            border: '1px solid #ddd',
            borderRadius: '3px',
            overflow: 'hidden'
          }}>
            <div 
              onClick={() => handleCompareModeChange('actual')}
              style={{
                padding: '4px 12px',
                fontSize: '13px',
                cursor: 'pointer',
                backgroundColor: currentCompareMode === 'actual' ? '#1890ff' : '#fff',
                color: currentCompareMode === 'actual' ? 'white' : '#333',
                borderRight: '1px solid #ddd'
              }}
            >
              实际值
            </div>
            
            {series.length <= 2 && (
              <>
                <div 
                  onClick={() => handleCompareModeChange('yoy')}
                  style={{
                    padding: '4px 12px',
                    fontSize: '13px',
                    cursor: 'pointer',
                    backgroundColor: currentCompareMode === 'yoy' ? '#1890ff' : '#fff',
                    color: currentCompareMode === 'yoy' ? 'white' : '#333',
                    borderRight: '1px solid #ddd'
                  }}
                >
                  同比
                </div>
                <div 
                  onClick={() => handleCompareModeChange('mom')}
                  style={{
                    padding: '4px 12px',
                    fontSize: '13px',
                    cursor: 'pointer',
                    backgroundColor: currentCompareMode === 'mom' ? '#1890ff' : '#fff',
                    color: currentCompareMode === 'mom' ? 'white' : '#333'
                  }}
                >
                  环比
                </div>
              </>
            )}
          </div>
        </div>
      )}
      
      {/* 图表容器 */}
      <div 
        ref={chartRef} 
        style={{ width: '100%', height: `${height}px` }}
      />
    </div>
  );
};

export default EnhancedLineChart;