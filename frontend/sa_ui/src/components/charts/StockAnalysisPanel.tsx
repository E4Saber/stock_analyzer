// src/components/charts/StockAnalysisPanel.tsx
import React, { useState, useEffect, useRef, useMemo, useCallback } from 'react';
import { 
  Card, Radio, Spin, Empty, Button, Space, Select,
  Row, Col, Typography, Tooltip, Modal, Tabs, Checkbox
} from 'antd';
import { 
  SettingOutlined, FullscreenOutlined
} from '@ant-design/icons';
import { getStockKline, getStockIndicators } from '../../services/mock/mockStockService';
import MainChartRenderer from './MainChartRenderer';
import IndicatorChartRenderer from './IndicatorChartRenderer';
import { 
  StockData, ChartType, PeriodType, IndicatorType, IndicatorPanelConfig,
  periodMap, getAvailableIndicators, getDefaultIndicatorPanels
} from './config/chartConfig';
import type { RadioChangeEvent } from 'antd';
import './StockAnalysisPanel.css';

const { Text } = Typography;
const { Option } = Select;
const { TabPane } = Tabs;

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

// 策略助手选项配置
interface StrategySettings {
  trendLine: boolean;
  volumeDistribution: boolean;
  companyAction: boolean;
  tradingPoints: boolean;
  holdingCost: boolean;
  drawLines: boolean;
  currentPriceLine: boolean;
  alertLine: boolean;
  gapMarking: boolean;
}

// K线样式配置
interface KLineStyleSettings {
  height: number; // 100-220%
  style: 'hollow' | 'solid' | 'american' | 'line';
  colorScheme: 'redGreen' | 'greenRed';
  showPreAfterMarket: boolean;
  showNightTrading: boolean;
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
  // ---------- 状态定义 ----------
  // 基本状态
  const [selectedStock, setSelectedStock] = useState<string>(defaultStock || (stocks[0]?.code || ''));
  const [mainChartData, setMainChartData] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [period, setPeriod] = useState<PeriodType>(defaultPeriod);
  const [chartType] = useState<ChartType>(defaultChartType); // 固定为K线图，不需要改变
  const [isFullscreen, setIsFullscreen] = useState<boolean>(false);

  // 技术指标相关状态
  const [indicatorPanels, setIndicatorPanels] = useState<IndicatorPanelConfig[]>(getDefaultIndicatorPanels());
  const [indicatorData, setIndicatorData] = useState<Record<IndicatorType, any>>({});
  const [availableIndicators] = useState<IndicatorType[]>(getAvailableIndicators());
  
  // 设置弹窗状态
  const [settingsVisible, setSettingsVisible] = useState<boolean>(false);
  const [activeSettingsTab, setActiveSettingsTab] = useState<string>('mainIndicator');
  
  // 策略助手设置
  const [strategySettings, setStrategySettings] = useState<StrategySettings>({
    trendLine: true,
    volumeDistribution: true,
    companyAction: true,
    tradingPoints: true,
    holdingCost: true,
    drawLines: true,
    currentPriceLine: true,
    alertLine: true,
    gapMarking: false
  });
  
  // K线样式设置
  const [klineSettings, setKlineSettings] = useState<KLineStyleSettings>({
    height: 100,
    style: 'hollow',
    colorScheme: 'redGreen',
    showPreAfterMarket: true,
    showNightTrading: true
  });
  
  // 选中的主图指标
  const [selectedMainIndicator, setSelectedMainIndicator] = useState<string>('MA');
  
  // 图表引用
  const mainChartRef = useRef<any>(null);
  const indicatorChartRefs = useRef<Record<IndicatorType, any>>({});

  // ---------- 数据获取 ----------
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
        if (chartType === 'candle') {
          chartData = response.data.map((item: any) => [
            item.date,
            item.open,
            item.close,
            item.low,
            item.high,
            item.volume
          ]);
        } else {
          // 其他图表类型也转为相同格式提高兼容性
          chartData = response.data.map((item: any) => [
            item.date,
            item.open,
            item.close,
            item.low,
            item.high,
            item.volume
          ]);
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
    
    // 通知父组件股票已更改
    if (onStockChange) {
      onStockChange(selectedStock);
    }
  }, [selectedStock, period, chartType, onStockChange]);
  
  // 获取技术指标数据
  const fetchIndicatorData = useCallback(async (stockCode: string, apiPeriod: string) => {
    try {
      // 获取活跃的指标类型
      const activeIndicatorTypes = indicatorPanels
        .filter(panel => panel.active)
        .map(panel => panel.type);
      
      // 添加主图指标
      const allIndicatorTypes = [...activeIndicatorTypes];
      if (selectedMainIndicator === 'MA') {
        allIndicatorTypes.push('MA');
      } else if (selectedMainIndicator === 'BOLL') {
        allIndicatorTypes.push('BOLL');
      }
      
      if (allIndicatorTypes.length === 0) return;
      
      // 获取指标数据
      const response = await getStockIndicators(stockCode, apiPeriod, allIndicatorTypes);
      
      // 更新指标数据
      setIndicatorData(response.data);
    } catch (error) {
      console.error('获取指标数据失败:', error);
    }
  }, [indicatorPanels, selectedMainIndicator]);

  // ---------- 事件处理函数 ----------
  // 处理股票选择变化
  const handleStockChange = useCallback((e: RadioChangeEvent) => {
    setSelectedStock(e.target.value);
  }, []);

  // 处理周期选择变化
  const handlePeriodChange = useCallback((value: PeriodType) => {
    setPeriod(value);
  }, []);
  
  // 切换全屏模式
  const toggleFullscreen = useCallback(() => {
    setIsFullscreen(prev => !prev);
  }, []);
  
  // 打开设置弹窗
  const openSettings = useCallback((tab: string = 'mainIndicator') => {
    setActiveSettingsTab(tab);
    setSettingsVisible(true);
  }, []);
  
  // 获取当前显示的指标面板
  const getActiveIndicatorPanels = useCallback(() => {
    return indicatorPanels.filter(panel => panel.active);
  }, [indicatorPanels]);
  
  // 添加指标面板
  const handleAddIndicatorPanel = useCallback((type: IndicatorType) => {
    setIndicatorPanels(prevPanels => {
      const updatedPanels = [...prevPanels];
      const existingPanelIndex = updatedPanels.findIndex(panel => panel.type === type);
      
      if (existingPanelIndex >= 0) {
        // 如果面板已存在但未激活，则激活它
        updatedPanels[existingPanelIndex].active = true;
      } else {
        // 否则添加新面板
        updatedPanels.push({ type, height: 120, active: true });
      }
      
      return updatedPanels;
    });
    
    setSettingsVisible(false);
  }, []);
  
  // 移除指标面板
  const handleRemoveIndicatorPanel = useCallback((type: IndicatorType) => {
    // 获取当前活跃的面板
    const activePanels = getActiveIndicatorPanels();
    
    // 如果要移除的是第一个活跃面板，则不执行任何操作
    if (activePanels.length > 0 && activePanels[0].type === type) {
      return;
    }
    
    // 否则正常移除
    setIndicatorPanels(prevPanels => 
      prevPanels.map(panel => 
        panel.type === type ? { ...panel, active: false } : panel
      )
    );
  }, [getActiveIndicatorPanels]);
  
  // 调整指标面板高度
  const handleResizeIndicatorPanel = useCallback((type: IndicatorType, height: number) => {
    setIndicatorPanels(prevPanels => 
      prevPanels.map(panel => 
        panel.type === type ? { ...panel, height } : panel
      )
    );
  }, []);
  
  // 初始化图表实例引用
  const handleMainChartInit = useCallback((instance: any) => {
    mainChartRef.current = instance;
  }, []);
  
  // 初始化指标图表实例引用
  const handleIndicatorChartInit = useCallback((type: IndicatorType, instance: any) => {
    indicatorChartRefs.current[type] = instance;
  }, []);

  // 计算主图表高度
  const calculateMainChartHeight = useCallback(() => {
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
  }, [height, showHeader, getActiveIndicatorPanels]);
  
  // 处理主图指标切换
  const handleMainIndicatorChange = useCallback((indicator: string) => {
    setSelectedMainIndicator(indicator);
    setSettingsVisible(false);
    
    // 重新获取数据
    const apiPeriod = periodMap[period];
    fetchIndicatorData(selectedStock, apiPeriod);
  }, [selectedStock, period, fetchIndicatorData]);
  
  // 处理策略助手设置变更
  const handleStrategySettingChange = useCallback((key: keyof StrategySettings) => {
    setStrategySettings(prev => ({
      ...prev,
      [key]: !prev[key]
    }));
  }, []);
  
  // 处理K线样式设置变更
  const handleKLineStyleChange = useCallback((key: keyof KLineStyleSettings, value: any) => {
    setKlineSettings(prev => ({
      ...prev,
      [key]: value
    }));
  }, []);

  // ---------- 记忆化渲染 ----------
  // 使用useMemo优化指标面板渲染，减少不必要的重新渲染
  const memoizedIndicatorPanels = useMemo(() => {
    const activePanels = getActiveIndicatorPanels();
    
    return activePanels.map((panel, index) => (
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
        onChartInit={(instance) => handleIndicatorChartInit(panel.type, instance)}
        isFirstIndicator={index === 0} // 第一个副图不显示关闭按钮
      />
    ));
  }, [
    indicatorPanels, 
    indicatorData, 
    mainChartData, 
    loading, 
    period, 
    handleRemoveIndicatorPanel, 
    handleResizeIndicatorPanel, 
    handleIndicatorChartInit,
    getActiveIndicatorPanels
  ]);

  // 记忆化主图表高度计算，减少不必要的重新计算
  const mainChartHeight = useMemo(() => calculateMainChartHeight(), 
    [calculateMainChartHeight]);

  // ---------- 渲染方法 ----------
  // 渲染标题栏
  const renderHeader = useCallback(() => {
    if (!showHeader) return null;
    
    return (
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          {/* <Tooltip title={`${stocks.find(s => s.code === selectedStock)?.name || ''} (${selectedStock})`}>
            <Text strong style={{ fontSize: 16 }}>
              {stocks.find(s => s.code === selectedStock)?.name || ''} ({selectedStock})
            </Text>
          </Tooltip> */}
        </div>
        
        <Space>
          {/* <Select defaultValue="none" style={{ width: 90, marginRight: 8 }}>
            <Option value="none">不复权</Option>
            <Option value="forward">前复权</Option>
            <Option value="backward">后复权</Option>
          </Select> */}
          
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
          
          {/* 设置按钮 */}
          <Button icon={<SettingOutlined />} onClick={() => openSettings()} />
          <Button icon={<FullscreenOutlined />} onClick={toggleFullscreen} />
        </Space>
      </div>
    );
  }, [showHeader, stocks, selectedStock, period, handlePeriodChange, toggleFullscreen, openSettings]);

  // 渲染主图指标选项
  const renderMainIndicatorOptions = useCallback(() => {
    const mainIndicators = ['无', 'MA', 'VMA', 'EMA', 'SAR', 'BBI', 'PBX', 'BBIBOLL', 'MIKE', 'ENE', 'ALLIGAT', 'HMA', 'LMA', 'BOLL'];
    
    return (
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '10px' }}>
        {mainIndicators.map(indicator => (
          <Button 
            key={indicator}
            type={selectedMainIndicator === indicator ? 'primary' : 'default'}
            onClick={() => handleMainIndicatorChange(indicator)}
            style={{ textAlign: 'center' }}
          >
            {indicator}
          </Button>
        ))}
      </div>
    );
  }, [selectedMainIndicator, handleMainIndicatorChange]);

  // 渲染副图指标选项
  const renderSubIndicatorOptions = useCallback(() => {
    const subIndicators = [
      { type: 'VOL', name: '成交量' },
      { type: 'VRSI', name: 'VRSI' },
      { type: 'KDJ', name: 'KDJ' },
      { type: 'ADTM', name: 'ADTM' },
      { type: 'RSI', name: 'RSI' },
      { type: 'MFI', name: 'MFI' },
      { type: 'OBV', name: 'OBV' },
      { type: 'EMV', name: 'EMV' },
      { type: 'MACD', name: 'MACD' },
      { type: 'DMI', name: 'DMI' },
      { type: 'ATR', name: 'ATR' },
      { type: 'DMA', name: 'DMA' }
    ];
    
    return (
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '10px' }}>
        {subIndicators.map(indicator => (
          <Button 
            key={indicator.type}
            type={getActiveIndicatorPanels().find(p => p.type === indicator.type) ? 'primary' : 'default'}
            onClick={() => handleAddIndicatorPanel(indicator.type as IndicatorType)}
            style={{ textAlign: 'center' }}
          >
            {indicator.name}
          </Button>
        ))}
      </div>
    );
  }, [getActiveIndicatorPanels, handleAddIndicatorPanel]);
  
  // 渲染策略助手选项
  const renderStrategyOptions = useCallback(() => {
    const strategyOptions = [
      { key: 'trendLine', label: '趋势线' },
      { key: 'volumeDistribution', label: '筹码分布' },
      { key: 'companyAction', label: '公司行动' },
      { key: 'tradingPoints', label: '买卖打点' },
      { key: 'holdingCost', label: '持仓成本' },
      { key: 'drawLines', label: '画线' },
      { key: 'currentPriceLine', label: '现价线' },
      { key: 'alertLine', label: '预警线' },
      { key: 'gapMarking', label: '跳空缺口' }
    ];
    
    return (
      <Row gutter={[16, 16]}>
        {strategyOptions.map(option => (
          <Col span={12} key={option.key}>
            <Checkbox 
              checked={strategySettings[option.key as keyof StrategySettings]}
              onChange={() => handleStrategySettingChange(option.key as keyof StrategySettings)}
            >
              {option.label}
            </Checkbox>
          </Col>
        ))}
      </Row>
    );
  }, [strategySettings, handleStrategySettingChange]);

  // 渲染K线样式选项
  const renderKlineStyleOptions = useCallback(() => {
    return (
      <>
        <div style={{ marginBottom: 24 }}>
          <div style={{ marginBottom: 8 }}>K线图高度</div>
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <div style={{ marginRight: 8 }}>100%</div>
            <div style={{ flex: 1 }}>
              <input 
                type="range" 
                min={100} 
                max={220} 
                value={klineSettings.height} 
                onChange={(e) => handleKLineStyleChange('height', parseInt(e.target.value))}
                style={{ width: '100%' }}
              />
            </div>
            <div style={{ marginLeft: 8 }}>220%</div>
          </div>
        </div>
        
        <div style={{ marginBottom: 16 }}>
          <div style={{ marginBottom: 8 }}>K线样式</div>
          <Radio.Group 
            value={klineSettings.style}
            onChange={(e) => handleKLineStyleChange('style', e.target.value)}
          >
            <Radio value="hollow">空心蜡烛图</Radio>
            <Radio value="solid">实心K线</Radio>
            <Radio value="american">美国线</Radio>
            <Radio value="line">折线图</Radio>
          </Radio.Group>
        </div>
        
        <div style={{ marginBottom: 16 }}>
          <div style={{ marginBottom: 8 }}>涨跌偏好</div>
          <Radio.Group 
            value={klineSettings.colorScheme}
            onChange={(e) => handleKLineStyleChange('colorScheme', e.target.value)}
          >
            <Radio value="redGreen">红涨绿跌</Radio>
            <Radio value="greenRed">绿涨红跌</Radio>
          </Radio.Group>
        </div>
        
        <div style={{ marginBottom: 16 }}>
          <div style={{ marginBottom: 8 }}>延长时段（支持5日和分钟K的图表数据）</div>
          <div>
            <Checkbox 
              checked={klineSettings.showPreAfterMarket}
              onChange={(e) => handleKLineStyleChange('showPreAfterMarket', e.target.checked)}
            >
              盘前盘后
            </Checkbox>
          </div>
          <div>
            <Checkbox 
              checked={klineSettings.showNightTrading}
              onChange={(e) => handleKLineStyleChange('showNightTrading', e.target.checked)}
            >
              夜盘
            </Checkbox>
          </div>
        </div>
      </>
    );
  }, [klineSettings, handleKLineStyleChange]);

  // ---------- 主渲染 ----------
  return (
    <Card
      style={{ 
        width: fullWidth ? '100%' : 'auto', 
        height: isFullscreen ? '100vh' : 'auto',
        padding: 0
      }}
      className={isFullscreen ? 'fullscreen-chart' : ''}
      bodyStyle={{ padding: '8px' }}
      title={renderHeader()}
      bordered={false}
    >
      {/* 主图表 */}
      <MainChartRenderer
        selectedStock={selectedStock}
        chartData={mainChartData}
        loading={loading}
        chartType={'candle'} // 固定为K线图类型
        chartHeight={mainChartHeight}
        period={period}
        showTitle={showTitle}
        stocks={stocks}
        indicatorData={indicatorData}
        mainIndicator={selectedMainIndicator}
        onChartInit={handleMainChartInit}
      />
      
      {/* 指标图表 - 使用记忆化渲染 */}
      {memoizedIndicatorPanels}
      
      {/* 添加指标按钮 */}
      {getActiveIndicatorPanels().length === 0 && (
        <div style={{ textAlign: 'center', marginTop: '10px' }}>
          <Button 
            type="dashed" 
            onClick={() => openSettings('subIndicator')}
          >
            添加技术指标
          </Button>
        </div>
      )}
      
      {/* 设置弹窗 */}
      <Modal
        title="图表设置"
        open={settingsVisible}
        onCancel={() => setSettingsVisible(false)}
        footer={null}
        width={600}
      >
        <Tabs activeKey={activeSettingsTab} onChange={setActiveSettingsTab}>
          <TabPane tab="主图" key="mainIndicator">
            {renderMainIndicatorOptions()}
          </TabPane>
          
          <TabPane tab="副图" key="subIndicator">
            {renderSubIndicatorOptions()}
          </TabPane>
          
          <TabPane tab="策略助手" key="strategy">
            {renderStrategyOptions()}
          </TabPane>
          
          <TabPane tab="K线样式" key="klineStyle">
            {renderKlineStyleOptions()}
          </TabPane>
        </Tabs>
      </Modal>
    </Card>
  );
};

export default StockAnalysisPanel;