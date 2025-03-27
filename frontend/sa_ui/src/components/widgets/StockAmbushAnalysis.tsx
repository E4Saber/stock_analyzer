import React, { useState } from 'react';
import { 
  Card, 
  Row, 
  Col, 
  Statistic, 
  Modal, 
  Tabs, 
  Input, 
  Button, 
  Tag, 
  Tooltip,
  Typography,
  Alert 
} from 'antd';
import { 
  LineChartOutlined,
  SecurityScanOutlined,
  StockOutlined,
  TeamOutlined,
  GlobalOutlined
} from '@ant-design/icons';
import FundFlowOverviewChart from '../charts/FundFlowOverviewChart';
import FundQualityAnalysisChart from '../charts/FundQualityAnalysisChart';
import VolumePriceRelationshipChart from '../charts/VolumePriceRelationshipChart';

const { Title, Paragraph } = Typography;
const { TabPane } = Tabs;

// 定义模块分数和详情接口
interface ModuleScore {
  id: number
  name: string;
  score: number;
  weight: number;
  details: string[];
  icon: React.ReactNode;
}

const StockAmbushAnalysis: React.FC = () => {
  const [selectedModule, setSelectedModule] = useState<ModuleScore | null>(null);
  
  // 模拟模块数据
  const modules: ModuleScore[] = [
    {
      id: 1,
      name: '资金流入特征',
      score: 82.5,
      weight: 0.3,
      details: [
        '连续15天资金净流入',
        '尾盘资金占比42%',
        '资金流入稳定性高'
      ],
      icon: <LineChartOutlined />
    },
    {
      id: 2,
      name: '筹码结构特征',
      score: 78.3,
      weight: 0.25,
      details: [
        '筹码集中度提升0.045',
        '股东户数减少7.2%',
        '大单买入比例上升'
      ],
      icon: <SecurityScanOutlined />
    },
    {
      id: 3,
      name: '技术形态特征',
      score: 75.6,
      weight: 0.2,
      details: [
        '底部W形态',
        '波动收敛特征明显',
        '均线系统转多头'
      ],
      icon: <StockOutlined />
    },
    {
      id: 4,
      name: '主力特征判断',
      score: 80.1,
      weight: 0.15,
      details: [
        '机构资金持续流入',
        '北向资金增持',
        '主力建仓完成度高'
      ],
      icon: <TeamOutlined />
    },
    {
      id: 5,
      name: '市场环境匹配',
      score: 72.9,
      weight: 0.1,
      details: [
        '行业板块轮动信号',
        '政策预期向好',
        '估值处于合理区间'
      ],
      icon: <GlobalOutlined />
    }
  ];

  // 计算总分
  const totalScore = modules.reduce((sum, module) => sum + module.score * module.weight, 0);

  // 根据总分获取描述
  const getTotalScoreDescription = (score: number) => {
    if (score >= 85) return '极高可靠性，建议重点关注';
    if (score >= 75) return '高可靠性，值得深入研究';
    if (score >= 65) return '中等可靠性，需谨慎评估';
    return '低可靠性，不推荐';
  };

  // 模块详情弹窗
  const ModuleDetailsModal = () => {
    if (!selectedModule) return null;

    return (
      <Modal
        title={`${selectedModule.name}详细分析`}
        visible={!!selectedModule}
        onCancel={() => setSelectedModule(null)}
        footer={null}
        width={800}
      >
        <Row gutter={16}>
          <Col span={12}>
            <Card>
              <Statistic 
                title="模块得分" 
                value={selectedModule.score} 
                precision={2}
                valueStyle={{ color: '#3f8600' }}
                prefix={selectedModule.icon}
              />
              <Paragraph style={{ marginTop: 16 }}>
                权重: {(selectedModule.weight * 100).toFixed(0)}%
              </Paragraph>
            </Card>
          </Col>
          <Col span={12}>
            <Card title="关键指标">
              {selectedModule.details.map((detail, index) => (
                <Tag key={index} color="processing" style={{ margin: 4 }}>
                  {detail}
                </Tag>
              ))}
            </Card>
          </Col>
        </Row>
        {selectedModule.id === 1 && 
          <Row gutter={16}>
            <Col span={24}>
                <FundFlowOverviewChart />
                <FundQualityAnalysisChart />
                <VolumePriceRelationshipChart />
            </Col>
          </Row>
        }
      </Modal>
    );
  };

  return (
    <div style={{ padding: 24 }}>
      {/* 模块得分卡片 */}
      <Card 
        title="资金埋伏股票分析报告" 
        extra={
          <Tooltip title={getTotalScoreDescription(totalScore)}>
            <Statistic 
              title="总分" 
              value={totalScore} 
              precision={2}
              valueStyle={{ 
                color: totalScore >= 75 ? '#3f8600' : '#cf1322',
                fontWeight: 'bold'
              }}
            />
          </Tooltip>
        }
      >
        <Row gutter={[16, 16]}>
          {modules.map((module) => (
            <Col key={module.name} span={4}>
              <Card 
                hoverable 
                onClick={() => setSelectedModule(module)}
                style={{ textAlign: 'center' }}
              >
                <div style={{ fontSize: 32, color: '#1890ff', marginBottom: 16 }}>
                  {module.icon}
                </div>
                <Statistic 
                  title={module.name} 
                  value={module.score} 
                  precision={2}
                  valueStyle={{ color: '#1890ff' }}
                />
                <Paragraph type="secondary" style={{ marginTop: 8 }}>
                  权重: {(module.weight * 100).toFixed(0)}%
                </Paragraph>
              </Card>
            </Col>
          ))}
        </Row>
      </Card>

      {/* 回测与建议 */}
      <Card style={{ marginTop: 24 }}>
        <Tabs defaultActiveKey="1">
          <TabPane tab="回测" key="1">
            <Row gutter={16}>
              <Col span={12}>
                <Card title="回测配置">
                  <Input 
                    addonBefore="股票代码" 
                    placeholder="例如：600519" 
                    style={{ marginBottom: 16 }}
                  />
                  <Input 
                    addonBefore="起始日期" 
                    type="date" 
                    style={{ marginBottom: 16 }}
                  />
                  <Input 
                    addonBefore="结束日期" 
                    type="date" 
                    style={{ marginBottom: 16 }}
                  />
                  <Button type="primary" block>
                    开始回测
                  </Button>
                </Card>
              </Col>
              <Col span={12}>
                <Card title="回测结果">
                  <Alert 
                    message="暂无回测结果" 
                    description="请输入参数并点击开始回测" 
                    type="info" 
                    showIcon 
                  />
                </Card>
              </Col>
            </Row>
          </TabPane>
          <TabPane tab="操作建议" key="2">
            <Card>
              <Title level={4}>策略建议</Title>
              <ul>
                <li>
                  <Tag color="success">建仓策略</Tag>
                  首次建仓30%，突破确认后追加30%
                </li>
                <li>
                  <Tag color="warning">止损设置</Tag>
                  跌破30日均线或8%价格止损
                </li>
                <li>
                  <Tag color="processing">验证周期</Tag>
                  15-30天（中线操作）
                </li>
                <li>
                  <Tag color="error">风险提示</Tag>
                  仅供参考，实际操作需要综合考虑
                </li>
              </ul>
            </Card>
          </TabPane>
        </Tabs>
      </Card>

      {/* 模块详情弹窗 */}
      <ModuleDetailsModal />
    </div>
  );
};

export default StockAmbushAnalysis;