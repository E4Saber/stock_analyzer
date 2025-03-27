import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Radio, Tooltip, Tag, Space, Table, Divider, Statistic } from 'antd';
import { InfoCircleOutlined, ArrowUpOutlined, ArrowDownOutlined } from '@ant-design/icons';
import ReactECharts from 'echarts-for-react';
import { mockFundQualityData } from '../../mock/mockFundQualityData'; // 导入模拟数据

const FundQualityAnalysisChart = ({ stockData, selectedDateRange }) => {
  const [chartType, setChartType] = useState('largeOrderRatio');
  const [timeRange, setTimeRange] = useState(selectedDateRange || '60d');
  
  // 使用props中的数据或使用模拟数据
  const data = stockData || mockFundQualityData;
  
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
  const currentLargeOrderRatio = getTimeRangeData(data.largeOrderRatio, timeRange);
  const currentLargeOrderBuySellRatio = getTimeRangeData(data.largeOrderBuySellRatio, timeRange);
  const currentActiveBuyRatio = getTimeRangeData(data.activeBuyRatio, timeRange);
  const currentInflowAcceleration = getTimeRangeData(data.inflowAcceleration, timeRange);
  const currentFundStyle = getTimeRangeData(data.fundStyle, timeRange);
  
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
  
  // 生成ECharts背景区域配置，标记主力埋伏区域
  const getMarkAreas = () => {
    return visibleAmbushPeriods.map(period => {
      // 根据置信度设置不同的颜色
      let color;
      switch(period.confidence) {
        case 'very-high': color = 'rgba(255, 182, 193, 0.3)'; break; // 浅红色
        case 'high': color = 'rgba(173, 216, 230, 0.25)'; break; // 浅蓝色
        case 'medium': color = 'rgba(152, 251, 152, 0.2)'; break; // 浅绿色
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
  
  // 获取资金特征图表选项
  const getFundQualityOption = () => {
    // 根据选择的图表类型准备数据
    let seriesData = [];
    let yAxisName = '';
    let seriesName = '';
    let color = '';
    let threshold = 0;
    let yMin = null;
    
    switch(chartType) {
      case 'largeOrderRatio':
        seriesData = currentLargeOrderRatio;
        yAxisName = '大单占比(%)';
        seriesName = '大单占比';
        color = '#5470C6';
        threshold = 40; // 大单占比阈值
        yMin = 0;
        break;
      case 'buySellRatio':
        seriesData = currentLargeOrderBuySellRatio;
        yAxisName = '大单买卖比';
        seriesName = '大单买卖比';
        color = '#91CC75';
        threshold = 1.5; // 大单买卖比阈值
        yMin = 0;
        break;
      case 'activeBuy':
        seriesData = currentActiveBuyRatio;
        yAxisName = '主动买盘比例(%)';
        seriesName = '主动买盘比例';
        color = '#FAC858';
        threshold = 70; // 主动买盘比例阈值
        yMin = 50;
        break;
      case 'acceleration':
        seriesData = currentInflowAcceleration;
        yAxisName = '资金流入加速度(%)';
        seriesName = '资金流入加速度';
        color = '#EE6666';
        threshold = 20; // 资金流入加速度阈值
        yMin = null;
        break;
    }
    
    return {
      title: {
        text: `${data.stockName} - ${seriesName}分析`,
        left: 'center',
        top: 10
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'cross'
        },
        formatter: function(params) {
          const date = params[0].axisValueLabel;
          const value = params[0].value;
          const dateIndex = currentDates.indexOf(date);
          
          let result = `${date}<br/>${params[0].marker}${seriesName}: ${value}`;
          
          // 添加资金类型信息
          if (dateIndex >= 0 && dateIndex < currentFundStyle.length) {
            const fundType = currentFundStyle[dateIndex];
            let fundTypeText = '';
            let fundColor = '';
            
            switch(fundType) {
              case 'institutional':
                fundTypeText = '机构资金';
                fundColor = '#5470C6';
                break;
              case 'northbound':
                fundTypeText = '北向资金';
                fundColor = '#91CC75';
                break;
              case 'retail':
                fundTypeText = '游资主导';
                fundColor = '#FAC858';
                break;
              default:
                fundTypeText = '未明确';
                fundColor = '#909399';
            }
            
            result += `<br/><span style="color:${fundColor};margin-left:16px">◉ ${fundTypeText}</span>`;
          }
          
          // 检查是否在埋伏期
          const inAmbushPeriod = visibleAmbushPeriods.find(
            period => dateIndex >= period.start && dateIndex <= period.end
          );
          
          if (inAmbushPeriod) {
            result += `<br/><span style="color:#f50;margin-top:4px;display:inline-block">◉ ${inAmbushPeriod.desc}</span>`;
          }
          
          return result;
        }
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
      xAxis: {
        type: 'category',
        data: currentDates,
        axisLabel: {
          formatter: value => value.substring(5), // 只显示月-日
          rotate: 45
        }
      },
      yAxis: {
        type: 'value',
        name: yAxisName,
        min: yMin,
        axisLine: {
          lineStyle: {
            color: color
          }
        },
        splitLine: {
          show: true,
          lineStyle: {
            type: 'dashed'
          }
        }
      },
      series: [
        {
          name: seriesName,
          type: 'line',
          data: seriesData,
          smooth: true,
          lineStyle: {
            color: color,
            width: 3
          },
          symbol: 'circle',
          symbolSize: 6,
          markLine: {
            data: [
              {
                name: `${seriesName}阈值`,
                yAxis: threshold,
                lineStyle: {
                  color: '#FF4500',
                  type: 'dashed'
                },
                label: {
                  formatter: `阈值: ${threshold}`,
                  position: 'middle'
                }
              },
              {
                name: '平均值',
                type: 'average',
                lineStyle: {
                  color: '#5470C6',
                  type: 'dashed'
                },
                label: {
                  formatter: '平均: {c}',
                  position: 'end'
                }
              }
            ]
          },
          markArea: {
            silent: true,
            data: getMarkAreas()
          }
        }
      ]
    };
  };
  
  // 准备详细资金特征表格数据
  const prepareTableData = () => {
    return currentDates.map((date, index) => {
      // 判断是否在埋伏期内
      const inAmbushPeriod = visibleAmbushPeriods.find(
        period => index >= period.start && index <= period.end
      );
      
      // 获取资金类型中文名
      const getFundStyleName = (style) => {
        switch(style) {
          case 'institutional': return '机构资金';
          case 'northbound': return '北向资金';
          case 'retail': return '游资主导';
          default: return '未明确';
        }
      };
      
      // 获取大单占比状态
      const getLargeOrderStatus = (ratio) => {
        if (ratio >= 50) return { status: 'strong', text: '强势', color: '#52c41a' };
        if (ratio >= 40) return { status: 'good', text: '良好', color: '#1890ff' };
        return { status: 'weak', text: '偏低', color: '#faad14' };
      };
      
      // 获取买卖比状态
      const getBuySellStatus = (ratio) => {
        if (ratio >= 2.0) return { status: 'strong', text: '明显买入', color: '#52c41a' };
        if (ratio >= 1.5) return { status: 'good', text: '偏买入', color: '#1890ff' };
        if (ratio >= 1.0) return { status: 'neutral', text: '平衡', color: '#d9d9d9' };
        return { status: 'weak', text: '偏卖出', color: '#ff4d4f' };
      };
      
      // 获取主动买盘比例状态
      const getActiveBuyStatus = (ratio) => {
        if (ratio >= 80) return { status: 'strong', text: '非常积极', color: '#52c41a' };
        if (ratio >= 70) return { status: 'good', text: '积极', color: '#1890ff' };
        if (ratio >= 60) return { status: 'neutral', text: '中性', color: '#d9d9d9' };
        return { status: 'weak', text: '被动', color: '#ff4d4f' };
      };
      
      // 获取资金加速度状态
      const getAccelerationStatus = (accel) => {
        if (accel >= 30) return { status: 'strong', text: '快速增长', color: '#52c41a' };
        if (accel >= 10) return { status: 'good', text: '增长', color: '#1890ff' };
        if (accel >= -10) return { status: 'neutral', text: '平稳', color: '#d9d9d9' };
        return { status: 'weak', text: '减速', color: '#ff4d4f' };
      };
      
      // 大单占比状态
      const largeOrderStatus = getLargeOrderStatus(currentLargeOrderRatio[index]);
      
      // 买卖比状态
      const buySellStatus = getBuySellStatus(currentLargeOrderBuySellRatio[index]);
      
      // 主动买盘状态
      const activeBuyStatus = getActiveBuyStatus(currentActiveBuyRatio[index]);
      
      // 资金加速度状态
      const accelerationStatus = getAccelerationStatus(currentInflowAcceleration[index]);
      
      return {
        key: index,
        date: date,
        largeOrderRatio: currentLargeOrderRatio[index],
        largeOrderStatus: largeOrderStatus,
        buySellRatio: currentLargeOrderBuySellRatio[index],
        buySellStatus: buySellStatus,
        activeBuyRatio: currentActiveBuyRatio[index],
        activeBuyStatus: activeBuyStatus,
        acceleration: currentInflowAcceleration[index],
        accelerationStatus: accelerationStatus,
        fundStyle: currentFundStyle[index],
        fundStyleName: getFundStyleName(currentFundStyle[index]),
        isAmbushPeriod: inAmbushPeriod ? true : false,
        ambushDesc: inAmbushPeriod ? inAmbushPeriod.desc : '',
        ambushConfidence: inAmbushPeriod ? inAmbushPeriod.confidence : ''
      };
    });
  };
  
  // 表格列定义
  const tableColumns = [
    {
      title: '日期',
      dataIndex: 'date',
      key: 'date',
      fixed: 'left',
      width: 100,
      render: (text) => text.substring(5) // 只显示月-日
    },
    {
      title: '主力判定',
      dataIndex: 'isAmbushPeriod',
      key: 'isAmbushPeriod',
      width: 100,
      filters: [
        { text: '埋伏期', value: true },
        { text: '非埋伏期', value: false }
      ],
      onFilter: (value, record) => record.isAmbushPeriod === value,
      render: (isAmbush, record) => {
        if (!isAmbush) return <Tag color="#d9d9d9">普通</Tag>;
        
        let color;
        switch(record.ambushConfidence) {
          case 'very-high': color = '#ff4d4f'; break;
          case 'high': color = '#1890ff'; break;
          case 'medium': color = '#52c41a'; break;
          default: color = '#d9d9d9';
        }
        
        return (
          <Tooltip title={record.ambushDesc}>
            <Tag color={color}>主力埋伏</Tag>
          </Tooltip>
        );
      }
    },
    {
      title: '资金类型',
      dataIndex: 'fundStyleName',
      key: 'fundStyleName',
      width: 100,
      filters: [
        { text: '机构资金', value: '机构资金' },
        { text: '北向资金', value: '北向资金' },
        { text: '游资主导', value: '游资主导' },
        { text: '未明确', value: '未明确' }
      ],
      onFilter: (value, record) => record.fundStyleName === value,
      render: (text, record) => {
        let color;
        switch(record.fundStyle) {
          case 'institutional': color = '#5470C6'; break;
          case 'northbound': color = '#91CC75'; break;
          case 'retail': color = '#FAC858'; break;
          default: color = '#909399';
        }
        
        return <Tag color={color}>{text}</Tag>;
      }
    },
    {
      title: '大单占比',
      dataIndex: 'largeOrderRatio',
      key: 'largeOrderRatio',
      sorter: (a, b) => a.largeOrderRatio - b.largeOrderRatio,
      render: (value, record) => (
        <Space>
          <span>{value}%</span>
          <Tag color={record.largeOrderStatus.color}>{record.largeOrderStatus.text}</Tag>
        </Space>
      )
    },
    {
      title: '大单买卖比',
      dataIndex: 'buySellRatio',
      key: 'buySellRatio',
      sorter: (a, b) => a.buySellRatio - b.buySellRatio,
      render: (value, record) => (
        <Space>
          <span>{value.toFixed(2)}</span>
          <Tag color={record.buySellStatus.color}>{record.buySellStatus.text}</Tag>
        </Space>
      )
    },
    {
      title: '主动买盘比例',
      dataIndex: 'activeBuyRatio',
      key: 'activeBuyRatio',
      sorter: (a, b) => a.activeBuyRatio - b.activeBuyRatio,
      render: (value, record) => (
        <Space>
          <span>{value}%</span>
          <Tag color={record.activeBuyStatus.color}>{record.activeBuyStatus.text}</Tag>
        </Space>
      )
    },
    {
      title: '资金流入加速度',
      dataIndex: 'acceleration',
      key: 'acceleration',
      sorter: (a, b) => a.acceleration - b.acceleration,
      render: (value, record) => (
        <Space>
          <span>{value}%</span>
          <Tag color={record.accelerationStatus.color}>{record.accelerationStatus.text}</Tag>
          {value > 0 ? <ArrowUpOutlined style={{ color: '#52c41a' }} /> : 
                       <ArrowDownOutlined style={{ color: '#ff4d4f' }} />}
        </Space>
      )
    }
  ];
  
  // 表格数据
  const tableData = prepareTableData();

  // 获取主要资金类型文本
  const getMainFundTypeText = (type) => {
    switch(type) {
      case 'institutional': return '机构资金';
      case 'northbound': return '北向资金';
      case 'retail': return '游资主导';
      default: return '混合资金';
    }
  };
  
  return (
    <Card bordered={false} style={{ width: '100%' }}>
      <Row gutter={[16, 16]}>
        {/* 顶部控制区 */}
        <Col span={24}>
          <Row justify="space-between" align="middle">
            <Col>
              <Radio.Group 
                value={chartType} 
                onChange={e => setChartType(e.target.value)}
                buttonStyle="solid"
              >
                <Radio.Button value="largeOrderRatio">大单占比</Radio.Button>
                <Radio.Button value="buySellRatio">大单买卖比</Radio.Button>
                <Radio.Button value="activeBuy">主动买盘比例</Radio.Button>
                <Radio.Button value="acceleration">资金流入加速度</Radio.Button>
              </Radio.Group>
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
            option={getFundQualityOption()} 
            style={{ height: '350px' }} 
            notMerge={true}
            lazyUpdate={true}
          />
        </Col>
        
        {/* 资金特征关键指标 */}
        <Col span={24}>
          <Card type="inner" title="资金特征关键指标" size="small">
            <Row gutter={16}>
              <Col span={6}>
                <Statistic 
                  title="平均大单占比" 
                  value={data.indicators.largeOrderAvgRatio}
                  suffix="%"
                  precision={1}
                  valueStyle={{ color: data.indicators.largeOrderAvgRatio >= 40 ? '#52c41a' : '#faad14' }}
                />
                <Tag color={data.indicators.largeOrderAvgRatio >= 40 ? 'green' : 'orange'}>
                  {data.indicators.largeOrderAvgRatio >= 40 ? '主力建仓特征' : '一般水平'}
                </Tag>
              </Col>
              <Col span={6}>
                <Statistic 
                  title="平均主动买盘比例" 
                  value={data.indicators.activeBuyAvgRatio}
                  suffix="%"
                  precision={1}
                  valueStyle={{ color: data.indicators.activeBuyAvgRatio >= 70 ? '#52c41a' : '#faad14' }}
                />
                <Tag color={data.indicators.activeBuyAvgRatio >= 70 ? 'green' : 'orange'}>
                  {data.indicators.activeBuyAvgRatio >= 70 ? '积极买入' : '一般强度'}
                </Tag>
              </Col>
              <Col span={6}>
                <Statistic 
                  title="主要资金类型" 
                  value={getMainFundTypeText(data.indicators.mainFundType)}
                  valueStyle={{ 
                    color: data.indicators.mainFundType === 'institutional' || 
                           data.indicators.mainFundType === 'northbound' ? '#52c41a' : '#faad14' 
                  }}
                />
              </Col>
              <Col span={6}>
                <Statistic 
                  title="北向资金净流入天数" 
                  value={data.indicators.northboundInflowDays}
                  suffix="天"
                  valueStyle={{ color: data.indicators.northboundInflowDays > 15 ? '#52c41a' : '#faad14' }}
                />
                <Tag color={data.indicators.northboundInflowDays > 15 ? 'green' : 'orange'}>
                  {data.indicators.northboundInflowDays > 15 ? '持续流入' : '一般水平'}
                </Tag>
              </Col>
            </Row>
          </Card>
        </Col>
        
        {/* 表格 */}
        <Col span={24}>
          <Divider orientation="left">资金特征详细数据</Divider>
          <Table 
            columns={tableColumns} 
            dataSource={tableData} 
            size="small"
            scroll={{ x: 900 }}
            pagination={{ 
              pageSize: 10,
              showSizeChanger: true,
              pageSizeOptions: ['10', '20', '50'],
              showTotal: total => `共 ${total} 条数据`
            }}
          />
        </Col>
      </Row>
    </Card>
  );
};

export default FundQualityAnalysisChart;