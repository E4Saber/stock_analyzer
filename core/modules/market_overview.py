"""
市场概览模块: 展示市场整体情况，包括指数、板块、热点等
添加了详细的调试信息以便排查问题
"""
import streamlit as st
import pandas as pd
import datetime
import traceback
import akshare as ak
import plotly.express as px
import plotly.graph_objects as go

from modules.data_loader import get_index_data, get_sector_data, get_market_news

def show_market_overview(test_mode=False):
    """展示市场概览页面"""
    st.title("市场概览")

    with st.expander("API原始数据", expanded=False):
        st.write("原始API返回数据:")
        
        if st.button("获取上证指数原始数据"):
            try:
                raw_data = ak.stock_zh_index_daily(symbol="sh000001")
                st.success(f"成功获取 {len(raw_data)} 条数据")
                st.write(f"数据日期范围: {raw_data['date'].min()} 至 {raw_data['date'].max()}")
                st.write(raw_data.head())
            except Exception as e:
                st.error(f"获取原始数据失败: {str(e)}")
    
    # 添加调试信息部分
    with st.expander("调试信息", expanded=True):
        st.write("开始加载市场概览数据...")
    
    # 加载市场数据
    with st.spinner("正在加载市场数据..."):
        # 设置日期范围
        # today = datetime.datetime.now().strftime("%Y%m%d")  # 今天日期
        # 确保不要使用未来日期
        # one_year_ago = (datetime.datetime.now() - datetime.timedelta(days=365)).strftime("%Y%m%d")
        end_date = datetime.datetime.now().strftime("%Y%m%d")
        start_date = (datetime.datetime.now() - datetime.timedelta(days=365)).strftime("%Y%m%d")  # 一年前

        
        with st.expander("调试信息", expanded=True):
            st.write(f"今天日期: {end_date}")
            st.write(f"一年前日期: {start_date}")
        
        try:
            # 获取上证指数数据
            with st.expander("调试信息", expanded=True):
                st.write("尝试获取上证指数数据...")
            
            sh_index = get_index_data("sh000001", start_date, end_date, test_mode)
            
            with st.expander("调试信息", expanded=True):
                st.write(f"上证指数数据获取结果: {'成功' if not sh_index.empty else '失败，返回了空数据'}")
                if not sh_index.empty:
                    st.write(f"上证指数数据行数: {len(sh_index)}")
                    st.write(f"上证指数数据列: {sh_index.columns.tolist()}")
                    st.write("上证指数数据预览:")
                    st.write(sh_index.head())
            
            # 获取深证成指数据
            with st.expander("调试信息", expanded=True):
                st.write("尝试获取深证成指数据...")
            
            sz_index = get_index_data("sz399001", start_date, end_date, test_mode)
            
            with st.expander("调试信息", expanded=True):
                st.write(f"深证成指数据获取结果: {'成功' if not sz_index.empty else '失败，返回了空数据'}")
                if not sz_index.empty:
                    st.write(f"深证成指数据行数: {len(sz_index)}")
                    st.write(f"深证成指数据列: {sz_index.columns.tolist()}")
                    st.write("深证成指数据预览:")
                    st.write(sz_index.head())
            
            # 获取行业板块数据
            with st.expander("调试信息", expanded=True):
                st.write("尝试获取行业板块数据...")
            
            sector_data = get_sector_data(test_mode)
            
            with st.expander("调试信息", expanded=True):
                st.write(f"行业板块数据获取结果: {'成功' if not sector_data.empty else '失败，返回了空数据'}")
                if not sector_data.empty:
                    st.write(f"行业板块数据行数: {len(sector_data)}")
                    st.write(f"行业板块数据列: {sector_data.columns.tolist()}")
                    st.write("行业板块数据预览:")
                    st.write(sector_data.head())
            
            # 布局市场概览组件
            with st.expander("调试信息", expanded=True):
                st.write("开始布局市场概览组件...")
            
            # 显示正式内容
            st.subheader("上证指数")
            
            # 检查上证指数数据是否有效
            if not sh_index.empty:
                if len(sh_index) > 0:
                    with st.expander("调试信息", expanded=True):
                        st.write("处理上证指数数据...")
                        st.write(f"索引类型: {type(sh_index.index)}")
                        st.write(f"收盘价列名: {'close' if 'close' in sh_index.columns else '不存在'}")
                    
                    try:
                        # 尝试获取最新数据
                        sh_latest = sh_index.iloc[-1]
                        sh_prev = sh_index.iloc[-2]
                        
                        with st.expander("调试信息", expanded=True):
                            st.write(f"最新数据: {sh_latest}")
                            st.write(f"前一日数据: {sh_prev}")
                        
                        # 计算日涨跌幅
                        sh_change_pct = (sh_latest['close'] - sh_prev['close']) / sh_prev['close'] * 100
                        
                        st.metric(
                            label="最新收盘价",
                            value=f"{sh_latest['close']:.2f}",
                            delta=f"{sh_change_pct:.2f}%"
                        )
                        
                        # 绘制上证指数走势图
                        fig = px.line(
                            sh_index, 
                            x=sh_index.index, 
                            y="close", 
                            title="上证指数走势图(最近一年)",
                            labels={"close": "收盘价", "index": "日期"}
                        )
                        fig.update_layout(height=400)
                        st.plotly_chart(fig, use_container_width=True)
                    except Exception as e:
                        st.error(f"处理上证指数数据时出错: {str(e)}")
                        with st.expander("调试信息", expanded=True):
                            st.write(f"错误详情: {str(e)}")
                            st.write(traceback.format_exc())
                else:
                    st.error("上证指数数据获取成功，但数据为空。请检查日期范围设置。")
                    with st.expander("调试信息", expanded=True):
                        st.write("请检查以下问题：")
                        st.write("1. 日期范围是否正确（开始日期必须早于结束日期）")
                        st.write("2. 结束日期是否超过今天（无法获取未来数据）")
                        st.write("3. API是否返回了正确格式的数据")
                        st.write(f"指定的日期范围：{start_date} 至 {end_date}")
                
            else:
                st.error("无法获取上证指数数据，API可能返回了错误")
                with st.expander("API诊断", expanded=True):
                    if st.button("测试API连接"):
                        try:
                            test_data = ak.stock_zh_index_daily(symbol="sh000001")
                            st.success(f"API测试成功！获取到 {len(test_data)} 条数据")
                            st.write("数据样例：")
                            st.write(test_data.head())
                        except Exception as e:
                            st.error(f"API测试失败：{str(e)}")
                            st.write(traceback.format_exc())
            
            # 显示深证成指
            st.subheader("深证成指")
            
            # 检查深证成指数据是否有效
            if not sz_index.empty:
                with st.expander("调试信息", expanded=True):
                    st.write("处理深证成指数据...")
                
                try:
                    # 尝试获取最新数据
                    sz_latest = sz_index.iloc[-1]
                    sz_prev = sz_index.iloc[-2]
                    
                    # 计算日涨跌幅
                    sz_change_pct = (sz_latest['close'] - sz_prev['close']) / sz_prev['close'] * 100
                    
                    st.metric(
                        label="最新收盘价",
                        value=f"{sz_latest['close']:.2f}",
                        delta=f"{sz_change_pct:.2f}%"
                    )
                    
                    # 绘制深证成指走势图
                    fig = px.line(
                        sz_index, 
                        x=sz_index.index, 
                        y="close", 
                        title="深证成指走势图(最近一年)",
                        labels={"close": "收盘价", "index": "日期"}
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.error(f"处理深证成指数据时出错: {str(e)}")
                    with st.expander("调试信息", expanded=True):
                        st.write(f"错误详情: {str(e)}")
                        st.write(traceback.format_exc())
            else:
                st.error("无法获取深证成指数据")
            
            # 行业板块涨跌幅
            st.subheader("行业板块涨跌幅")
            
            if not sector_data.empty:
                with st.expander("调试信息", expanded=True):
                    st.write("处理行业板块数据...")
                    st.write(f"涨跌幅列名: {'涨跌幅' if '涨跌幅' in sector_data.columns else '不存在'}")
                    st.write(f"板块名称列名: {'板块名称' if '板块名称' in sector_data.columns else '不存在'}")
                
                try:
                    # 检查必要的列是否存在
                    if '涨跌幅' in sector_data.columns and '板块名称' in sector_data.columns:
                        # 选择前15个行业板块
                        top_sectors = sector_data.sort_values(by="涨跌幅", ascending=False).head(15)
                        
                        fig = px.bar(
                            top_sectors,
                            x="板块名称",
                            y="涨跌幅",
                            color="涨跌幅",
                            color_continuous_scale=px.colors.diverging.RdBu_r,
                            title="行业板块涨跌幅排行(Top 15)"
                        )
                        fig.update_layout(height=500)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.error("行业板块数据缺少必要的列")
                except Exception as e:
                    st.error(f"处理行业板块数据时出错: {str(e)}")
                    with st.expander("调试信息", expanded=True):
                        st.write(f"错误详情: {str(e)}")
                        st.write(traceback.format_exc())
            else:
                st.error("无法获取行业板块数据")
                
        except Exception as e:
            st.error(f"加载市场数据时出错: {str(e)}")
            with st.expander("调试信息", expanded=True):
                st.write(f"错误详情: {str(e)}")
                st.write(traceback.format_exc())