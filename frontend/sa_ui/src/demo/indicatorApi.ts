// src/services/api/indicatorApi.ts
import axios from 'axios';
import { CPISeriesData } from './EnhancedLineChart';

// API基础URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

// 支持的指标类型
export type IndicatorType = 'cpi' | 'gdp' | 'm' | 'pmi';

// 指标元数据接口
export interface IndicatorMetadata {
  name: string;
  description: string;
  frequency: string;
  available_series: string[];
  date_format: string;
  source: string;
}

// 指标元数据映射接口
export interface IndicatorsMetadata {
  [key: string]: IndicatorMetadata;
}

// 指标数据接口
export interface IndicatorData {
  [seriesKey: string]: CPISeriesData;
}

// 指标API服务
const indicatorApi = {
  /**
   * 获取指标数据
   * @param indicatorType 指标类型
   * @param params 查询参数
   * @returns Promise<IndicatorData>
   */
  getIndicatorData: async (
    indicatorType: IndicatorType,
    params?: {
      year?: number;
      start_period?: string;
      end_period?: string;
      limit?: number;
      series?: string[];
    }
  ): Promise<IndicatorData> => {
    try {
      const response = await axios.get(`${API_BASE_URL}/macroeconomics/indicators/data/${indicatorType}`, { 
        params,
        // 如果series是数组，需要特殊处理
        paramsSerializer: params => {
          const searchParams = new URLSearchParams();
          
          // 手动添加每个参数
          for (const [key, value] of Object.entries(params || {})) {
            if (Array.isArray(value)) {
              // 对于数组，为每个值添加同名参数
              value.forEach(item => {
                searchParams.append(key, item);
              });
            } else if (value !== undefined) {
              searchParams.append(key, String(value));
            }
          }
          
          return searchParams.toString();
        }
      });
      return response.data;
    } catch (error) {
      console.error(`获取${indicatorType}数据失败:`, error);
      throw error;
    }
  },

  /**
   * 获取所有支持的指标的元数据
   * @returns Promise<IndicatorsMetadata>
   */
  getIndicatorsMetadata: async (): Promise<IndicatorsMetadata> => {
    try {
      const response = await axios.get(`${API_BASE_URL}/macroeconomics/indicators/metadata`);
      return response.data;
    } catch (error) {
      console.error('获取指标元数据失败:', error);
      throw error;
    }
  },

  /**
   * 根据指标类型获取特定的元数据
   * @param indicatorType 指标类型
   * @returns Promise<IndicatorMetadata>
   */
  getIndicatorMetadata: async (indicatorType: IndicatorType): Promise<IndicatorMetadata> => {
    try {
      const metadata = await indicatorApi.getIndicatorsMetadata();
      if (!metadata[indicatorType]) {
        throw new Error(`不支持的指标类型: ${indicatorType}`);
      }
      return metadata[indicatorType];
    } catch (error) {
      console.error(`获取${indicatorType}元数据失败:`, error);
      throw error;
    }
  },

  /**
   * 获取特定年份的指标数据
   * @param indicatorType 指标类型
   * @param year 年份
   * @param series 可选的系列限制
   * @returns Promise<IndicatorData>
   */
  getIndicatorDataByYear: async (
    indicatorType: IndicatorType,
    year: number,
    series?: string[]
  ): Promise<IndicatorData> => {
    return indicatorApi.getIndicatorData(indicatorType, { year, series });
  },

  /**
   * 获取特定日期范围的指标数据
   * @param indicatorType 指标类型
   * @param startPeriod 开始期间
   * @param endPeriod 结束期间
   * @param series 可选的系列限制
   * @returns Promise<IndicatorData>
   */
  getIndicatorDataByRange: async (
    indicatorType: IndicatorType,
    startPeriod: string,
    endPeriod: string,
    series?: string[]
  ): Promise<IndicatorData> => {
    return indicatorApi.getIndicatorData(indicatorType, { 
      start_period: startPeriod, 
      end_period: endPeriod,
      series 
    });
  },
  
  /**
   * 将API返回的数据转换为图表组件所需的格式
   * @param data 指标数据
   * @param selectedSeries 选择的系列
   * @returns 图表组件数据
   */
  formatForChart: (data: IndicatorData, selectedSeries?: string[]): CPISeriesData[] => {
    // 如果指定了系列，只返回这些系列
    if (selectedSeries && selectedSeries.length > 0) {
      return selectedSeries
        .filter(series => data[series]) // 过滤掉不存在的系列
        .map(series => data[series]);
    }
    
    // 否则返回所有系列
    return Object.values(data);
  }
};

export default indicatorApi;