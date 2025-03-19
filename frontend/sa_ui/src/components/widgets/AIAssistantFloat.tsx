/**
 * TODO
 * 设计成悬浮在网页右侧（可以调节高度或隐藏，隐藏的话就需要显示按钮）
 * 根据所在页面的内容，自动获取背景信息，然后根据用户的特定询问，返回分析结果
 * 
 * 关于分析思考的过程，可以参考Tiger的DS的思考背景，分析背景需要参看设计MD
 * 并对常见的问题类型进行分析测试
 * 
 */
// src/components/widgets/AIAssistantFloat.tsx
import React, { useState, useEffect, useRef } from 'react';
import { 
  Button, Input, Card, Space, Tag, List, Typography, Divider,
  Collapse, Switch, Radio, Tooltip, Badge, Popover
} from 'antd';
import { 
  CloseOutlined, MinusOutlined, QuestionCircleOutlined, 
  RobotOutlined, LineChartOutlined, DollarOutlined, 
  FileTextOutlined, BarChartOutlined, HistoryOutlined,
  SaveOutlined, ShareAltOutlined, SendOutlined
} from '@ant-design/icons';
import Draggable from 'react-draggable';
import { StockData } from '../../types/market';
import './AIAssistantFloat.css';

const { Text, Title, Paragraph } = Typography;
const { TextArea } = Input;
const { Panel } = Collapse;

interface AIAssistantFloatProps {
  currentStock?: StockData;
  visible: boolean;
  onClose: () => void;
  onMinimize: () => void;
}

// 预设问题列表
const PRESET_QUESTIONS = [
  '该股近期技术面如何？',
  '主要支撑和阻力位在哪里？',
  '这只股票有什么风险？',
  '近期有什么重要消息影响？',
  '资金流向情况如何？',
  '与同行业股票相比表现如何？',
  '现在适合买入吗？'
];

// 分析维度
const ANALYSIS_DIMENSIONS = [
  { key: 'technical', label: '技术面', icon: <LineChartOutlined /> },
  { key: 'funds', label: '资金面', icon: <DollarOutlined /> },
  { key: 'news', label: '消息面', icon: <FileTextOutlined /> },
  { key: 'industry', label: '行业对比', icon: <BarChartOutlined /> },
  { key: 'history', label: '历史模式', icon: <HistoryOutlined /> }
];

/**
 * AI分析助手悬浮窗组件
 */
const AIAssistantFloat: React.FC<AIAssistantFloatProps> = ({ 
  currentStock,
  visible,
  onClose,
  onMinimize
}) => {
  // 组件状态
  const [question, setQuestion] = useState<string>('');
  const [analyzing, setAnalyzing] = useState<boolean>(false);
  const [analysisResult, setAnalysisResult] = useState<any>(null);
  const [multiDimensionMode, setMultiDimensionMode] = useState<boolean>(true);
  const [selectedDimensions, setSelectedDimensions] = useState<string[]>(
    ANALYSIS_DIMENSIONS.map(dim => dim.key)
  );
  const [expanded, setExpanded] = useState<boolean>(true);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  
  // 悬浮窗引用，用于尺寸调整
  const floatRef = useRef<HTMLDivElement>(null);
  const initialSize = { width: 380, height: 480 };
  const [size, setSize] = useState(initialSize);
  const [resizing, setResizing] = useState(false);
  
  // 监听当前股票变化，重置状态
  useEffect(() => {
    if (currentStock) {
      setAnalysisResult(null);
      setQuestion('');
    }
  }, [currentStock]);
  
  // 选择预设问题
  const handleSelectPresetQuestion = (q: string) => {
    setQuestion(q);
  };
  
  // 切换分析维度
  const toggleDimension = (dimension: string) => {
    if (selectedDimensions.includes(dimension)) {
      setSelectedDimensions(selectedDimensions.filter(d => d !== dimension));
    } else {
      setSelectedDimensions([...selectedDimensions, dimension]);
    }
  };
  
  // 提交分析请求
  const handleAnalyze = async () => {
    if (!question || !currentStock) return;
    
    setAnalyzing(true);
    
    try {
      // 这里应该调用实际的AI分析API
      // 这里使用模拟数据作为示例
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // 模拟分析结果
      const mockResult = {
        stockCode: currentStock.code,
        stockName: currentStock.name,
        question: question,
        timestamp: new Date().toISOString(),
        technicalAnalysis: selectedDimensions.includes('technical') ? {
          score: 75,
          trend: '上升通道，接近通道上轨',
          indicators: [
            { name: 'MACD', status: '金叉形成，短期动能向上' },
            { name: 'KDJ', status: '处于超买区域，需警惕回调' },
            { name: 'RSI', status: '高位，存在回调可能' }
          ],
          keyLevels: [
            { type: '支撑位', values: ['1720元', '1680元'] },
            { type: '阻力位', values: ['1830元', '1880元'] }
          ],
          risks: [
            '量能近期萎缩，上涨动力不足',
            '60日均线拐头向下，中期趋势转弱'
          ]
        } : null,
        fundsAnalysis: selectedDimensions.includes('funds') ? {
          mainForce: '近5日净流出3.42亿元',
          northBound: '近一周累计净买入2.15亿元',
          institutions: '公募基金持仓比例环比增加0.5%',
          margin: '融资余额增加，融券余额减少'
        } : null,
        newsAnalysis: selectedDimensions.includes('news') ? {
          recentNews: [
            { title: '公司发布年报，净利润同比增长12.5%', impact: '利好', date: '2025-03-15' },
            { title: '行业政策调整，预计影响有限', impact: '中性', date: '2025-03-10' }
          ],
          analystRatings: '12家机构评级：9个买入，3个持有，0个卖出'
        } : null,
        industryAnalysis: selectedDimensions.includes('industry') ? {
          rank: '行业内排名第2位',
          comparison: '估值低于行业平均水平15%',
          industryTrend: '行业整体处于上升周期中期阶段'
        } : null,
        historicalPatterns: selectedDimensions.includes('history') ? {
          similarPatterns: '当前形态与2023年4月相似',
          seasonality: '历史上二季度表现通常较好',
          priceTargets: '基于历史相似度分析，未来一个月目标价区间：1750-1900元'
        } : null,
        summary: '综合分析显示，该股近期技术面偏强，但存在短期回调风险。资金面整体稳定，机构持股增加是积极信号。历史经验显示，当前形态后续大概率有5-10%的上涨空间，建议关注1720元支撑位表现。'
      };
      
      setAnalysisResult(mockResult);
    } catch (error) {
      console.error('分析请求失败:', error);
      // 可以加入错误处理逻辑
    } finally {
      setAnalyzing(false);
    }
  };
  
  // 处理拖拽结束事件
  const handleDragStop = (e: any, data: any) => {
    setPosition({ x: data.x, y: data.y });
  };
  
  // 处理尺寸调整
  const handleResize = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!resizing) return;
    
    const container = floatRef.current;
    if (!container) return;
    
    const newWidth = Math.max(300, e.clientX - container.getBoundingClientRect().left);
    const newHeight = Math.max(400, e.clientY - container.getBoundingClientRect().top);
    
    setSize({ width: newWidth, height: newHeight });
  };
  
  // 鼠标移动事件监听
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (resizing) {
        const container = floatRef.current;
        if (!container) return;
        
        const newWidth = Math.max(300, e.clientX - container.getBoundingClientRect().left);
        const newHeight = Math.max(400, e.clientY - container.getBoundingClientRect().top);
        
        setSize({ width: newWidth, height: newHeight });
      }
    };
    
    const handleMouseUp = () => {
      if (resizing) {
        setResizing(false);
      }
    };
    
    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
    
    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [resizing]);
  
  // 如果不可见，不渲染组件
  if (!visible) return null;
  
  // 如果被最小化，只显示图标
  if (!expanded) {
    return (
      <Draggable
        defaultPosition={position}
        onStop={handleDragStop}
        bounds="parent"
      >
        <div className="ai-assistant-minimized">
          <Badge dot>
            <Button 
              type="primary" 
              shape="circle" 
              icon={<RobotOutlined />} 
              size="large"
              onClick={() => setExpanded(true)}
            />
          </Badge>
        </div>
      </Draggable>
    );
  }
  
  return (
    <Draggable
      handle=".ai-assistant-header"
      defaultPosition={position}
      onStop={handleDragStop}
      bounds="parent"
    >
      <div 
        ref={floatRef}
        className="ai-assistant-float"
        style={{ 
          width: `${size.width}px`, 
          height: `${size.height}px`,
        }}
      >
        {/* 头部栏 */}
        <div className="ai-assistant-header">
          <div className="ai-assistant-title">
            <RobotOutlined /> AI分析助手
          </div>
          <div className="ai-assistant-controls">
            <Button 
              type="text" 
              icon={<MinusOutlined />} 
              size="small"
              onClick={() => setExpanded(false)}
            />
            <Button 
              type="text" 
              icon={<CloseOutlined />} 
              size="small"
              onClick={onClose}
            />
          </div>
        </div>
        
        {/* 当前股票信息 */}
        {currentStock && (
          <div className="ai-assistant-stock-info">
            当前分析: {currentStock.name} ({currentStock.code})
            <Tag color={currentStock.change >= 0 ? 'green' : 'red'}>
              {currentStock.change >= 0 ? '+' : ''}{currentStock.change_percent.toFixed(2)}%
            </Tag>
          </div>
        )}
        
        {/* 内容区域 */}
        <div className="ai-assistant-content">
          {!analysisResult ? (
            // 问题输入区域
            <>
              <TextArea
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="输入您的问题或选择下方问题"
                autoSize={{ minRows: 2, maxRows: 4 }}
                className="ai-assistant-input"
              />
              
              <div className="ai-assistant-preset-questions">
                <List
                  size="small"
                  dataSource={PRESET_QUESTIONS}
                  renderItem={(item) => (
                    <List.Item 
                      onClick={() => handleSelectPresetQuestion(item)}
                      className="preset-question-item"
                    >
                      <Text>• {item}</Text>
                    </List.Item>
                  )}
                />
              </div>
              
              <div className="ai-assistant-options">
                <div className="option-row">
                  <Switch 
                    checked={multiDimensionMode} 
                    onChange={setMultiDimensionMode}
                    size="small"
                  />
                  <Text style={{ marginLeft: 8 }}>多维分析模式</Text>
                  <Tooltip title="同时从多个维度分析，提供更全面的见解">
                    <QuestionCircleOutlined style={{ marginLeft: 4 }} />
                  </Tooltip>
                </div>
                
                <div className="option-row dimensions">
                  <Space wrap>
                    {ANALYSIS_DIMENSIONS.map(dim => (
                      <Tag
                        key={dim.key}
                        color={selectedDimensions.includes(dim.key) ? 'blue' : 'default'}
                        onClick={() => toggleDimension(dim.key)}
                        className="dimension-tag"
                        icon={dim.icon}
                      >
                        {dim.label}
                      </Tag>
                    ))}
                  </Space>
                </div>
              </div>
              
              <div className="ai-assistant-actions">
                <Button 
                  type="primary" 
                  onClick={handleAnalyze} 
                  loading={analyzing}
                  disabled={!question || !currentStock}
                  icon={<SendOutlined />}
                >
                  分析
                </Button>
              </div>
            </>
          ) : (
            // 分析结果展示区域
            <div className="ai-assistant-result">
              <div className="result-header">
                <Title level={5}>
                  {currentStock?.name} ({currentStock?.code}) - 分析结果
                </Title>
                <Button type="link" onClick={() => setAnalysisResult(null)}>返回</Button>
              </div>
              
              <div className="result-content">
                {analysisResult.technicalAnalysis && (
                  <div className="analysis-section">
                    <Title level={5}>
                      <LineChartOutlined /> 技术面分析
                    </Title>
                    <div className="section-content">
                      <Paragraph>
                        <Text strong>技术指标综合评分:</Text>{' '}
                        <Text type={analysisResult.technicalAnalysis.score > 50 ? 'success' : 'danger'}>
                          {analysisResult.technicalAnalysis.score}分 
                          ({analysisResult.technicalAnalysis.score > 70 ? '偏强' : 
                            analysisResult.technicalAnalysis.score > 50 ? '中性' : '偏弱'})
                        </Text>
                      </Paragraph>
                      
                      <Paragraph>
                        <Text strong>走势状态:</Text>
                        <ul>
                          {analysisResult.technicalAnalysis.indicators.map((ind: any, i: number) => (
                            <li key={i}>{ind.name}: {ind.status}</li>
                          ))}
                        </ul>
                      </Paragraph>
                      
                      <Paragraph>
                        <Text strong>关键价位:</Text>
                        <ul>
                          {analysisResult.technicalAnalysis.keyLevels.map((level: any, i: number) => (
                            <li key={i}>{level.type}: {level.values.join('、')}</li>
                          ))}
                        </ul>
                      </Paragraph>
                      
                      <Paragraph>
                        <Text strong type="warning">风险提示:</Text>
                        <ul>
                          {analysisResult.technicalAnalysis.risks.map((risk: string, i: number) => (
                            <li key={i}>{risk}</li>
                          ))}
                        </ul>
                      </Paragraph>
                    </div>
                    <Divider />
                  </div>
                )}
                
                {analysisResult.fundsAnalysis && (
                  <div className="analysis-section">
                    <Title level={5}>
                      <DollarOutlined /> 资金面分析
                    </Title>
                    <div className="section-content">
                      <Paragraph>
                        <Text strong>主力资金:</Text>{' '}
                        <Text>{analysisResult.fundsAnalysis.mainForce}</Text>
                      </Paragraph>
                      <Paragraph>
                        <Text strong>北向资金:</Text>{' '}
                        <Text>{analysisResult.fundsAnalysis.northBound}</Text>
                      </Paragraph>
                      <Paragraph>
                        <Text strong>机构持仓:</Text>{' '}
                        <Text>{analysisResult.fundsAnalysis.institutions}</Text>
                      </Paragraph>
                      <Paragraph>
                        <Text strong>融资融券:</Text>{' '}
                        <Text>{analysisResult.fundsAnalysis.margin}</Text>
                      </Paragraph>
                    </div>
                    <Divider />
                  </div>
                )}
                
                {analysisResult.newsAnalysis && (
                  <div className="analysis-section">
                    <Title level={5}>
                      <FileTextOutlined /> 消息面分析
                    </Title>
                    <div className="section-content">
                      <Paragraph>
                        <Text strong>近期要闻:</Text>
                        <ul>
                          {analysisResult.newsAnalysis.recentNews.map((news: any, i: number) => (
                            <li key={i}>
                              <Text>{news.title}</Text>
                              <Tag color={
                                news.impact === '利好' ? 'green' : 
                                news.impact === '利空' ? 'red' : 'blue'
                              }>
                                {news.impact}
                              </Tag>
                              <Text type="secondary">({news.date})</Text>
                            </li>
                          ))}
                        </ul>
                      </Paragraph>
                      <Paragraph>
                        <Text strong>分析师评级:</Text>{' '}
                        <Text>{analysisResult.newsAnalysis.analystRatings}</Text>
                      </Paragraph>
                    </div>
                    <Divider />
                  </div>
                )}
                
                {/* 更多分析部分省略 */}
                
                <div className="analysis-summary">
                  <Paragraph>
                    <Text strong>综合分析:</Text>
                    <br />
                    <Text>{analysisResult.summary}</Text>
                  </Paragraph>
                </div>
                
                <div className="result-actions">
                  <Button icon={<SaveOutlined />}>保存分析</Button>
                  <Button icon={<ShareAltOutlined />}>分享</Button>
                </div>
              </div>
            </div>
          )}
        </div>
        
        {/* 调整大小的手柄 */}
        <div 
          className="resize-handle"
          onMouseDown={() => setResizing(true)}
        />
      </div>
    </Draggable>
  );
};

export default AIAssistantFloat;

