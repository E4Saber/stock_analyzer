import React from "react";
import ReactFlow, { Background, Controls, MiniMap, Handle, Position, EdgeLabelRenderer } from "reactflow";
import "reactflow/dist/style.css";
import Tooltip from "@mui/material/Tooltip";

const stockNodes = [
  { id: "1", position: { x: 0, y: 0 }, data: { name: "上游企业A", change: "+3.5%", score: 8, details: { profitability: 8, growth: 7, sentiment: 6 } }, type: "custom" },
  { id: "2", position: { x: 0, y: 150 }, data: { name: "上游企业B", change: "-1.2%", score: 6, details: { profitability: 6, growth: 5, sentiment: 7 } }, type: "custom" },
  { id: "3", position: { x: 250, y: 75 }, data: { name: "中间企业C", change: "+0.8%", score: 7, details: { profitability: 7, growth: 6, sentiment: 8 } }, type: "custom" },
  { id: "4", position: { x: 500, y: 0 }, data: { name: "下游企业D", change: "-2.1%", score: 5, details: { profitability: 5, growth: 4, sentiment: 6 } }, type: "custom" },
  { id: "5", position: { x: 500, y: 150 }, data: { name: "下游企业E", change: "+4.0%", score: 9, details: { profitability: 9, growth: 9, sentiment: 9 } }, type: "custom" },
  { id: "6", position: { x: 750, y: 75 }, data: { name: "终端企业F", change: "+1.2%", score: 7, details: { profitability: 7, growth: 6, sentiment: 7 } }, type: "custom" }
];

const stockEdges = [
  { id: "e1-3", source: "1", target: "3", label: "电子元件", animated: true },
  { id: "e2-3", source: "2", target: "3", label: "原材料", animated: true },
  { id: "e3-4", source: "3", target: "4", label: "半导体组件", animated: true },
  { id: "e3-5", source: "3", target: "5", label: "光伏材料", animated: true },
  { id: "e5-6", source: "5", target: "6", label: "终端设备", animated: true }
];

const CustomNode = ({ data }) => (
  <div style={{ position: "relative", padding: 10, background: "#fff", border: "1px solid #ddd", borderRadius: 5, textAlign: "center", minWidth: 120 }}>
    <div style={{ fontWeight: "bold" }}>{data.name}</div>
    <div style={{ color: data.change.includes("+") ? "green" : "red" }}>{data.change}</div>
    <Tooltip
      title={<div>
        <div>盈利能力: {data.details.profitability}/10</div>
        <div>成长性: {data.details.growth}/10</div>
        <div>市场情绪: {data.details.sentiment}/10</div>
      </div>}
      arrow
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

export default function SupplyChainGraph() {
  return (
    <div style={{ height: "500px", width: "100%" }}>
      <ReactFlow nodes={stockNodes} edges={stockEdges} nodeTypes={{ custom: CustomNode }} fitView>
        <MiniMap />
        <Controls />
        <Background />
      </ReactFlow>
    </div>
  );
}
