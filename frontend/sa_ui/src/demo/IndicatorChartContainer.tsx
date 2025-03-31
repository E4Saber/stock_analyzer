// src/containers/IndicatorChartContainer.tsx
import React, { useState, useEffect } from 'react';
import EnhancedLineChart, { CPISeriesData } from './EnhancedLineChart';
import indicatorApi, { IndicatorType, IndicatorMetadata } from './indicatorApi';
import { message, Spin, Select, Radio, Space, Button, Card, Divider, Typography } from 'antd';

const { Option } = Select;
const { Text, Title, Paragraph } = Typography;

interface IndicatorChartContainerProps {
  indicatorType: IndicatorType;
  title?: string;
  defaultYear?: number;
  height?: number;
  showToolbar?: boolean;
}

const IndicatorChartContainer: React.FC<IndicatorChartContainerProps> = ({ 
  indicatorType,
  title,
  defaultYear = null, 
  height = 450,
  showToolbar = true
}) => {
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedSeries, setSelectedSeries] = useState<string[]>([]);
  const [availableSeries, setAvailableSeries] = useState<string[]>([]);
  const [selectedYear, setSelectedYear] = useState<number | null>(defaultYear);
  const [allYears, setAllYears] = useState<number[]>([]);
  const [indicatorData, setIndicatorData] = useState<CPISeriesData[]>([]);
  const [metadata, setMetadata] = useState<IndicatorMetadata | null>(null);
  
  // 获取指标元数据
  useEffect(() => {
    const fetchMetadata = async () => {
      try {
        const data = await indicatorApi.getIndicatorMetadata(indicatorType);
        setMetadata(data);
        
        // 默认选择第一个可用系列
        if (data.available_series && data.available_series.length > 0) {
          setSelectedSeries([data.available_series[0]]);
          setAvailableSeries(data.available_series);
        }
      } catch (error) {
        message.error(`获取${indicatorType}元数据失败`);
        console.error(error);
      }
    };
    
    fetchMetadata();
  }, [indicatorType]);

  // 生成年份范围
  useEffect(() => {
    // 假设数据从2000年到当前年份
    const currentYear = new Date().getFullYear();
    const years = Array.from({ length: currentYear - 1999 }, (_, i) => 2000 + i);
    setAllYears(years);
  }, []);

  // 获取指标数据
  const fetchIndicatorData = async () => {
    setLoading(true);
    try {
      let apiData;
      
      if (selectedYear) {
        // 获取特定年份的数据
        apiData = await indicatorApi.getIndicatorDataByYear(
          indicatorType, 
          selectedYear,
          selectedSeries.length > 0 ? selectedSeries : undefined
        );
      } else {
        // 获取所有数据
        apiData = await indicatorApi.getIndicatorData(
          indicatorType,
          { series: selectedSeries.length > 0 ? selectedSeries : undefined }
        );
      }
      
      // 转换数据为图表所需格式
      const formattedData = indicatorApi.formatForChart(apiData, selectedSeries);
      setIndicatorData(formattedData);
    } catch (error) {
      message.error(`获取${indicatorType}数据失败，请稍后重试`);
      console.error('获取指标数据失败:', error);
    } finally {
      setLoading(false);
    }
  };
  
  // 组件挂载和依赖项变化时获取数据
  useEffect(() => {
    if (selectedSeries.length > 0) {
      fetchIndicatorData();
    }
  }, [selectedYear, selectedSeries, indicatorType]);

  // 处理系列选择变化
  const handleSeriesChange = (selected: string[]) => {
    // 确保至少选择一个系列
    if (selected.length === 0) {
      message.info('请至少选择一个数据系列');
      return;
    }
    setSelectedSeries(selected);
  };

  // 处理年份选择变化
  const handleYearChange = (year: number | null) => {
    setSelectedYear(year);
  };

  // 格式化系列名称，用于显示在下拉选择框中
  const formatSeriesName = (seriesKey: string): string => {
    const nameMap: { [key: string]: string } = {
      // CPI
      'national': '全国CPI',
      'urban': '城市CPI',
      'rural': '农村CPI',
      
      // GDP
      'gdp': 'GDP总量',
      'primaryIndustry': '第一产业',
      'secondaryIndustry': '第二产业',
      'tertiaryIndustry': '第三产业',
      
      // 货币供应量
      'm0': 'M0货币供应量',
      'm1': 'M1货币供应量',
      'm2': 'M2货币供应量',
      
      // PMI
      'manufacturingPMI': '制造业PMI',
      'nonmanufacturingPMI': '非制造业PMI',
      'compositePMI': '综合PMI'
    };
    
    return nameMap[seriesKey] || seriesKey;
  };

  // 获取指标显示标题
  const getDisplayTitle = (): string => {
    if (title) return title;
    
    if (metadata) {
      return `${metadata.name}走势${selectedYear ? ` (${selectedYear}年)` : ''}`;
    }
    
    const indicatorNames: { [key in IndicatorType]: string } = {
      'cpi': '消费者价格指数(CPI)',
      'gdp': '国内生产总值(GDP)',
      'm': '货币供应量',
      'pmi': '采购经理人指数(PMI)'
    };
    
    return `${indicatorNames[indicatorType]}走势${selectedYear ? ` (${selectedYear}年)` : ''}`;
  };

  return (
    <div style={{ padding: showToolbar ? '20px' : '0' }}>
      {showToolbar && (
        <>
          <h2>{getDisplayTitle()}</h2>
          
          <div style={{ marginBottom: '20px' }}>
            <div style={{ marginBottom: '10px' }}>
              <Space align="center">
                <Text strong>选择数据系列:</Text>
                <Select
                  mode="multiple"
                  style={{ width: '400px' }}
                  placeholder="选择数据系列"
                  value={selectedSeries}
                  onChange={handleSeriesChange}
                  optionLabelProp="label"
                >
                  {availableSeries.map(series => (
                    <Option key={series} value={series} label={formatSeriesName(series)}>
                      {formatSeriesName(series)}
                    </Option>
                  ))}
                </Select>
              </Space>
            </div>
            
            <div>
              <Space align="center">
                <Text strong>按年份筛选:</Text>
                <Radio.Group value={selectedYear} onChange={e => handleYearChange(e.target.value)}>
                  <Radio.Button value={null}>全部</Radio.Button>
                  {allYears.slice(-5).map(year => (
                    <Radio.Button key={year} value={year}>{year}年</Radio.Button>
                  ))}
                </Radio.Group>
                
                {allYears.length > 5 && (
                  <Select
                    style={{ width: '120px' }}
                    placeholder="更多年份"
                    value={selectedYear && !allYears.slice(-5).includes(selectedYear) ? selectedYear : undefined}
                    onChange={handleYearChange}
                    allowClear
                  >
                    {allYears.slice(0, -5).map(year => (
                      <Option key={year} value={year}>{year}年</Option>
                    ))}
                  </Select>
                )}
              </Space>
            </div>
          </div>
        </>
      )}
      
      {/* 显示指标图表 */}
      <div style={{ width: '100%', boxSizing: 'border-box' }}>
        {loading ? (
          <div style={{ height: `${height}px`, display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
            <Spin tip={`加载${metadata?.name || '指标'}数据中...`} />
          </div>
        ) : (
          <EnhancedLineChart
            series={indicatorData}
            title={getDisplayTitle()}
            height={height}
            showDataZoom={true}
            showToolbox={true}
            markLine={true}
            enableCompareModes={true}
          />
        )}
      </div>
      
      {showToolbar && metadata && (
        <div style={{ marginTop: '20px', fontSize: '14px', color: '#666' }}>
          <Divider />
          
          <Space direction="vertical" style={{ width: '100%' }}>
            <Paragraph>
              <Text strong>指标说明: </Text>
              {metadata.description}
            </Paragraph>
            
            <Space>
              <Text strong>数据频率: </Text>
              <Text>{metadata.frequency}</Text>
              
              <Divider type="vertical" />
              
              <Text strong>数据来源: </Text>
              <Text>{metadata.source}</Text>
            </Space>
          </Space>
        </div>
      )}
    </div>
  );
};

export default IndicatorChartContainer;