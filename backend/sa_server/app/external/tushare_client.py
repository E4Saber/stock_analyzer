# app/external/tushare_client.py
import os
import tushare as ts
from dotenv import load_dotenv


# 加载环境变量
load_dotenv()

def get_tushare_client():
    """
    获取Tushare API实例
    """
    # 初始化Tushare
    try:
        ts.set_token(os.getenv("TUSHARE_TOKEN", ""))
        pro = ts.pro_api()
    except Exception as e:
        print(f"Tushare初始化错误: {str(e)}")
        # 使用空的API实例，后续会进行错误处理
        pro = None
    
    return pro
# app/services/tushare_services.py
