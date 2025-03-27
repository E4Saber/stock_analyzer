import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Switch, Space, Tooltip, Badge, Radio, Divider } from 'antd';
import { InfoCircleOutlined, QuestionCircleOutlined } from '@ant-design/icons';
import ReactECharts from 'echarts-for-react';
import * as echarts from 'echarts/core';

const FundFlowOverviewChart = ({ stockData }) => {
  const [showPrice, setShowPrice] = useState(true);
  const [timeRange, setTimeRange] = useState('60d'); // 默认显示60天
  
  // 模拟数据 - 实际应用中从props获取
  const mockData = {
    stockCode: '600519',
    stockName: '贵州茅台',
    // 假设60天的数据
    dates: Array.from({ length: 60 }, (_, i) => {
      const date = new Date(2025, 1, 1);
      date.setDate(date.getDate() + i);
      return date.toISOString().slice(0, 10);
    }),
    
    // 日资金流入数据
    dailyFundFlow: [
      // 第一段埋伏期 (0-9)
      1.2, 0.8, 1.5, 1.8, 0.9, 1.3, 0.7, 1.1, 1.4, 1.0,
      // 非埋伏期 (10-19)
      -0.5, 0.3, -0.7, -0.2, 0.5, -0.6, -0.8, 0.2, -0.3, 0.4,
      // 第二段埋伏期 (20-34)
      0.6, 1.2, 0.9, 1.5, 1.8, 1.3, 1.7, 2.0, 1.4, 0.8, 1.6, 1.9, 2.2, 1.5, 1.1,
      // 股价上涨期 (资金流出) (35-44)
      -0.4, -0.8, -1.2, -0.5, -0.9, -1.5, -0.3, -0.7, -1.0, -0.6,
      // 第三段埋伏期 (45-59)
      0.8, 1.3, 1.7, 1.5, 1.9, 2.3, 1.8, 2.1, 2.5, 1.6, 2.0, 2.4, 1.8, 2.2, 2.6
    ],
    
    // 尾盘资金流入
    closingFundFlow: [
      // 第一段埋伏期 (高尾盘占比)
      0.6, 0.4, 0.8, 0.9, 0.5, 0.7, 0.3, 0.6, 0.7, 0.5,
      // 非埋伏期 (低尾盘占比)
      -0.3, 0.1, -0.4, -0.1, 0.2, -0.3, -0.5, 0.1, -0.2, 0.2,
      // 第二段埋伏期 (高尾盘占比)
      0.3, 0.6, 0.5, 0.8, 0.9, 0.7, 0.9, 1.1, 0.7, 0.4, 0.8, 1.0, 1.2, 0.8, 0.6,
      // 股价上涨期
      -0.2, -0.4, -0.6, -0.3, -0.5, -0.8, -0.1, -0.4, -0.5, -0.3,
      // 第三段埋伏期
      0.4, 0.7, 0.9, 0.8, 1.0, 1.2, 0.9, 1.1, 1.3, 0.8, 1.0, 1.2, 0.9, 1.1, 1.4
    ],
    
    // 股价数据 (体现滞后上涨特性)
    prices: [
      // 第一段埋伏期 (股价平稳)
      1520, 1525, 1515, 1530, 1535, 1525, 1540, 1530, 1535, 1545,
      // 非埋伏期 (略微下跌)
      1540, 1535, 1525, 1520, 1530, 1515, 1505, 1510, 1500, 1505,
      // 第二段埋伏期 (股价平稳整理)
      1510, 1515, 1520, 1525, 1530, 1525, 1535, 1540, 1530, 1525, 1535, 1545, 1550, 1545, 1555,
      // 股价上涨期 (前期埋伏效果显现)
      1570, 1590, 1610, 1625, 1650, 1680, 1695, 1705, 1730, 1745,
      // 第三段埋伏期 (新的建仓阶段)
      1750, 1755, 1760, 1750, 1755, 1765, 1770, 1775, 1785, 1780, 1790, 1800, 1795, 1805, 1810
    ],
    
    // 主力埋伏时间段标记
    ambushPeriods: [
      { start: 0, end: 9, confidence: 'high', desc: '首次建仓期' },
      { start: 20, end: 34, confidence: 'very-high', desc: '主升前集中建仓' },
      { start: 45, end: 59, confidence: 'medium', desc: '二次建仓期' }
    ],
    
    // 市场指标
    marketCap: 22756.8, // 流通市值(亿元)
    indicators: {
      totalInflow: 38.6, // 累计净流入(亿元)
      inflowToCapRatio: 0.17, // 占流通市值比例
      averageClosingRatio: 0.52, // 平均尾盘资金占比
      mainForceConfidence: 0.85 // 主力介入置信度
    }
  };
  
  // 使用props中的数据或使用模拟数据
  const data = stockData || mockData;
  
  // 计算累计资金流入
  const calculateCumulativeFlow = (flowData) => {
    let cumulative = [];
    let sum = 0;
    for (let flow of flowData) {
      sum += flow;
      cumulative.push(Number(sum.toFixed(2)));
    }
    return cumulative;
  };
  
  const cumulativeFundFlow = calculateCumulativeFlow(data.dailyFundFlow);
  
  // 配置时间段时间范围
  const getTimeRangeData = (fullData, rangeType) => {
    let days;
    switch(rangeType) {
      case '20d': days = 20; break;
      case '30d': days = 30; break;
      case '60d': days = 60; break;
      case '120d': days = 120; break;
      default: days = fullData.length;
    }
    return fullData.slice(-Math.min(days, fullData.length));
  };
  
  // 获取当前时间范围的数据
  const currentDates = getTimeRangeData(data.dates, timeRange);
  const currentFundFlow = getTimeRangeData(data.dailyFundFlow, timeRange);
  const currentClosingFlow = getTimeRangeData(data.closingFundFlow, timeRange);
  const currentPrices = getTimeRangeData(data.prices, timeRange);
  const currentCumulative = getTimeRangeData(cumulativeFundFlow, timeRange);
  
  // 调整埋伏时间段以匹配当前时间范围
  const getVisibleAmbushPeriods = () => {
    const offset = data.dates.length - currentDates.length;
    return data.ambushPeriods
      .filter(period => period.end >= offset) // 只保留在当前范围内的埋伏期
      .map(period => ({
        ...period,
        start: Math.max(0, period.start - offset), // 调整开始位置
        end: Math.min(currentDates.length - 1, period.end - offset) // 调整结束位置
      }));
  };
  
  const visibleAmbushPeriods = getVisibleAmbushPeriods();
  
  // 计算累计资金占流通市值比例
  const cumulativeRatio = currentCumulative.map(sum => 
    ((sum / data.marketCap) * 100).toFixed(2)
  );
  
  // 生成ECharts背景区域配置，标记主力埋伏区域
  const getMarkAreas = () => {
    return visibleAmbushPeriods.map(period => {
      // 根据置信度设置不同的颜色
      let color;
      switch(period.confidence) {
        case 'very-high': color = 'rgba(255, 182, 193, 0.35)'; break; // 浅红色
        case 'high': color = 'rgba(173, 216, 230, 0.3)'; break; // 浅蓝色
        case 'medium': color = 'rgba(152, 251, 152, 0.25)'; break; // 浅绿色
        default: color = 'rgba(211, 211, 211, 0.2)'; // 浅灰色
      }
      
      return [{
        name: period.desc,
        itemStyle: {
          color: color
        },
        label: {
          show: true,
          position: 'top',
          formatter: period.desc,
          fontSize: 12,
          color: '#333',
          backgroundColor: 'rgba(255, 255, 255, 0.7)',
          padding: [2, 4]
        },
        xAxis: currentDates[period.start],
        yAxis: 0
      }, {
        xAxis: currentDates[period.end],
        yAxis: 'max'
      }];
    });
  };
  
  // 图表选项
  const getOption = () => {
    return {
      title: {
        text: `${data.stockName}(${data.stockCode}) - 资金流入与主力潜伏分析`,
        subtext: '背景色区域表示识别出的主力潜伏期',
        left: 'center'
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'cross',
          label: {
            backgroundColor: '#6a7985'
          }
        },
        formatter: function(params) {
          let result = params[0].axisValueLabel + '<br/>';
          
          // 遍历所有数据项
          params.forEach(item => {
            if (item.seriesName && item.value !== undefined) {
              let valueStr;
              
              // 根据系列名称格式化数值
              if (item.seriesName === '日资金流入' || item.seriesName === '尾盘资金') {
                valueStr = `${item.value.toFixed(2)}亿元`;
              } else if (item.seriesName === '累计资金占比') {
                valueStr = `${item.value}%`;
              } else if (item.seriesName === '股价') {
                valueStr = `${item.value.toFixed(2)}元`;
              } else {
                valueStr = item.value;
              }
              
              result += `${item.marker}${item.seriesName}: ${valueStr}<br/>`;
            }
          });
          
          // 检查当前日期是否在埋伏期内
          const dateIndex = currentDates.indexOf(params[0].axisValueLabel);
          const inAmbushPeriod = visibleAmbushPeriods.find(
            period => dateIndex >= period.start && dateIndex <= period.end
          );
          
          if (inAmbushPeriod) {
            result += `<div style="margin-top:5px;padding:3px 0;border-top:1px dashed #999;">
                      <span style="color:#f50;font-weight:bold;">◉ ${inAmbushPeriod.desc}</span>
                     </div>`;
          }
          
          return result;
        }
      },
      legend: {
        data: [
          '日资金流入', '尾盘资金', '累计资金占比', 
          ...(showPrice ? ['股价'] : [])
        ],
        top: 40
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      toolbox: {
        feature: {
          saveAsImage: {}
        }
      },
      dataZoom: [
        {
          type: 'inside',
          start: 0,
          end: 100
        },
        {
          start: 0,
          end: 100
        }
      ],
      xAxis: [
        {
          type: 'category',
          boundaryGap: false,
          data: currentDates,
          axisLabel: {
            formatter: value => value.substring(5), // 只显示月-日
            rotate: 45
          }
        }
      ],
      yAxis: [
        {
          type: 'value',
          name: '资金流入(亿元)',
          position: 'left',
          axisLine: {
            lineStyle: {
              color: '#5470C6'
            }
          },
          axisLabel: {
            formatter: '{value}'
          },
          splitLine: {
            show: true,
            lineStyle: {
              type: 'dashed'
            }
          }
        },
        {
          type: 'value',
          name: '占流通市值(%)',
          position: 'right',
          offset: 0,
          axisLine: {
            lineStyle: {
              color: '#91CC75'
            }
          },
          axisLabel: {
            formatter: '{value}%'
          }
        },
        ...(showPrice ? [{
          type: 'value',
          name: '股价(元)',
          position: 'right',
          offset: 80,
          axisLine: {
            lineStyle: {
              color: '#EE6666'
            }
          },
          axisLabel: {
            formatter: '{value}'
          },
          splitLine: {
            show: false
          }
        }] : [])
      ],
      visualMap: [
        {
          show: false,
          dimension: 1,
          pieces: [{
            gt: 0,
            lte: 5,
            color: '#5470C6'
          }, {
            lt: 0,
            color: '#EE6666'
          }],
          outOfRange: {
            color: '#5470C6'
          }
        }
      ],
      series: [
        {
          name: '日资金流入',
          type: 'bar',
          yAxisIndex: 0,
          data: currentFundFlow,
          itemStyle: {
            color: function(params) {
              return params.value >= 0 ? '#5470C6' : '#EE6666';
            }
          },
          emphasis: {
            focus: 'series'
          },
          markLine: {
            data: [
              {
                name: '资金均值',
                type: 'average',
                lineStyle: {
                  color: '#5470C6',
                  type: 'dashed'
                },
                label: {
                  position: 'end',
                  formatter: '平均: {c}亿'
                }
              }
            ]
          }
        },
        {
          name: '尾盘资金',
          type: 'bar',
          yAxisIndex: 0,
          data: currentClosingFlow,
          itemStyle: {
            color: function(params) {
              return params.value >= 0 ? 'rgba(145, 204, 117, 0.8)' : 'rgba(238, 102, 102, 0.8)';
            }
          },
          emphasis: {
            focus: 'series'
          },
          barGap: '-70%',
          barWidth: '40%',
          z: 2
        },
        {
          name: '累计资金占比',
          type: 'line',
          smooth: true,
          yAxisIndex: 1,
          lineStyle: {
            width: 3,
            color: '#91CC75'
          },
          data: cumulativeRatio,
          z: 3
        },
        ...(showPrice ? [{
          name: '股价',
          type: 'line',
          smooth: true,
          symbol: 'emptyCircle',
          symbolSize: 6,
          yAxisIndex: 2,
          lineStyle: {
            width: 2.5,
            color: '#EE6666'
          },
          areaStyle: {
            opacity: 0.1,
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(238, 102, 102, 0.3)' },
              { offset: 1, color: 'rgba(238, 102, 102, 0.1)' }
            ])
          },
          data: currentPrices,
          z: 4
        }] : []),
        {
          name: '埋伏期标记',
          type: 'custom',
          renderItem: function() { return { type: 'group' }; }, // 空渲染函数
          data: [],
          markArea: {
            silent: true,
            data: getMarkAreas()
          },
          z: 1
        }
      ]
    };
  };

  // 显示不同置信度的颜色标记
  const confidenceColors = {
    'very-high': { color: '#ffb6c1', text: '高置信度建仓期' },
    'high': { color: '#add8e6', text: '中高置信度建仓期' },
    'medium': { color: '#98fb98', text: '中等置信度建仓期' }
  };
  
  return (
    <Card bordered={false} style={{ width: '100%' }}>
      <Row gutter={[16, 16]}>
        {/* 顶部控制区 */}
        <Col span={24}>
          <Row justify="space-between" align="middle">
            <Col>
              <Space size="large">
                <Space>
                  <span style={{ fontWeight: 'bold' }}>时间范围:</span>
                  <Radio.Group 
                    value={timeRange} 
                    onChange={e => setTimeRange(e.target.value)}
                    buttonStyle="solid"
                  >
                    <Radio.Button value="20d">20天</Radio.Button>
                    <Radio.Button value="30d">30天</Radio.Button>
                    <Radio.Button value="60d">60天</Radio.Button>
                    <Radio.Button value="120d">120天</Radio.Button>
                  </Radio.Group>
                </Space>
                
                <Space>
                  <span style={{ fontWeight: 'bold' }}>显示股价:</span>
                  <Switch 
                    checked={showPrice} 
                    onChange={setShowPrice} 
                    checkedChildren="开" 
                    unCheckedChildren="关"
                  />
                  <Tooltip title="显示股价走势可以观察主力潜伏期与股价变动的关系，通常股价会滞后于主力埋伏而上涨">
                    <QuestionCircleOutlined />
                  </Tooltip>
                </Space>
              </Space>
            </Col>
            
            <Col>
              <Space>
                {Object.entries(confidenceColors).map(([key, value]) => (
                  <Badge 
                    key={key}
                    color={value.color} 
                    text={value.text} 
                    style={{ backgroundColor: 'transparent' }}
                  />
                ))}
                <Tooltip title="系统根据资金流向特征、尾盘资金占比、主动性买盘等多维指标综合判断主力潜伏期">
                  <InfoCircleOutlined />
                </Tooltip>
              </Space>
            </Col>
          </Row>
        </Col>
        
        {/* 图表 */}
        <Col span={24}>
          <ReactECharts 
            option={getOption()} 
            style={{ height: '450px' }} 
            notMerge={true}
            lazyUpdate={true}
          />
        </Col>
        
        {/* 分析总结 */}
        <Col span={24}>
          <Divider orientation="left">主力资金分析</Divider>
          <Row gutter={[16, 8]}>
            <Col span={24}>
              <Space wrap size="large">
                <span>
                  <strong>累计净流入: </strong>
                  <span style={{ color: '#5470C6', fontWeight: 'bold' }}>
                    {data.indicators.totalInflow.toFixed(2)}亿元
                  </span>
                  <span style={{ color: '#888', marginLeft: 8 }}>
                    占流通市值
                    <span style={{ color: '#91CC75', fontWeight: 'bold', margin: '0 4px' }}>
                      {(data.indicators.inflowToCapRatio * 100).toFixed(2)}%
                    </span>
                  </span>
                </span>
                
                <span>
                  <strong>尾盘资金占比: </strong>
                  <span style={{ 
                    color: data.indicators.averageClosingRatio > 0.38 ? '#52c41a' : '#888',
                    fontWeight: 'bold'
                  }}>
                    {(data.indicators.averageClosingRatio * 100).toFixed(2)}%
                  </span>
                  {data.indicators.averageClosingRatio > 0.38 && 
                    <span style={{ color: '#52c41a', marginLeft: 4 }}>
                      (机构特征)
                    </span>
                  }
                </span>
                
                <span>
                  <strong>主力介入置信度: </strong>
                  <span style={{ 
                    color: data.indicators.mainForceConfidence > 0.7 ? '#f50' : '#888',
                    fontWeight: 'bold'
                  }}>
                    {(data.indicators.mainForceConfidence * 100).toFixed(0)}%
                  </span>
                </span>
              </Space>
            </Col>
            
            <Col span={24}>
              <p style={{ margin: '8px 0' }}>
                分析结论: 该股票在近期展现出明显的主力资金埋伏特征，主要表现为
                {data.ambushPeriods.length > 0 ? 
                  `${data.ambushPeriods.length}个独立的建仓期，` : '持续的建仓，'}
                尾盘资金占比高达{(data.indicators.averageClosingRatio * 100).toFixed(1)}%，
                具有典型的
                {data.indicators.averageClosingRatio > 0.45 ? '机构资金' : 
                  data.indicators.averageClosingRatio > 0.38 ? '中长线资金' : '短线资金'}
                建仓特征。
                {showPrice && data.ambushPeriods.some(p => p.confidence === 'very-high' || p.confidence === 'high') ? 
                  '从股价走势可以观察到，主力建仓完成后股价呈现明显上涨，验证了埋伏信号的有效性。' : ''}
              </p>
            </Col>
          </Row>
        </Col>
      </Row>
    </Card>
  );
};

export default FundFlowOverviewChart;