import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

"""
数据可视化模块: 负责绘制各类图表
"""

def plot_candlestick(df, title="K线图", height=600, include_volume=True):
    """绘制K线图"""
    if df.empty:
        return go.Figure()
        
    if include_volume:
        fig = make_subplots(
            rows=2, 
            cols=1, 
            shared_xaxes=True,
            vertical_spacing=0.03,
            row_heights=[0.7, 0.3]
        )
    else:
        fig = go.Figure()
    
    # 添加K线图
    candlestick = go.Candlestick(
        x=df['日期'] if '日期' in df.columns else df.index,
        open=df['开盘'],
        high=df['最高'],
        low=df['最低'],
        close=df['收盘'],
        name="K线"
    )
    
    if include_volume:
        fig.add_trace(candlestick, row=1, col=1)
        
        # 添加成交量
        colors = ['red' if row['收盘'] >= row['开盘'] else 'green' for _, row in df.iterrows()]
        volume_bars = go.Bar(
            x=df['日期'] if '日期' in df.columns else df.index,
            y=df['成交量'],
            marker_color=colors,
            name="成交量"
        )
        fig.add_trace(volume_bars, row=2, col=1)
    else:
        fig.add_trace(candlestick)
    
    # 添加均线 (如果存在)
    for ma in ['MA5', 'MA10', 'MA20', 'MA60']:
        if ma in df.columns:
            ma_scatter = go.Scatter(
                x=df['日期'] if '日期' in df.columns else df.index,
                y=df[ma],
                mode='lines',
                name=ma
            )
            if include_volume:
                fig.add_trace(ma_scatter, row=1, col=1)
            else:
                fig.add_trace(ma_scatter)
    
    # 更新图表布局
    fig.update_layout(
        title=title,
        height=height,
        xaxis_rangeslider_visible=False
    )
    
    return fig

def plot_technical_indicators(df, indicators):
    """绘制技术指标图表"""
    # 实现代码略
    pass
