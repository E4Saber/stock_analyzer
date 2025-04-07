import React, { useEffect, useState } from "react";
import ReactFlow, { Background, Controls, MiniMap, Handle, Position } from "reactflow";
import "reactflow/dist/style.css";
import { Tooltip, Modal, Button } from "antd";
import "antd/dist/reset.css"; // 引入Ant Design的样式

// 定义节点类型接口（修正TypeScript错误）
interface NodeData {
  name: string;
  change: string;
  score: number;
  details: {
    profitability: number;
    growth: number;
    sentiment: number;
  };
  type: string; // supplier, current, customer
}

// 节点接口
interface Node {
  id: string;
  position: {
    x: number;
    y: number;
  };
  data: NodeData;
  type: string;
  style?: React.CSSProperties;
}

// 边接口
interface Edge {
  id: string;
  source: string;
  target: string;
  label: string;
  animated: boolean;
  style?: React.CSSProperties;
}

// 自定义节点组件，使用Ant Design的Tooltip
const CustomNode = ({ data }: { data: NodeData }) => {
  // 根据节点类型设置不同的样式
  const nodeStyle: React.CSSProperties = {
    position: "relative",
    padding: 10,
    background: "#fff",
    border: "1px solid #ddd",
    borderRadius: 5,
    textAlign: "center",
    minWidth: 120
  };
  
  // 根据节点类型设置不同的背景色
  if (data.type === "current") {
    nodeStyle.background = "#e3f2fd"; // 当前企业使用淡蓝色背景
    nodeStyle.border = "2px solid #1976d2";
  } else if (data.type === "supplier") {
    nodeStyle.background = "#e8f5e9"; // 供应商使用淡绿色背景
  } else if (data.type === "customer") {
    nodeStyle.background = "#fff3e0"; // 客户使用淡橙色背景
  }
  
  return (
    <div style={nodeStyle}>
      <div style={{ fontWeight: "bold" }}>{data.name}</div>
      <div style={{ color: data.change.includes("+") ? "green" : "red" }}>{data.change}</div>
      <Tooltip
        title={
          <div>
            <div>盈利能力: {data.details.profitability}/10</div>
            <div>成长性: {data.details.growth}/10</div>
            <div>市场情绪: {data.details.sentiment}/10</div>
          </div>
        }
      >
        <div
          style={{
            position: "absolute",
            top: -10,
            right: -10,
            background: "#ff5722",
            color: "white",
            width: 30,
            height: 30,
            borderRadius: "50%",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            fontWeight: "bold",
            cursor: "pointer"
          }}
        >
          {data.score}
        </div>
      </Tooltip>
      <Handle type="source" position={Position.Right} />
      <Handle type="target" position={Position.Left} />
    </div>
  );
};

// 供应链图谱组件（内部组件）
const SupplyChainGraph = () => {
  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);

  // 示例数据 - 实际使用中可以通过API获取或作为props传入
  const sampleData = {
    // 中心企业（当前公司）
    current: { 
      name: "当前企业", 
      change: "+1.5%", 
      score: 8, 
      details: { profitability: 8, growth: 7, sentiment: 9 } 
    },
    // 上游供应商
    suppliers: [
      { name: "供应商A", change: "+3.5%", score: 8, details: { profitability: 8, growth: 7, sentiment: 6 } },
      { name: "供应商B", change: "-1.2%", score: 6, details: { profitability: 6, growth: 5, sentiment: 7 } },
      { name: "供应商C", change: "+2.1%", score: 7, details: { profitability: 7, growth: 6, sentiment: 8 } }
    ],
    // 下游客户
    customers: [
      { name: "客户A", change: "-2.1%", score: 5, details: { profitability: 5, growth: 4, sentiment: 6 } },
      { name: "客户B", change: "+4.0%", score: 9, details: { profitability: 9, growth: 9, sentiment: 9 } },
      { name: "客户C", change: "+1.2%", score: 7, details: { profitability: 7, growth: 6, sentiment: 7 } }
    ]
  };

  useEffect(() => {
    // 动态计算节点和边
    const calculateNodesAndEdges = () => {
      const calculatedNodes: Node[] = [];
      const calculatedEdges: Edge[] = [];
      
      // 坐标设置
      const centerX = 400; // 中心企业的X坐标
      const supplierX = 100; // 供应商的X坐标
      const customerX = 700; // 客户的X坐标
      const centerY = 250; // 中心企业的Y坐标
      
      // 添加中心企业节点
      calculatedNodes.push({
        id: "current",
        position: { x: centerX, y: centerY },
        data: { ...sampleData.current, type: "current" },
        type: "custom",
        style: { zIndex: 1000 } // 确保中心节点显示在最上层
      });
      
      // 处理供应商节点
      const suppliersCount = sampleData.suppliers.length;
      const suppliersHeight = 500; // 供应商节点的总高度空间
      const suppliersGap = suppliersCount > 1 ? suppliersHeight / (suppliersCount - 1) : 0;
      
      sampleData.suppliers.forEach((item, index) => {
        const nodeId = `supplier-${index}`;
        // 计算Y坐标，使供应商垂直均匀分布
        const yPos = suppliersCount > 1 
          ? (suppliersHeight / 2) - (suppliersHeight / 2) + (index * suppliersGap)
          : centerY;
        
        calculatedNodes.push({
          id: nodeId,
          position: { x: supplierX, y: yPos },
          data: { ...item, type: "supplier" },
          type: "custom"
        });
        
        // 添加从供应商到中心企业的边
        calculatedEdges.push({
          id: `e-${nodeId}-current`,
          source: nodeId,
          target: "current",
          label: "供应",
          animated: true,
          style: { stroke: "#4caf50" } // 供应关系使用绿色
        });
      });
      
      // 处理客户节点
      const customersCount = sampleData.customers.length;
      const customersHeight = 500;
      const customersGap = customersCount > 1 ? customersHeight / (customersCount - 1) : 0;
      
      sampleData.customers.forEach((item, index) => {
        const nodeId = `customer-${index}`;
        // 计算Y坐标，使客户垂直均匀分布
        const yPos = customersCount > 1 
          ? (customersHeight / 2) - (customersHeight / 2) + (index * customersGap)
          : centerY;
        
        calculatedNodes.push({
          id: nodeId,
          position: { x: customerX, y: yPos },
          data: { ...item, type: "customer" },
          type: "custom"
        });
        
        // 添加从中心企业到客户的边
        calculatedEdges.push({
          id: `e-current-${nodeId}`,
          source: "current",
          target: nodeId,
          label: "销售",
          animated: true,
          style: { stroke: "#ff9800" } // 销售关系使用橙色
        });
      });
      
      return { calculatedNodes, calculatedEdges };
    };
    
    const { calculatedNodes, calculatedEdges } = calculateNodesAndEdges();
    setNodes(calculatedNodes);
    setEdges(calculatedEdges);
  }, []);

  // 定义节点类型映射
  const nodeTypes = {
    custom: CustomNode
  };

  return (
    <div style={{ height: "500px", width: "100%" }}>
      <ReactFlow 
        nodes={nodes} 
        edges={edges} 
        nodeTypes={nodeTypes} 
        fitView
      >
        <MiniMap />
        <Controls />
        <Background />
      </ReactFlow>
    </div>
  );
};

// 封装成Modal的供应链图谱组件（导出组件）
interface SupplyChainModalProps {
  visible: boolean;
  onClose: () => void;
  title?: string;
}

export const SupplyChainModal: React.FC<SupplyChainModalProps> = ({ 
  visible, 
  onClose, 
  title = "企业供应链关系图"
}) => {
  return (
    <Modal
      title={title}
      open={visible}
      onCancel={onClose}
      width={1000}
      footer={[
        <Button key="close" onClick={onClose}>
          关闭
        </Button>
      ]}
    >
      <SupplyChainGraph />
    </Modal>
  );
};

// 使用示例组件
export const SupplyChainButton: React.FC = () => {
  const [modalVisible, setModalVisible] = useState(false);

  const showModal = () => {
    setModalVisible(true);
  };

  const hideModal = () => {
    setModalVisible(false);
  };

  return (
    <>
      <Button type="primary" onClick={showModal}>
        查看供应链关系图
      </Button>
      <SupplyChainModal visible={modalVisible} onClose={hideModal} />
    </>
  );
};

export default SupplyChainModal;