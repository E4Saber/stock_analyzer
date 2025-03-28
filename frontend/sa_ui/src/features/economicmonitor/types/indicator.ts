// src/types/indicator.ts

// 指标数据点类型
export interface DataPoint {
    date: string;
    value: number;
    yoy: number;
    mom: number;
  }
  
  // 指标构成数据类型
  export interface CompositionItem {
    name: string;
    value: number;
  }
  
  // 迷你图表数据点类型
  export interface TrendPoint {
    x: number;
    y: number;
  }
  
  // 指标状态类型
  export type IndicatorStatus = 'normal' | 'warning' | 'alert';
  
  // 变化类型
  export type ChangeType = 'increase' | 'decrease' | 'stable';
  
  // 趋势类型
  export type TrendType = 'up' | 'down' | 'flat';
  
  // 地区类型
  export type RegionType = 'us' | 'china' | 'cross';
  
  // 指标分类类型
  export type CategoryType = 
    | 'growth' 
    | 'employment' 
    | 'price' 
    | 'consumption' 
    | 'production' 
    | 'finance' 
    | 'trade'
    | 'other';
  
  // 时间范围类型
  export type TimeRangeType = '1m' | '3m' | '6m' | '1y' | '3y' | '5y';
  
  // 比较模式类型
  export type CompareModeType = 'actual' | 'yoy' | 'mom';
  
  // 显示类型
  export type DisplayType = 'line' | 'bar';
  
  // 仪表盘指标类型
  export interface IndicatorType {
    id: string;
    name: string;
    value: number;
    unit: string;
    change: number;
    changeType: ChangeType;
    status: IndicatorStatus;
    trend: TrendPoint[];
    region: RegionType;
    category: CategoryType;
    updateTime: string;
  }
  
  // 指标详细数据类型
  export interface IndicatorDetailType extends IndicatorType {
    description: string;
    frequency: string;
    source: string;
    sourceUrl: string;
    previous: number;
    expected: number;
    yoy: number;
    mom: number;
    max: number;
    min: number;
    avg: number;
    trend: TrendType;
    chartData: DataPoint[];
    tableData: DataPoint[];
    composition?: CompositionItem[];
  }
  
  // 相关指标类型
  export interface RelatedIndicatorType {
    id: string;
    name: string;
    current: number;
    unit: string;
    trend: TrendType;
    category: CategoryType;
    frequency: string;
    chartData: DataPoint[] | TrendPoint[];
  }
  
  // 组件属性类型
  
  // 仪表盘Tab属性
  export interface DashboardTabProps {
    onIndicatorSelect: (indicator: IndicatorType) => void;
  }
  
  // 指标详情页属性
  export interface IndicatorDetailProps {
    indicator: IndicatorType;
    onBack: () => void;
  }
  
  // 地区经济指标Tab属性
  export interface RegionTabProps {
    onIndicatorSelect: (indicator: IndicatorType) => void;
  }
  
  // 指标卡片属性
  export interface IndicatorCardProps {
    indicator: IndicatorType;
    onClick: (indicator: IndicatorType) => void;
    farther?: string
  }
  
  // 数据摘要卡片属性
  export interface DataSummaryCardProps {
    title: string;
    data: {
      max: number;
      min: number;
      avg: number;
      trend: TrendType;
    };
    style?: React.CSSProperties;
  }
  
  // 对比选择器属性
  export interface CompareSelectProps {
    currentIndicator: IndicatorType;
    relatedIndicators: RelatedIndicatorType[];
    selectedIndicators: RelatedIndicatorType[];
    onConfirm: (indicators: RelatedIndicatorType[]) => void;
    onCancel: () => void;
    maxSelect?: number;
  }
  
  // 线图属性
  export interface LineChartProps {
    data: DataPoint[];
    title?: string;
    height?: number;
    compareMode?: CompareModeType;
    showTooltip?: boolean;
    showLegend?: boolean;
    showDataZoom?: boolean;
    showToolbox?: boolean;
    compareWith?: RelatedIndicatorType[];
  }
  
  // 柱状图属性
  export interface BarChartProps extends LineChartProps {}
  
  // 迷你图表属性
  export interface MiniChartProps {
    data: DataPoint[] | TrendPoint[];
    height?: number;
    color?: string;
  }
  
  // 图表选项生成函数参数
  export interface ChartOptionsParams {
    data: DataPoint[];
    title?: string;
    compareMode?: CompareModeType;
    showTooltip?: boolean;
    showLegend?: boolean;
    showDataZoom?: boolean;
    showToolbox?: boolean;
    compareWith?: RelatedIndicatorType[];
  }