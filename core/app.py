import streamlit as st
from modules.market_overview import show_market_overview
# from modules.stock_analyzer import show_stock_analyzer
from modules.news_collector import show_news_page
from modules.environment_checker import show_environment_info

# 页面配置
st.set_page_config(page_title="量化分析平台", page_icon="📈", layout="wide")

# 自定义CSS样式
st.markdown("""
<style>
    .main {background-color: #f5f7fa;}
    h1, h2, h3 {color: #1E3A8A;}
</style>
""", unsafe_allow_html=True)

# 侧边栏
with st.sidebar:
    st.title("量化分析平台")
    
    analysis_options = ["市场概览", "个股分析", "热点资讯", "环境诊断"]
    selected_analysis = st.selectbox("选择分析类型", analysis_options)
    
    st.markdown("---")
    st.caption("本应用使用AKShare获取数据，结合Streamlit构建前端界面。")
    st.caption("数据仅供参考，不构成投资建议。")

# 根据选择的分析类型显示对应的页面
if selected_analysis == "市场概览":
    show_market_overview()
# elif selected_analysis == "个股分析":
#     show_stock_analyzer()
# elif selected_analysis == "热点资讯":
#     show_news_page()
# elif selected_analysis == "环境诊断":
#     show_environment_info()