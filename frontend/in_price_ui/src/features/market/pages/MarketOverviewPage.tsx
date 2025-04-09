import React from 'react';
import { Typography, Card, Row, Col, Statistic, Divider } from 'antd';
import { ArrowUpOutlined, ArrowDownOutlined } from '@ant-design/icons';

const { Title } = Typography;

const MarketOverviewPage: React.FC = () => {
    return (
        <div className="page-content">
            <Title level={2}>市场概览</Title>
            
            <Divider />
            
            <Row gutter={[16, 16]}>
                <Col span={8}>
                    <Card title="上证指数" bordered={false}>
                        <Statistic
                            value={3483.25}
                            precision={2}
                            valueStyle={{ color: '#cf1322' }}
                            prefix={<ArrowUpOutlined />}
                            suffix="+0.68%"
                        />
                    </Card>
                </Col>
                <Col span={8}>
                    <Card title="深证成指" bordered={false}>
                        <Statistic
                            value={13678.48}
                            precision={2}
                            valueStyle={{ color: '#cf1322' }}
                            prefix={<ArrowUpOutlined />}
                            suffix="+0.95%"
                        />
                    </Card>
                </Col>
                <Col span={8}>
                    <Card title="创业板指" bordered={false}>
                        <Statistic
                            value={2784.36}
                            precision={2}
                            valueStyle={{ color: '#3f8600' }}
                            prefix={<ArrowDownOutlined />}
                            suffix="-0.21%"
                        />
                    </Card>
                </Col>
            </Row>
            
            <Divider>全球市场</Divider>
            
            <Row gutter={[16, 16]}>
                <Col span={8}>
                    <Card title="道琼斯指数" bordered={false}>
                        <Statistic
                            value={36742.35}
                            precision={2}
                            valueStyle={{ color: '#cf1322' }}
                            prefix={<ArrowUpOutlined />}
                            suffix="+0.45%"
                        />
                    </Card>
                </Col>
                <Col span={8}>
                    <Card title="纳斯达克指数" bordered={false}>
                        <Statistic
                            value={16378.92}
                            precision={2}
                            valueStyle={{ color: '#cf1322' }}
                            prefix={<ArrowUpOutlined />}
                            suffix="+0.73%"
                        />
                    </Card>
                </Col>
                <Col span={8}>
                    <Card title="恒生指数" bordered={false}>
                        <Statistic
                            value={19842.36}
                            precision={2}
                            valueStyle={{ color: '#3f8600' }}
                            prefix={<ArrowDownOutlined />}
                            suffix="-0.32%"
                        />
                    </Card>
                </Col>
            </Row>

        </div>
    );
};

export default MarketOverviewPage;