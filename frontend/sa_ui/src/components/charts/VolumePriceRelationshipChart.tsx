import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Radio, Tooltip, Tag, Space, Statistic, Divider, Switch } from 'antd';
import { InfoCircleOutlined, ArrowUpOutlined, ArrowDownOutlined, ExclamationCircleOutlined } from '@ant-design/icons';
import ReactECharts from 'echarts-for-react';
import * as echarts from 'echarts/core';
import { mockVolumePriceData } from '../../mock/mockVolumePriceData';

const VolumePriceRelationshipChart = ({ stockData, selectedDateRange }) => {
  const [timeRange, setTimeRange] = useState(selectedDateRange || '60d');
  const [showDivergence, setShowDivergence] = useState(true);
  const [showSupportBuying, setShowSupportBuying] = useState(true);
  
  // 使用props中的数据或使用模拟数据
  const data = stockData || mockVolumePriceData;
  
  // 根据传入的时间范围筛选数据
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
  
  // 同步时间范围
  useEffect(() => {
    if (selectedDateRange) {
      setTimeRange(selectedDateRange);
    }
  }, [selectedDateRange]);
  
  // 获取当前时间范围的数据
  const currentDates = getTimeRangeData(data.dates, timeRange);
  const currentPrices = getTimeRangeData(data.prices, timeRange);
  const currentFundFlow = getTimeRangeData(data.fundFlow, timeRange);
  const currentVolumes = getTimeRangeData(data.volumes, timeRange);
  const currentPriceChangePercent = getTimeRangeData(data.priceChangePercent, timeRange);
  
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
  
  const cumulativeFundFlow = calculateCumulativeFlow(currentFundFlow);
  
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
  
  // 获取回调日信息
  const getPullbackDays = () => {
    return currentPriceChangePercent.map((change, index) => 
      change < -0.5 ? index : -1
    ).filter(idx => idx !== -1);
  };
  
  const pullbackDays = getPullbackDays();
  
  // 计算量价背离区域
  const getDivergencePeriods = () => {
    let divergencePeriods = [];
    let start = -1;
    
    for (let i = 1; i < currentPrices.length; i++) {
      // 计算价格变动方向
      const priceDirection = currentPrices[i] > currentPrices[i-1] ? 1 : 
                             currentPrices[i] < currentPrices[i-1] ? -1 : 0;
      
      // 计算资金流向方向
      const fundDirection = currentFundFlow[i] > 0 ? 1 : 
                           currentFundFlow[i] < 0 ? -1 : 0;
      
      // 检查是否背离
      const isDiverging = (priceDirection < 0 && fundDirection > 0) || 
                         (priceDirection === 0 && fundDirection > 0 && currentFundFlow[i] > 0.5); // 价格横盘但有明显资金流入
      
      if (isDiverging && start === -1) {
        start = i;
      } else if (!isDiverging && start !== -1) {
        if (i - start >= 2) { // 至少持续2天才记录
          divergencePeriods.push({
            start: start,
            end: i - 1,
            intensity: Math.abs(currentPrices[i-1] - currentPrices[start]) / currentPrices[start] * 100
          });
        }
        start = -1;
      }
    }
    
    // 处理当前正在进行的背离
    if (start !== -1 && currentPrices.length - start >= 2) {
      divergencePeriods.push({
        start: start,
        end: currentPrices.length - 1,
        intensity: Math.abs(currentPrices[currentPrices.length-1] - currentPrices[start]) / currentPrices[start] * 100
      });
    }
    
    return divergencePeriods;
  };
  
  const divergencePeriods = getDivergencePeriods();
  
  // 生成ECharts背景区域配置，标记主力埋伏区域
  const getMarkAreas = () => {
    let markAreas = [];
    
    // 标记主力埋伏区域
    visibleAmbushPeriods.forEach(period => {
      let color;
      switch(period.confidence) {
        case 'very-high': color = 'rgba(255, 182, 193, 0.2)'; break; // 浅红色
        case 'high': color = 'rgba(173, 216, 230, 0.15)'; break; // 浅蓝色
        case 'medium': color = 'rgba(152, 251, 152, 0.1)'; break; // 浅绿色
        default: color = 'rgba(211, 211, 211, 0.1)'; // 浅灰色
      }
      
      markAreas.push([
        {
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
          yAxis: 'min'
        }, 
        {
          xAxis: currentDates[period.end],
          yAxis: 'max'
        }
      ]);
    });
    
    // 如果开启量价背离显示
    if (showDivergence) {
      // 标记量价背离区域
      divergencePeriods.forEach(period => {
        markAreas.push([
          {
            name: '量价背离',
            itemStyle: {
              color: 'rgba(255, 140, 0, 0.15)' // 橙色半透明
            },
            label: {
              show: true,
              position: 'top',
              formatter: '量价背离',
              fontSize: 12,
              color: '#ff7f0e'
            },
            xAxis: currentDates[period.start],
            yAxis: 'min'
          }, 
          {
            xAxis: currentDates[period.end],
            yAxis: 'max'
          }
        ]);
      });
    }
    
    return markAreas;
  };
  
  // 生成回调日标记点
  const getMarkPoints = () => {
    if (!showSupportBuying) return [];
    
    return pullbackDays.map(day => ({
      name: '回调买入',
      coord: [currentDates[day], currentPrices[day]],
      value: currentFundFlow[day].toFixed(2),
      itemStyle: {
        color: currentFundFlow[day] > 0.5 ? '#52c41a' : '#faad14'
      },
      symbolSize: currentFundFlow[day] > 0.5 ? 15 : 10,
      symbol: 'pin',
      label: {
        formatter: '{b}',
        position: 'top'
      }
    }));
  };
  
  // 量价关系图表选项
  const getChartOption = () => {
    return {
      title: {
        text: `${data.stockName} - 量价关系分析`,
        left: 'center',
        top: 10
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'cross'
        },
        formatter: function(params) {
          let result = `${params[0].axisValueLabel}<br/>`;
          
          // 股价信息
          const priceItem = params.find(item => item.seriesName === '股价');
          if (priceItem) {
            result += `${priceItem.marker}${priceItem.seriesName}: ${priceItem.value.toFixed(2)}元<br/>`;
          }
          
          // 资金流向信息
          const fundFlowItem = params.find(item => item.seriesName === '资金流入');
          if (fundFlowItem) {
            result += `${fundFlowItem.marker}${fundFlowItem.seriesName}: ${fundFlowItem.value.toFixed(2)}亿元<br/>`;
          }
          
          // 累计资金流入信息
          const cumulativeItem = params.find(item => item.seriesName === '累计资金流入');
          if (cumulativeItem) {
            result += `${cumulativeItem.marker}${cumulativeItem.seriesName}: ${cumulativeItem.value.toFixed(2)}亿元<br/>`;
          }
          
          // 成交量信息
          const volumeItem = params.find(item => item.seriesName === '成交量');
          if (volumeItem) {
            result += `${volumeItem.marker}${volumeItem.seriesName}: ${volumeItem.value.toFixed(0)}万手<br/>`;
          }
          
          // 价格变动百分比
          const dateIndex = currentDates.indexOf(params[0].axisValueLabel);
          if (dateIndex >= 0 && dateIndex < currentPriceChangePercent.length) {
            const changePercent = currentPriceChangePercent[dateIndex];
            const color = changePercent >= 0 ? '#52c41a' : '#ff4d4f';
            result += `<span style="color:${color}">涨跌幅: ${changePercent.toFixed(2)}%</span><br/>`;
          }
          
          // 检查是否为回调日
          if (pullbackDays.includes(dateIndex)) {
            const fundFlow = currentFundFlow[dateIndex];
            const color = fundFlow > 0.5 ? '#52c41a' : '#faad14';
            result += `<span style="color:${color}">回调日买入强度: ${fundFlow.toFixed(2)}亿</span><br/>`;
          }
          
          // 检查是否在量价背离区间
          const inDivergence = divergencePeriods.find(period => 
            dateIndex >= period.start && dateIndex <= period.end
          );
          if (inDivergence) {
            result += `<span style="color:#ff7f0e">量价背离区间 [强度: ${inDivergence.intensity.toFixed(1)}%]</span><br/>`;
          }
          
          return result;
        }
      },
      legend: {
        data: ['股价', '资金流入', '累计资金流入', '成交量'],
        top: 40
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '15%',
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
          end: 100,
          bottom: '2%'
        }
      ],
      xAxis: {
        type: 'category',
        data: currentDates,
        axisLabel: {
          formatter: value => value.substring(5), // 只显示月-日
          rotate: 45
        }
      },
      yAxis: [
        {
          type: 'value',
          name: '股价(元)',
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
          name: '资金流入(亿元)',
          position: 'right',
          axisLine: {
            lineStyle: {
              color: '#91CC75'
            }
          },
          axisLabel: {
            formatter: '{value}'
          },
          splitLine: {
            show: false
          }
        },
        {
          type: 'value',
          name: '成交量(万手)',
          position: 'right',
          offset: 80,
          axisLine: {
            lineStyle: {
              color: '#FAC858'
            }
          },
          axisLabel: {
            formatter: '{value}'
          },
          splitLine: {
            show: false
          }
        }
      ],
      series: [
        {
          name: '股价',
          type: 'line',
          data: currentPrices,
          yAxisIndex: 0,
          symbol: 'emptyCircle',
          symbolSize: 6,
          lineStyle: {
            color: '#5470C6',
            width: 2.5
          },
          emphasis: {
            focus: 'series'
          },
          markPoint: {
            data: getMarkPoints()
          }
        },
        {
          name: '资金流入',
          type: 'bar',
          data: currentFundFlow,
          yAxisIndex: 1,
          itemStyle: {
            color: function(params) {
              return params.value >= 0 ? '#91CC75' : '#EE6666';
            }
          },
          emphasis: {
            focus: 'series'
          }
        },
        {
          name: '累计资金流入',
          type: 'line',
          data: cumulativeFundFlow,
          yAxisIndex: 1,
          symbol: 'none',
          lineStyle: {
            color: '#73C0DE',
            width: 2,
            type: 'dashed'
          },
          emphasis: {
            focus: 'series'
          }
        },
        {
          name: '成交量',
          type: 'bar',
          data: currentVolumes,
          yAxisIndex: 2,
          itemStyle: {
            color: '#FAC858',
            opacity: 0.6
          },
          emphasis: {
            focus: 'series'
          }
        },
        {
          name: '背景区域',
          type: 'custom',
          renderItem: function() { return { type: 'group' }; }, // 空渲染函数
          data: [],
          markArea: {
            silent: true,
            data: getMarkAreas()
          },
          z: -1
        }
      ]
    };
  };
  
  // 计算量价背离指标
  const calculateVolumePriceDivergence = () => {
    // 计算价格总变化百分比
    const startPrice = currentPrices[0];
    const endPrice = currentPrices[currentPrices.length - 1];
    const priceChangePercent = (endPrice / startPrice - 1) * 100;
    
    // 计算累计资金流入占流通市值比例
    const totalInflow = cumulativeFundFlow[cumulativeFundFlow.length - 1];
    const inflowToCapRatio = (totalInflow / data.marketCap) * 100;
    
    // 计算背离度 (正值表示有背离)
    let divergence = 0;
    
    if (Math.abs(priceChangePercent) < 0.5 && inflowToCapRatio > 0.05) {
      // 价格几乎不变但有资金流入，极强背离
      divergence = 5.0;
    } else if (priceChangePercent < 0 && inflowToCapRatio > 0) {
      // 价格下跌但资金流入，强背离
      divergence = Math.abs(inflowToCapRatio / priceChangePercent) * 3;
    } else if (priceChangePercent > 0 && inflowToCapRatio > 0) {
      // 价格上涨资金流入，计算比值
      // 如果资金流入比例远大于价格涨幅，也视为背离
      divergence = inflowToCapRatio / priceChangePercent - 1;
    }
    
    return {
      divergence: Math.max(0, divergence),
      priceChangePercent,
      inflowToCapRatio,
      totalInflow
    };
  };
  
  // 计算回调买入强度
  const calculateSupportBuyingStrength = () => {
    if (pullbackDays.length === 0) return 0;
    
    // 计算回调日的平均资金流入
    const pullbackInflow = pullbackDays.reduce((sum, day) => sum + Math.max(0, currentFundFlow[day]), 0);
    
    // 计算非回调日的平均资金流入
    const nonPullbackDays = currentDates.length - pullbackDays.length;
    const nonPullbackIndices = [...Array(currentDates.length).keys()].filter(i => !pullbackDays.includes(i));
    const nonPullbackInflow = nonPullbackIndices.reduce((sum, idx) => sum + Math.max(0, currentFundFlow[idx]), 0);
    
    // 如果非回调日资金流入为零，返回默认值
    if (nonPullbackInflow <= 0 || nonPullbackDays <= 0) return 1.0;
    
    // 计算回调日的相对资金流入强度 (回调日平均 / 非回调日平均)
    const pullbackAvg = pullbackInflow / pullbackDays.length;
    const nonPullbackAvg = nonPullbackInflow / nonPullbackDays;
    const supportStrength = pullbackAvg / nonPullbackAvg;
    
    return supportStrength;
  };
  
  // 计算突破前资金蓄势指标
  const calculateBreakthroughFundAccumulation = () => {
    // 在这个简化版本中，假设最近5天接近最高价的天数为接近压力位
    const highestPrice = Math.max(...currentPrices);
    const threshold = highestPrice * 0.95;
    
    const nearHighPriceIndices = currentPrices
      .map((price, index) => price > threshold ? index : -1)
      .filter(idx => idx !== -1)
      .slice(-5); // 最近5天
    
    if (nearHighPriceIndices.length === 0) return 0;
    
    // 计算接近压力位时的资金流入
    const nearHighPriceInflow = nearHighPriceIndices.reduce((sum, idx) => sum + Math.max(0, currentFundFlow[idx]), 0);
    
    // 计算总资金流入中的占比
    const totalPositiveInflow = currentFundFlow.reduce((sum, flow) => sum + Math.max(0, flow), 0);
    
    return totalPositiveInflow > 0 ? nearHighPriceInflow / totalPositiveInflow : 0;
  };
  
  // 计算各个指标
  const volumePriceDivergence = calculateVolumePriceDivergence();
  const supportBuyingStrength = calculateSupportBuyingStrength();
  const breakthroughAccumulation = calculateBreakthroughFundAccumulation();
  
  // 获取指标状态颜色
  const getDivergenceColor = (value) => {
    if (value >= 3.0) return '#52c41a'; // 强背离，绿色
    if (value >= 1.5) return '#1890ff'; // 中等背离，蓝色
    return '#faad14'; // 弱背离或无背离，橙色
  };
  
  const getSupportBuyingColor = (value) => {
    if (value >= 2.0) return '#52c41a'; // 强支撑，绿色
    if (value >= 1.5) return '#1890ff'; // 中等支撑，蓝色
    if (value >= 1.0) return '#faad14'; // 弱支撑，橙色
    return '#ff4d4f'; // 无支撑，红色
  };
  
  const getBreakthroughAccumulationColor = (value) => {
    if (value >= 0.4) return '#52c41a'; // 强蓄势，绿色
    if (value >= 0.25) return '#1890ff'; // 中等蓄势，蓝色
    if (value >= 0.1) return '#faad14'; // 弱蓄势，橙色
    return '#d9d9d9'; // 无蓄势，灰色
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
                  <span>量价背离标记:</span>
                  <Switch 
                    checked={showDivergence} 
                    onChange={setShowDivergence} 
                    checkedChildren="开" 
                    unCheckedChildren="关"
                  />
                </Space>
                <Space>
                  <span>回调买入标记:</span>
                  <Switch 
                    checked={showSupportBuying} 
                    onChange={setShowSupportBuying} 
                    checkedChildren="开" 
                    unCheckedChildren="关"
                  />
                </Space>
              </Space>
            </Col>
            <Col>
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
            </Col>
          </Row>
        </Col>
        
        {/* 图表 */}
        <Col span={24}>
          <ReactECharts 
            option={getChartOption()} 
            style={{ height: '450px' }} 
            notMerge={true}
            lazyUpdate={true}
          />
        </Col>
        
        {/* 量价关系关键指标 */}
        <Col span={24}>
          <Card type="inner" title="量价关系核心指标" size="small">
            <Row gutter={16}>
              <Col span={8}>
                <Statistic 
                  title={
                    <Space>
                      <span>量价背离度</span>
                      <Tooltip title="量价背离度指标衡量资金流入与价格变动的不匹配程度，值越高表示背离越明显，通常意味着主力在低位积极建仓">
                        <InfoCircleOutlined />
                      </Tooltip>
                    </Space>
                  } 
                  value={volumePriceDivergence.divergence}
                  precision={2}
                  valueStyle={{ color: getDivergenceColor(volumePriceDivergence.divergence) }}
                />
                <div style={{ marginTop: 4 }}>
                  <Tag color={getDivergenceColor(volumePriceDivergence.divergence)}>
                    {volumePriceDivergence.divergence >= 3.0 ? '强烈背离' : 
                     volumePriceDivergence.divergence >= 1.5 ? '明显背离' : 
                     volumePriceDivergence.divergence >= 0.5 ? '轻微背离' : '正常关系'}
                  </Tag>
                </div>
                <div style={{ fontSize: 12, color: '#888', marginTop: 4 }}>
                  <span>价格变动: {volumePriceDivergence.priceChangePercent.toFixed(2)}%</span>
                  <span style={{ marginLeft: 8 }}>资金占比: {volumePriceDivergence.inflowToCapRatio.toFixed(2)}%</span>
                </div>
              </Col>
              <Col span={8}>
                <Statistic 
                  title={
                    <Space>
                      <span>回调买入强度</span>
                      <Tooltip title="回调买入强度衡量股价回调时大单买入的相对强度，值越高表示回调时的买入意愿越强，通常意味着有主力在支撑位接盘">
                        <InfoCircleOutlined />
                      </Tooltip>
                    </Space>
                  } 
                  value={supportBuyingStrength}
                  precision={2}
                  valueStyle={{ color: getSupportBuyingColor(supportBuyingStrength) }}
                />
                <div style={{ marginTop: 4 }}>
                  <Tag color={getSupportBuyingColor(supportBuyingStrength)}>
                    {supportBuyingStrength >= 2.0 ? '强势支撑' : 
                     supportBuyingStrength >= 1.5 ? '明显支撑' : 
                     supportBuyingStrength >= 1.0 ? '一般支撑' : '支撑弱'}
                  </Tag>
                </div>
                <div style={{ fontSize: 12, color: '#888', marginTop: 4 }}>
                  <span>回调日数量: {pullbackDays.length}天</span>
                </div>
              </Col>
              <Col span={8}>
                <Statistic 
                  title={
                    <Space>
                      <span>突破前资金蓄势</span>
                      <Tooltip title="突破前资金蓄势衡量接近压力位时资金流入的集中程度，值越高表示在突破前资金蓄势越充分，通常预示着成功突破的可能性更大">
                        <InfoCircleOutlined />
                      </Tooltip>
                    </Space>
                  } 
                  value={breakthroughAccumulation}
                  precision={2}
                  valueStyle={{ color: getBreakthroughAccumulationColor(breakthroughAccumulation) }}
                />
                <div style={{ marginTop: 4 }}>
                  <Tag color={getBreakthroughAccumulationColor(breakthroughAccumulation)}>
                    {breakthroughAccumulation >= 0.4 ? '充分蓄势' : 
                     breakthroughAccumulation >= 0.25 ? '明显蓄势' : 
                     breakthroughAccumulation >= 0.1 ? '轻微蓄势' : '尚无蓄势'}
                  </Tag>
                </div>
              </Col>
            </Row>
          </Card>
        </Col>
        
        {/* 分析总结 */}
        <Col span={24}>
          <Divider orientation="left">量价关系分析总结</Divider>
          <div style={{ padding: '8px 16px' }}>
            <p>
              {volumePriceDivergence.divergence >= 1.5 ? 
                <strong style={{ color: '#52c41a' }}>存在明显的量价背离现象，</strong> : 
                '量价关系基本协调，'}
              
              {supportBuyingStrength >= 1.5 ? 
                <strong style={{ color: '#52c41a' }}>回调时有较强的大单支撑，</strong> : 
                supportBuyingStrength >= 1.0 ? 
                '回调时有一定的买盘支撑，' : 
                '回调时缺乏有效支撑，'}
              
              {breakthroughAccumulation >= 0.25 ? 
                <strong style={{ color: '#52c41a' }}>接近压力位时资金蓄势充分。</strong> : 
                breakthroughAccumulation >= 0.1 ? 
                '接近压力位时有一定资金蓄势。' : 
                '尚未观察到明显的突破前资金蓄势。'}
            </p>
            
            <p>总体评估：
              {
                (volumePriceDivergence.divergence >= 1.5 || supportBuyingStrength >= 1.5 || breakthroughAccumulation >= 0.25) ? 
                <strong style={{ color: '#52c41a' }}>存在较明确的主力建仓特征，量价互动积极，建议持续关注。</strong> : 
                (volumePriceDivergence.divergence >= 0.5 || supportBuyingStrength >= 1.0 || breakthroughAccumulation >= 0.1) ?
                <span style={{ color: '#1890ff' }}>有一定的主力介入迹象，但特征不够明显，建议继续观察。</span> :
                <span style={{ color: '#faad14' }}>量价关系一般，尚未发现明确的主力建仓行为。</span>
              }
            </p>
            
            <p style={{ marginTop: 8, fontSize: 13, color: '#666' }}>
              <ExclamationCircleOutlined style={{ marginRight: 5 }} />
              {divergencePeriods.length > 0 ? 
                `检测到${divergencePeriods.length}个量价背离区间，最强背离区间强度为${Math.max(...divergencePeriods.map(p => p.intensity)).toFixed(1)}%。` : 
                '当前时间范围内未检测到明显量价背离区间。'}
              {pullbackDays.length > 0 ? 
                ` 共有${pullbackDays.length}个回调日，回调买入强度为${supportBuyingStrength.toFixed(2)}倍。` : 
                ' 当前时间范围内未检测到显著回调日。'}
            </p>
          </div>
        </Col>
      </Row>
    </Card>
  );
};

export default VolumePriceRelationshipChart;