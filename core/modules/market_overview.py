"""
市场概览模块: 展示市场整体情况，包括指数、板块、热点等
"""
import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
import plotly.graph_objects as go

from modules.data_loader import get_index_data, get_sector_data, get_market_news

def show_market_overview():
    """展示市场概览页面"""
    st.title("市场概览")
    
    # 加载市场数据
    with st.spinner("正在加载市场数据..."):
        # 设置日期范围
        end_date = datetime.datetime.now().strftime("%Y%m%d")
        start_date = (datetime.datetime.now() - datetime.timedelta(days=365)).strftime("%Y%m%d")  # 一年前
        
        try:
            # 创建选项卡，分组显示不同市场的指数
            tab1, tab2, tab3 = st.tabs(["中国市场", "香港市场", "美国市场"])
            
            # 第一个选项卡：中国市场
            with tab1:
                # 获取上证指数数据
                sh_index = get_index_data("sh000001", start_date, end_date)
                
                # 获取深证成指数据
                sz_index = get_index_data("sz399001", start_date, end_date)
                
                # 创建两列布局
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("上证指数")
                    
                    # 检查上证指数数据是否有效
                    if not sh_index.empty and len(sh_index) > 0:
                        try:
                            # 尝试获取最新数据
                            sh_latest = sh_index.iloc[-1]
                            sh_prev = sh_index.iloc[-2]
                            
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
                            fig.update_layout(height=300)
                            st.plotly_chart(fig, use_container_width=True)
                        except Exception as e:
                            st.error(f"无法显示上证指数数据")
                    else:
                        st.error("无法获取上证指数数据")
                
                with col2:
                    st.subheader("深证成指")
                    
                    # 检查深证成指数据是否有效
                    if not sz_index.empty and len(sz_index) > 0:
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
                            fig.update_layout(height=300)
                            st.plotly_chart(fig, use_container_width=True)
                        except Exception as e:
                            st.error(f"无法显示深证成指数据")
                    else:
                        st.error("无法获取深证成指数据")
            
            # 第二个选项卡：香港市场
            with tab2:
                # 获取恒生指数数据
                hk_index = get_index_data("hkHSI", start_date, end_date)
                
                # 获取恒生科技指数数据
                hk_tech_index = get_index_data("hkHSTECH", start_date, end_date)
                
                # 创建两列布局
                col3, col4 = st.columns(2)
                
                with col3:
                    st.subheader("恒生指数")
                    
                    # 检查恒生指数数据是否有效
                    if not hk_index.empty and len(hk_index) > 0:
                        try:
                            # 尝试获取最新数据
                            hk_latest = hk_index.iloc[-1]
                            hk_prev = hk_index.iloc[-2]
                            
                            # 计算日涨跌幅
                            hk_change_pct = (hk_latest['close'] - hk_prev['close']) / hk_prev['close'] * 100
                            
                            st.metric(
                                label="最新收盘价",
                                value=f"{hk_latest['close']:.2f}",
                                delta=f"{hk_change_pct:.2f}%"
                            )
                            
                            # 绘制恒生指数走势图
                            fig = px.line(
                                hk_index, 
                                x=hk_index.index, 
                                y="close", 
                                title="恒生指数走势图(最近一年)",
                                labels={"close": "收盘价", "index": "日期"}
                            )
                            fig.update_layout(height=300)
                            st.plotly_chart(fig, use_container_width=True)
                        except Exception as e:
                            st.error(f"无法显示恒生指数数据")
                    else:
                        st.error("无法获取恒生指数数据")
                
                with col4:
                    st.subheader("恒生科技指数")
                    
                    # 检查恒生科技指数数据是否有效
                    if not hk_tech_index.empty and len(hk_tech_index) > 0:
                        try:
                            # 尝试获取最新数据
                            hk_tech_latest = hk_tech_index.iloc[-1]
                            hk_tech_prev = hk_tech_index.iloc[-2]
                            
                            #
                            # 计算日涨跌幅
                            hk_tech_change_pct = (hk_tech_latest['close'] - hk_tech_prev['close']) / hk_tech_prev['close'] * 100
                            
                            st.metric(
                                label="最新收盘价",
                                value=f"{hk_tech_latest['close']:.2f}",
                                delta=f"{hk_tech_change_pct:.2f}%"
                            )
                            
                            # 绘制恒生科技指数走势图
                            fig = px.line(
                                hk_tech_index, 
                                x=hk_tech_index.index, 
                                y="close", 
                                title="恒生科技指数走势图(最近一年)",
                                labels={"close": "收盘价", "index": "日期"}
                            )
                            fig.update_layout(height=300)
                            st.plotly_chart(fig, use_container_width=True)
                        except Exception as e:
                            st.error(f"无法显示恒生科技指数数据")
                    else:
                        st.error("无法获取恒生科技指数数据")
            
            # 第三个选项卡：美国市场
            with tab3:
                # 获取标普500指数数据
                us_index = get_index_data("us.SPX", start_date, end_date)
                
                st.subheader("标普500指数")
                
                # 检查标普500指数数据是否有效
                if not us_index.empty and len(us_index) > 0:
                    try:
                        # 尝试获取最新数据
                        us_latest = us_index.iloc[-1]
                        us_prev = us_index.iloc[-2]
                        
                        # 计算日涨跌幅
                        us_change_pct = (us_latest['close'] - us_prev['close']) / us_prev['close'] * 100
                        
                        st.metric(
                            label="最新收盘价",
                            value=f"{us_latest['close']:.2f}",
                            delta=f"{us_change_pct:.2f}%"
                        )
                        
                        # 绘制标普500指数走势图
                        fig = px.line(
                            us_index, 
                            x=us_index.index, 
                            y="close", 
                            title="标普500指数走势图(最近一年)",
                            labels={"close": "收盘价", "index": "日期"}
                        )
                        fig.update_layout(height=400)
                        st.plotly_chart(fig, use_container_width=True)
                    except Exception as e:
                        st.error(f"无法显示标普500指数数据")
                else:
                    st.error("无法获取标普500指数数据")
            
            # 行业板块涨跌幅
            st.subheader("行业板块涨跌幅")
            
            # 获取行业板块数据
            sector_data = get_sector_data()
            
            if not sector_data.empty:
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
                    st.error(f"无法显示行业板块数据")
            else:
                st.error("无法获取行业板块数据")
                
        except Exception as e:
            st.error(f"加载市场数据时出错: {str(e)}")