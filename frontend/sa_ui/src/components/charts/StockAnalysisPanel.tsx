// src/components/charts/StockAnalysisPanel.tsx
import React, { useState, useEffect, useRef } from 'react';
import { 
  Card, Radio, Spin, Empty, Dropdown, Button, Space, Select,
  Row, Col, Typography, DatePicker, Tooltip, Tag
} from 'antd';
import { 
  LineChartOutlined, BarChartOutlined, 
  DownOutlined, ReloadOutlined, FullscreenOutlined, 
  PlusOutlined, SettingOutlined
} from '@ant-design/icons';
import { getStockKline, getStockIndicators } from '../../services/mock/mockStockService';
import MainChartRenderer from './MainChartRenderer';
import IndicatorChartRenderer from './IndicatorChartRenderer';
import { 
  StockData, ChartType, PeriodType, IndicatorType, IndicatorPanelConfig,
  periodMap, getAvailableIndicators, getDefaultIndicatorPanels
} from './config/chartConfig';
import type { RadioChangeEvent } from 'antd';
import moment from 'moment';

const { Title, Text } = Typography;
const { Option } = Select;

// 自定义图表类型图标
const CandlestickOutlined = () => (
  <svg viewBox="0 0 1024 1024" width="1em" height="1em" fill="currentColor">
    <path d="M184 352h-48c-4.4 0-8 3.6-8 8v304c0 4.4 3.6 8 8 8h48c4.4 0 8-3.6 8-8V360c0-4.4-3.6-8-8-8zm736 0h-48c-4.4 0-8 3.6-8 8v304c0 4.4 3.6 8 8 8h48c4.4 0 8-3.6 8-8V360c0-4.4-3.6-8-8-8zM504.3 620.8l-110 66c-15.4 9.2-35.2-2.4-35.2-20.7V359.9c0-18.3 19.8-29.9 35.2-20.7l110 66c13.9 8.4 13.9 29.2 0 37.6-14 8.4-14 29.2 0 37.6 13.9 8.4 13.9 29.2 0 37.6-14 8.4-14 29.3 0 37.7 13.9 8.4 13.9 29.2 0 37.6-14 8.4-14 29.2 0 37.5z" />
  </svg>
);

// 组件属性定义
interface StockAnalysisPanelProps {
  stocks: StockData[];
  defaultStock?: string;
  height?: number;
  showHeader?: boolean;
  showTitle?: boolean;
  defaultPeriod?: PeriodType;
  defaultChartType?: ChartType;
  fullWidth?: boolean;
  onStockChange?: (code: string) => void;
}

const StockAnalysisPanel: React.FC<StockAnalysisPanelProps> = ({
  stocks,
  defaultStock,
  height = 600,
  showHeader = true,
  showTitle = true,
  defaultPeriod = 'day',
  defaultChartType = 'candle',
  fullWidth = false,
  onStockChange
}) => {
  // 基本状态
  const [selectedStock, setSelectedStock] = useState<string>(defaultStock || (stocks[0]?.code || ''));
  const [mainChartData, setMainChartData] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [period, setPeriod] = useState<PeriodType>(defaultPeriod);
  const [chartType, setChartType] = useState<ChartType>(defaultChartType);
  const [dateRange, setDateRange] = useState<[moment.Moment, moment.Moment] | null>(null);
  const [isFullscreen, setIsFullscreen] = useState<boolean>(false);

  // 技术指标相关状态
  const [indicatorPanels, setIndicatorPanels] = useState<IndicatorPanelConfig[]>(getDefaultIndicatorPanels());
  const [indicatorData, setIndicatorData] = useState<Record<IndicatorType, any>>({});
  const [availableIndicators] = useState<IndicatorType[]>(getAvailableIndicators());
  
  // 比较功能相关状态
  const [compareMode, setCompareMode] = useState<boolean>(false);
  const [comparedStocks, setComparedStocks] = useState<string[]>([]);
  const [comparedData, setComparedData] = useState<Record<string, any[]>>({});

  // 图表引用
  const mainChartRef = useRef<any>(null);
  const indicatorChartRefs = useRef<Record<IndicatorType, any>>({});

  // 获取股票K线数据
  useEffect(() => {
    if (!selectedStock) return;
    
    const fetchStockData = async () => {
      setLoading(true);
      try {
        const apiPeriod = periodMap[period];
        
        // 获取K线数据
        const response = await getStockKline(selectedStock, apiPeriod, chartType);
        
        // 根据图表类型转换数据格式
        let chartData;
        if (chartType === 'line') {
          chartData = response.data.map((item: any) => [
            item.date,
            item.close
          ]);
        } else if (chartType === 'candle') {
          chartData = response.data.map((item: any) => [
            item.date,
            item.open,
            item.close,
            item.low,
            item.high,
            item.volume
          ]);
        } else if (chartType === 'bar') {
          chartData = response.data.map((item: any) => [
            item.date,
            item.volume,
            item.close > item.open ? 1 : -1  // 用于确定柱状图颜色
          ]);
        }
        
        // 如果设置了日期范围，过滤数据
        if (dateRange && dateRange[0] && dateRange[1]) {
          const startDate = dateRange[0].format('YYYY-MM-DD');
          const endDate = dateRange[1].format('YYYY-MM-DD');
          
          chartData = chartData.filter((item: any) => {
            const itemDate = item[0];
            return itemDate >= startDate && itemDate <= endDate;
          });
        }
        
        setMainChartData(chartData);
        
        // 同时获取技术指标数据
        await fetchIndicatorData(selectedStock, apiPeriod);
      } catch (error) {
        console.error('获取股票数据失败:', error);
        setMainChartData([]);
        setIndicatorData({});
      } finally {
        setLoading(false);
      }
    };
    
    fetchStockData();
    
    // 如果启用比较模式，获取比较数据
    if (compareMode && comparedStocks.length > 0) {
      fetchComparedData();
    }
    
    // 通知父组件股票已更改
    if (onStockChange) {
      onStockChange(selectedStock);
    }
  }, [selectedStock, period, chartType, dateRange, compareMode, comparedStocks]);
  
  // 获取技术指标数据
  const fetchIndicatorData = async (stockCode: string, apiPeriod: string) => {
    try {
      // 获取活跃的指标类型
      const activeIndicatorTypes = indicatorPanels
        .filter(panel => panel.active)
        .map(panel => panel.type);
      
      if (activeIndicatorTypes.length === 0) return;
      
      // 获取指标数据
      const response = await getStockIndicators(stockCode, apiPeriod, activeIndicatorTypes);
      
      // 更新指标数据
      setIndicatorData(response.data);
    } catch (error) {
      console.error('获取指标数据失败:', error);
    }
  };
  
  // 获取比较数据
  const fetchComparedData = async () => {
    const apiPeriod = periodMap[period];
    const newComparedData: Record<string, any[]> = {};
    
    // 使用Promise.all并行获取所有比较股票的数据
    await Promise.all(
      comparedStocks.map(async (code) => {
        try {
          const response = await getStockKline(code, apiPeriod, 'line');
          
          // 标准化数据，只保留日期和收盘价
          const chartData = response.data.map((item: any) => [
            item.date,
            item.close
          ]);
          
          // 如果设置了日期范围，过滤数据
          if (dateRange && dateRange[0] && dateRange[1]) {
            const startDate = dateRange[0].format('YYYY-MM-DD');
            const endDate = dateRange[1].format('YYYY-MM-DD');
            
            newComparedData[code] = chartData.filter((item: any) => {
              const itemDate = item[0];
              return itemDate >= startDate && itemDate <= endDate;
            });
          } else {
            newComparedData[code] = chartData;
          }
        } catch (error) {
          console.error(`获取比较数据失败 (${code}):`, error);
          newComparedData[code] = [];
        }
      })
    );
    
    setComparedData(newComparedData);
  };

  // 处理股票选择变化
  const handleStockChange = (e: RadioChangeEvent) => {
    setSelectedStock(e.target.value);
  };

  // 处理周期选择变化
  const handlePeriodChange = (value: PeriodType) => {
    setPeriod(value);
  };
  
  // 处理图表类型变化
  const handleChartTypeChange = (type: ChartType) => {
    setChartType(type);
  };
  
  // 处理比较模式切换
  const handleCompareToggle = () => {
    setCompareMode(!compareMode);
    if (!compareMode) {
      // 默认添加第一个不同的股票作为比较
      const differentStock = stocks.find(stock => stock.code !== selectedStock);
      if (differentStock) {
        setComparedStocks([differentStock.code]);
      }
    } else {
      // 关闭比较模式
      setComparedStocks([]);
      setComparedData({});
    }
  };
  
  // 处理添加比较股票
  const handleAddCompareStock = (code: string) => {
    if (!comparedStocks.includes(code)) {
      setComparedStocks([...comparedStocks, code]);
    }
  };
  
  // 处理移除比较股票
  const handleRemoveCompareStock = (code: string) => {
    setComparedStocks(comparedStocks.filter(item => item !== code));
    
    // 从比较数据中移除
    const newComparedData = { ...comparedData };
    delete newComparedData[code];
    setComparedData(newComparedData);
  };
  
  // 处理日期范围变化
  const handleDateRangeChange = (dates: any) => {
    setDateRange(dates);
  };
  
  // 切换全屏模式
  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
  };
  
  // 刷新数据
  const refreshData = () => {
    // 通过重新设置选中的股票来触发数据刷新
    const current = selectedStock;
    setSelectedStock('');
    setTimeout(() => {
      setSelectedStock(current);
    }, 100);
  };
  
  // 添加指标面板
  const handleAddIndicatorPanel = () => {
    // 找到第一个未激活的指标
    const inactiveIndicator = availableIndicators.find(indicator => 
      !indicatorPanels.some(panel => panel.type === indicator && panel.active)
    );
    
    if (inactiveIndicator) {
      const updatedPanels = [...indicatorPanels];
      const existingPanelIndex = updatedPanels.findIndex(panel => panel.type === inactiveIndicator);
      
      if (existingPanelIndex >= 0) {
        // 如果面板已存在但未激活，则激活它
        updatedPanels[existingPanelIndex].active = true;
      } else {
        // 否则添加新面板
        updatedPanels.push({ type: inactiveIndicator, height: 120, active: true });
      }
      
      setIndicatorPanels(updatedPanels);
    }
  };
  
  // 移除指标面板
  const handleRemoveIndicatorPanel = (type: IndicatorType) => {
    const updatedPanels = indicatorPanels.map(panel => 
      panel.type === type ? { ...panel, active: false } : panel
    );
    setIndicatorPanels(updatedPanels);
  };
  
  // 调整指标面板高度
  const handleResizeIndicatorPanel = (type: IndicatorType, height: number) => {
    const updatedPanels = indicatorPanels.map(panel => 
      panel.type === type ? { ...panel, height } : panel
    );
    setIndicatorPanels(updatedPanels);
  };

  // 获取当前显示的指标面板
  const getActiveIndicatorPanels = () => {
    return indicatorPanels.filter(panel => panel.active);
  };
  
  // 初始化图表实例引用
  const handleMainChartInit = (instance: any) => {
    mainChartRef.current = instance;
  };
  
  // 初始化指标图表实例引用
  const handleIndicatorChartInit = (type: IndicatorType, instance: any) => {
    indicatorChartRefs.current[type] = instance;
  };

  // 计算主图表高度
  const calculateMainChartHeight = () => {
    // 基础高度
    const baseHeight = height || 600;
    
    // 控制栏高度
    const controlsHeight = showHeader ? 50 : 0;
    
    // 所有活跃指标面板总高度
    const activePanelsHeight = getActiveIndicatorPanels().reduce((total, panel) => {
      return total + panel.height;
    }, 0);
    
    // 加上面板间隔
    const totalIndicatorHeight = activePanelsHeight > 0 ? activePanelsHeight + 20 : 0;
    
    // 主图表占用剩余高度，但至少有200px
    return Math.max(baseHeight - controlsHeight - totalIndicatorHeight, 200);
  };

  // 为Dropdown菜单准备items
  const getCompareStockItems = () => {
    return stocks
      .filter(stock => stock.code !== selectedStock && !comparedStocks.includes(stock.code))
      .map(stock => ({
        key: stock.code,
        label: `${stock.name} (${stock.code})`,
        onClick: () => handleAddCompareStock(stock.code)
      }));
  };

  // 为Dropdown菜单准备indicators items
  const getIndicatorItems = () => {
    return availableIndicators
      .filter(indicator => 
        !indicatorPanels.some(panel => panel.type === indicator && panel.active)
      )
      .map(indicator => ({
        key: indicator,
        label: indicator,
        onClick: () => {
          const updatedPanels = [...indicatorPanels];
          const existingPanelIndex = updatedPanels.findIndex(panel => panel.type === indicator);
          
          if (existingPanelIndex >= 0) {
            updatedPanels[existingPanelIndex].active = true;
          } else {
            updatedPanels.push({ type: indicator, height: 120, active: true });
          }
          
          setIndicatorPanels(updatedPanels);
        }
      }));
  };

  return (
    <Card
      style={{ 
        width: fullWidth ? '100%' : 'auto', 
        height: isFullscreen ? '100vh' : 'auto',
        padding: 0
      }}
      className={isFullscreen ? 'fullscreen-chart' : ''}
      bodyStyle={{ padding: '8px' }}
      title={
        showHeader && (
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Radio.Group value={selectedStock} onChange={handleStockChange} buttonStyle="solid">
              {stocks.slice(0, 5).map(stock => (
                <Radio.Button key={stock.code} value={stock.code}>
                  <Tooltip title={`${stock.name} ${stock.current} (${stock.change >= 0 ? '+' : ''}${stock.change_percent}%)`}>
                    <span>
                      {stock.name}
                      <span style={{ 
                        marginLeft: 5,
                        color: stock.change >= 0 ? '#3f8600' : '#cf1322'
                      }}>
                        {stock.change >= 0 ? '+' : ''}{stock.change_percent}%
                      </span>
                    </span>
                  </Tooltip>
                </Radio.Button>
              ))}
            </Radio.Group>
            
            <Space>
              {/* 图表类型切换 */}
              <Radio.Group value={chartType} onChange={(e) => handleChartTypeChange(e.target.value)}>
                <Tooltip title="折线图">
                  <Radio.Button value="line"><LineChartOutlined /></Radio.Button>
                </Tooltip>
                <Tooltip title="K线图">
                  <Radio.Button value="candle"><CandlestickOutlined /></Radio.Button>
                </Tooltip>
                <Tooltip title="成交量">
                  <Radio.Button value="bar"><BarChartOutlined /></Radio.Button>
                </Tooltip>
              </Radio.Group>
              
              {/* 周期选择 */}
              <Select 
                value={period} 
                onChange={handlePeriodChange}
                style={{ width: 100 }}
              >
                <Option value="1m">1分钟</Option>
                <Option value="5m">5分钟</Option>
                <Option value="15m">15分钟</Option>
                <Option value="30m">30分钟</Option>
                <Option value="60m">60分钟</Option>
                <Option value="day">日线</Option>
                <Option value="week">周线</Option>
                <Option value="month">月线</Option>
              </Select>
              
              {/* 操作按钮 */}
              <Button 
                type={compareMode ? "primary" : "default"}
                onClick={handleCompareToggle}
              >
                对比
              </Button>
              
              <Dropdown 
                menu={{
                  items: getCompareStockItems(),
                }}
                disabled={!compareMode}
              >
                <Button>
                  <Space>
                    添加对比
                    <DownOutlined />
                  </Space>
                </Button>
              </Dropdown>
              
              <Button onClick={refreshData}><ReloadOutlined /></Button>
              <Button onClick={toggleFullscreen}><FullscreenOutlined /></Button>
              
              {/* 添加指标按钮 */}
              <Dropdown
                menu={{
                  items: getIndicatorItems()
                }}
              >
                <Button icon={<PlusOutlined />}>
                  添加指标
                </Button>
              </Dropdown>
            </Space>
          </div>
        )
      }
      bordered={false}
    >
      {compareMode && comparedStocks.length > 0 && (
        <div style={{ marginBottom: '10px' }}>
          <Text strong>正在对比: </Text>
          {comparedStocks.map(code => {
            const stock = stocks.find(s => s.code === code);
            return (
              <StockTag
                key={code}
                closable
                onClose={() => handleRemoveCompareStock(code)}
                style={{ marginRight: '8px' }}
              >
                {stock ? `${stock.name} (${stock.code})` : code}
              </StockTag>
            );
          })}
        </div>
      )}
      
      {/* 主图表 */}
      <MainChartRenderer
        selectedStock={selectedStock}
        chartData={mainChartData}
        loading={loading}
        chartType={chartType}
        chartHeight={calculateMainChartHeight()}
        period={period}
        showTitle={showTitle}
        compareMode={compareMode}
        comparedStocks={comparedStocks}
        comparedData={comparedData}
        indicatorData={indicatorData}
        stocks={stocks}
        onChartInit={handleMainChartInit}
      />
      
      {/* 指标图表 */}
      {getActiveIndicatorPanels().map(panel => (
        <IndicatorChartRenderer
          key={panel.type}
          indicatorType={panel.type}
          indicatorData={indicatorData[panel.type]}
          chartData={mainChartData}
          loading={loading}
          height={panel.height}
          period={period}
          onRemove={handleRemoveIndicatorPanel}
          onResize={handleResizeIndicatorPanel}
          onChartInit={handleIndicatorChartInit}
        />
      ))}
      
      {/* 底部控制栏 - 添加指标按钮 */}
      {getActiveIndicatorPanels().length === 0 && (
        <div style={{ textAlign: 'center', marginTop: '10px' }}>
          <Button 
            type="dashed" 
            icon={<PlusOutlined />} 
            onClick={handleAddIndicatorPanel}
          >
            添加技术指标
          </Button>
        </div>
      )}
    </Card>
  );
};

// 自定义Tag组件，包含关闭按钮
const StockTag: React.FC<{
  children: React.ReactNode;
  closable?: boolean;
  onClose?: () => void;
  style?: React.CSSProperties;
}> = ({ children, closable, onClose, style }) => {
  return (
    <Tag 
      closable={closable}
      onClose={onClose}
      style={style}
    >
      {children}
    </Tag>
  );
};

export default StockAnalysisPanel;