"""
环境诊断工具: 用于检查环境配置和AKShare API可用性
"""
import streamlit as st
import pandas as pd
import sys
import importlib
import traceback

def check_environment():
    """检查环境配置和依赖包版本"""
    env_info = {
        "Python版本": sys.version,
        "依赖包版本": {}
    }
    
    # 检查关键依赖包
    packages = ["akshare", "pandas", "numpy", "streamlit", "plotly", "talib"]
    
    for package in packages:
        try:
            module = importlib.import_module(package)
            version = getattr(module, "__version__", "未知")
            env_info["依赖包版本"][package] = version
        except ImportError:
            env_info["依赖包版本"][package] = "未安装"
        except Exception as e:
            env_info["依赖包版本"][package] = f"错误: {str(e)}"
    
    return env_info

def test_akshare_api():
    """测试AKShare API的可用性"""
    try:
        import akshare as ak
        
        api_tests = {}
        
        # 测试获取股票列表
        try:
            stock_info = ak.stock_info_a_code_name()
            api_tests["股票列表(stock_info_a_code_name)"] = {
                "状态": "成功" if not stock_info.empty else "失败",
                "数据行数": len(stock_info) if not stock_info.empty else 0,
                "数据列": stock_info.columns.tolist() if not stock_info.empty else []
            }
        except Exception as e:
            api_tests["股票列表(stock_info_a_code_name)"] = {
                "状态": "错误",
                "错误信息": str(e)
            }
        
        # 测试获取个股历史数据
        try:
            stock_data = ak.stock_zh_a_hist(symbol="sh600000", period="daily", start_date="20230301", end_date="20230310")
            api_tests["个股历史数据(stock_zh_a_hist)"] = {
                "状态": "成功" if not stock_data.empty else "失败",
                "数据行数": len(stock_data) if not stock_data.empty else 0,
                "数据列": stock_data.columns.tolist() if not stock_data.empty else []
            }
        except Exception as e:
            api_tests["个股历史数据(stock_zh_a_hist)"] = {
                "状态": "错误",
                "错误信息": str(e)
            }
        
        # 测试获取指数数据
        try:
            index_data = ak.stock_zh_index_daily(symbol="sh000001")
            api_tests["指数数据(stock_zh_index_daily)"] = {
                "状态": "成功" if not index_data.empty else "失败",
                "数据行数": len(index_data) if not index_data.empty else 0,
                "数据列": index_data.columns.tolist() if not index_data.empty else [],
                "索引类型": str(type(index_data.index)) if not index_data.empty else "未知"
            }
        except Exception as e:
            api_tests["指数数据(stock_zh_index_daily)"] = {
                "状态": "错误",
                "错误信息": str(e)
            }
        
        # 测试获取行业板块数据
        try:
            sector_data = ak.stock_sector_spot()
            api_tests["行业板块数据(stock_sector_spot)"] = {
                "状态": "成功" if not sector_data.empty else "失败",
                "数据行数": len(sector_data) if not sector_data.empty else 0,
                "数据列": sector_data.columns.tolist() if not sector_data.empty else []
            }
        except Exception as e:
            api_tests["行业板块数据(stock_sector_spot)"] = {
                "状态": "错误",
                "错误信息": str(e)
            }
        
        # 测试获取新闻数据
        try:
            news_data = ak.stock_news_em()
            api_tests["新闻数据(stock_news_em)"] = {
                "状态": "成功" if not news_data.empty else "失败",
                "数据行数": len(news_data) if not news_data.empty else 0,
                "数据列": news_data.columns.tolist() if not news_data.empty else []
            }
        except Exception as e:
            api_tests["新闻数据(stock_news_em)"] = {
                "状态": "错误",
                "错误信息": str(e)
            }
        
        return api_tests
    except Exception as e:
        return {"总体错误": str(e), "详细信息": traceback.format_exc()}

def show_environment_info():
    """显示环境信息和API测试结果"""
    st.title("环境诊断")
    
    # 检查环境配置
    with st.spinner("正在检查环境配置..."):
        env_info = check_environment()
        
        st.subheader("环境配置")
        st.write(f"Python版本: {env_info['Python版本']}")
        
        st.subheader("依赖包版本")
        packages_df = pd.DataFrame(
            {"包名": list(env_info["依赖包版本"].keys()), 
             "版本": list(env_info["依赖包版本"].values())}
        )
        st.table(packages_df)
    
    # 测试AKShare API
    with st.spinner("正在测试AKShare API..."):
        api_tests = test_akshare_api()
        
        st.subheader("AKShare API测试结果")
        
        if "总体错误" in api_tests:
            st.error(f"测试AKShare API时发生错误: {api_tests['总体错误']}")
            st.code(api_tests["详细信息"])
        else:
            for api_name, result in api_tests.items():
                with st.expander(f"{api_name} - {result.get('状态', '未知')}"):
                    if result.get("状态") == "错误":
                        st.error(f"错误信息: {result.get('错误信息', '未知错误')}")
                    else:
                        for key, value in result.items():
                            if key != "状态":
                                st.write(f"{key}: {value}")