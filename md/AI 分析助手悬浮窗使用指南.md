# AI 分析助手悬浮窗使用指南

## 概述

AI 分析助手悬浮窗是一个强大的工具，为散户投资者提供实时、专业的股票分析服务。它能够根据当前查看的股票自动提供上下文感知的分析，让非专业投资者也能获得专业级的分析建议。

## 组件结构

AI 分析助手由两个主要组件组成:

1. **AIAssistantTrigger**: 触发按钮组件，显示在页面的固定位置，用于打开/关闭悬浮窗。
2. **AIAssistantFloat**: 悬浮窗主体组件，包含问题输入、分析选项和结果展示等功能。

## 安装依赖

确保已安装以下依赖:

```bash
npm install react-draggable --save
```

## 使用方法

### 基本用法

将 AI 助手添加到任何页面:

```jsx
import AIAssistantTrigger from '../components/widgets/AIAssistantTrigger';

// 在页面组件中使用
const YourPage = () => {
  const stockData = { /* 股票数据对象 */ };
  
  return (
    <div>
      {/* 页面内容 */}
      
      {/* 添加 AI 助手触发按钮 */}
      <AIAssistantTrigger 
        currentStock={stockData} 
        position="bottom-right" 
      />
    </div>
  );
};
```

### 参数说明

#### AIAssistantTrigger 组件参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| currentStock | StockData | undefined | 当前查看的股票数据 |
| position | 'top-right' \| 'bottom-right' \| 'bottom-left' \| 'top-left' | 'bottom-right' | 触发按钮在页面中的位置 |

#### AIAssistantFloat 组件参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| currentStock | StockData | undefined | 当前查看的股票数据 |
| visible | boolean | - | 悬浮窗是否可见 |
| onClose | () => void | - | 关闭按钮点击事件 |
| onMinimize | () => void | - | 最小化按钮点击事件 |

## 功能特点

### 1. 可拖拽

悬浮窗可以通过拖拽头部移动到页面的任何位置，方便用户在不同位置查看分析内容。

### 2. 可调整大小

右下角的调整手柄允许用户根据需要调整悬浮窗的大小。

### 3. 最小化功能

用户可以最小化悬浮窗，它会变成一个浮动图标，不影响页面内容的查看。

### 4. 多维度分析

用户可以选择需要的分析维度，包括:
- 技术面分析
- 资金面分析
- 消息面分析
- 行业对比分析
- 历史模式分析

### 5. 预设问题

提供常见问题列表，用户可以直接点击选择，不需要手动输入。

### 6. 结果保存与分享

分析结果可以保存或分享给其他用户。

## 集成到项目中

### 1. 将组件文件添加到项目

将以下文件添加到项目中:
- `src/components/widgets/AIAssistantFloat.tsx`
- `src/components/widgets/AIAssistantFloat.css`
- `src/components/widgets/AIAssistantTrigger.tsx`

### 2. 修改 App.tsx

更新路由配置，添加 AI 版本的股票详情页:

```jsx
<Routes>
  {/* 其他路由 */}
  <Route path="/stocks/:code" element={<StockDetail />} />
  <Route path="/stocks-ai/:code" element={<StockDetailWithAI />} />
</Routes>
```

### 3. 创建股票详情 AI 版页面

创建 `StockDetailWithAI.tsx` 页面，集成 AI 分析功能。

## 自定义与扩展

### 自定义分析维度

修改 `AIAssistantFloat.tsx` 中的 `ANALYSIS_DIMENSIONS` 常量可以自定义分析维度:

```jsx
const ANALYSIS_DIMENSIONS = [
  { key: 'technical', label: '技术面', icon: <LineChartOutlined /> },
  // 添加更多维度
];
```

### 自定义预设问题

修改 `AIAssistantFloat.tsx` 中的 `PRESET_QUESTIONS` 常量可以自定义预设问题:

```jsx
const PRESET_QUESTIONS = [
  '该股近期技术面如何？',
  // 添加更多问题
];
```

### 连接实际 AI 分析服务

实际应用中，需要将 `handleAnalyze` 函数连接到真实的 AI 分析服务:

```jsx
const handleAnalyze = async () => {
  if (!question || !currentStock) return;
  
  setAnalyzing(true);
  
  try {
    // 调用实际的 AI 分析 API
    const response = await apiClient.post('/ai/analyze', {
      stockCode: currentStock.code,
      question: question,
      dimensions: selectedDimensions
    });
    
    setAnalysisResult(response.data);
  } catch (error) {
    console.error('分析请求失败:', error);
    // 错误处理逻辑
  } finally {
    setAnalyzing(false);
  }
};
```

## 最佳实践

1. **保持分析结果简洁明了**: 避免过于专业或复杂的表述，确保普通散户能够理解。

2. **突出风险提示**: 在分析结果中明确指出潜在风险，帮助用户做出更理性的决策。

3. **响应式设计**: 确保在不同屏幕尺寸下都能有良好的显示效果。

4. **性能优化**: 大量分析数据可能导致性能问题，考虑使用虚拟滚动等技术优化长列表。

5. **增加教育功能**: 对专业术语添加解释说明，帮助用户学习和理解。

## 常见问题

### Q: 悬浮窗会占用大量屏幕空间吗?
A: 悬浮窗支持任意位置拖动、大小调整和最小化，用户可以根据需要灵活控制显示方式，不影响主要内容查看。

### Q: 如何在多个页面共享分析结果?
A: 可以实现分析结果保存功能，将结果存储在本地存储或服务端，在不同页面间共享。

### Q: 分析频率是否有限制?
A: 这取决于后端 AI 服务的处理能力和限制。一般建议实现合理的节流或限制机制，避免过于频繁的请求。