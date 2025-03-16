# 修改 news_collector.py 文件

"""
新闻收集模块: 获取和展示市场热点资讯
"""
import streamlit as st
import pandas as pd
import akshare as ak

def get_market_news(limit=30):
    """获取市场最新资讯
    
    参数:
        limit (int): 获取的新闻条数
        
    返回:
        pandas.DataFrame: 市场资讯
    """
    try:
        # 获取东方财富网新闻
        stock_news = ak.stock_news_em()
        
        # 确保返回的不是空 DataFrame
        if stock_news.empty:
            return pd.DataFrame(columns=["date", "title", "url", "content"])
        
        # 打印列名，以便调试
        print("新闻数据的列名:", stock_news.columns.tolist())
        
        # 根据实际返回的列名重命名为标准列名
        columns_map = {
            # 以下是可能的列名映射，根据实际情况调整
            "日期": "date",
            "标题": "title",
            "链接": "url",
            "内容": "content",
            # 英文列名的可能性
            "date": "date",
            "title": "title", 
            "url": "url",
            "content": "content"
        }
        
        # 创建一个新 DataFrame，包含转换后的列名
        news_data = pd.DataFrame()
        
        for old_col, new_col in columns_map.items():
            if old_col in stock_news.columns:
                news_data[new_col] = stock_news[old_col]
        
        # 如果缺少某些必要的列，添加空列
        for col in ["date", "title", "url"]:
            if col not in news_data.columns:
                news_data[col] = ""
                
        return news_data.head(limit)
    except Exception as e:
        print(f"获取市场资讯失败: {e}")
        return pd.DataFrame(columns=["date", "title", "url", "content"])

def show_news_page():
    """展示热点资讯页面"""
    st.title("热点资讯")
    
    # 获取市场热点资讯
    with st.spinner("正在获取最新资讯..."):
        news_data = get_market_news(limit=30)
        
        if not news_data.empty and "title" in news_data.columns:
            # 显示资讯列表
            for _, row in news_data.iterrows():
                # 确保标题不为空
                title = row.get("title", "无标题")
                if not title:
                    title = "无标题"
                    
                with st.expander(f"{title}"):
                    # 显示日期（如果存在）
                    if "date" in row and row["date"]:
                        st.write(f"**发布日期**: {row['date']}")
                    
                    # 显示链接（如果存在）
                    if "url" in row and row["url"]:
                        st.markdown(f"[阅读原文]({row['url']})")
                    
                    # 显示内容（如果存在）
                    if "content" in row and row["content"]:
                        st.write(row["content"])
        else:
            st.error("无法获取市场资讯或数据格式不正确")
            
            # 显示调试信息
            if not news_data.empty:
                st.warning("获取到数据，但格式可能不符合预期")
                st.write("获取到的列名:", news_data.columns.tolist())
                st.write("数据预览:")
                st.write(news_data.head())