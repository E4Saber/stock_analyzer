from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta
import json

from app.data.modules.cn_index_data import CNIndexBaseData, CNIndexData
from app.external.tushare_client import get_cn_indices

# 导入您的数据模型
from app.data.modules.cn_index_data import CNIndexBaseData, CNIndexData
from app.data.modules.global_index_data import GlobalIndexData

from app.utils.date_utils import get_yesterday_yyyymmdd

# 定义API响应模型
class IndexResponse(BaseModel):
    """API响应通用结构"""
    code: int = 200
    message: str = "success"
    data: Any
    
    class Config:
        from_attributes = True
        arbitrary_types_allowed = True

# 处理函数

def transform_cn_index_for_ui(base_data: CNIndexBaseData, index_data: List[CNIndexData]) -> Dict:
    """
    转换A股指数数据为前端UI需要的格式
    
    Args:
        base_data (CNIndexBaseData): 指数基本信息
        index_data (List[CNIndexData]): 指数历史行情数据
        
    Returns:
        Dict: 适合前端UI使用的数据结构
    """
    # 获取最新一天的数据
    latest_data = index_data[0] if index_data else None
    
    # 转换基本信息
    result = {
        "code": base_data.ts_code.split('.')[0],  # 移除后缀，如 000001.SH -> 000001
        "name": base_data.name,
        "fullname": base_data.fullname,
        "market": base_data.market,
        "publisher": base_data.publisher,
        "category": base_data.category,
        "base_date": base_data.base_date,
        "description": base_data.desc,
    }
    
    # 添加最新行情
    if latest_data:
        result.update({
            "current": latest_data.close,
            "change": latest_data.change,
            "change_percent": latest_data.pct_chg,
            "open": latest_data.open,
            "high": latest_data.high,
            "low": latest_data.low,
            "pre_close": latest_data.pre_close,
            "volume": latest_data.vol,
            "amount": latest_data.amount,
            "date": latest_data.trade_date,
        })
    
    # 转换K线历史数据为前端需要的格式
    kline_data = []
    for data in index_data:
        kline_data.append({
            "date": data.trade_date,
            "open": data.open,
            "close": data.close,
            "low": data.low,
            "high": data.high,
            "volume": data.vol,
            "amount": data.amount,
        })
    
    result["kline_data"] = kline_data
    
    return result

def transform_hk_index_for_ui(index_code: str, index_name: str, index_data: List[GlobalIndexData], dates: List[str]) -> Dict:
    """
    转换港股指数数据为前端UI需要的格式
    
    Args:
        index_code (str): 指数代码
        index_name (str): 指数名称
        index_data (List[HKIndexData]): 指数历史行情数据
        dates (List[str]): 对应的日期列表
        
    Returns:
        Dict: 适合前端UI使用的数据结构
    """
    # 获取最新一天的数据
    latest_data = index_data[0] if index_data else None
    latest_date = dates[0] if dates else datetime.now().strftime("%Y-%m-%d")
    
    # 转换基本信息
    result = {
        "code": index_code,
        "name": index_name,
    }
    
    # 添加最新行情
    if latest_data:
        pre_close = index_data[1].close if len(index_data) > 1 else latest_data.close
        change = latest_data.close - pre_close
        change_percent = (change / pre_close * 100) if pre_close != 0 else 0
        
        result.update({
            "current": latest_data.close,
            "change": round(change, 2),
            "change_percent": round(change_percent, 2),
            "open": latest_data.open,
            "high": latest_data.high,
            "low": latest_data.low,
            "pre_close": pre_close,
            "volume": latest_data.volume,
            "date": latest_date,
        })
    
    # 转换K线历史数据为前端需要的格式
    kline_data = []
    for i, data in enumerate(index_data):
        if i < len(dates):
            kline_data.append({
                "date": dates[i],
                "open": data.open,
                "close": data.close,
                "low": data.low,
                "high": data.high,
                "volume": data.volume,
            })
    
    result["kline_data"] = kline_data
    
    return result

# API端点处理函数
def get_index_detail(index_code: str) -> IndexResponse:
    """
    获取指数详情API
    
    Args:
        index_code (str): 指数代码，如 000001 (上证指数)
        
    Returns:
        IndexResponse: API响应
    """
    try:
        # 这里应该是从数据库或外部API获取数据
        # 以下为示例，实际应用中需要替换为真实数据获取逻辑
        if index_code.startswith('H'):
            # 处理港股指数
            # 示例数据，实际应用中需要替换为真实数据获取
            index_name = "恒生指数" if index_code == "HSI" else "未知港股指数"
            hk_data = [GlobalIndexData(open=18500.0, high=18700.0, low=18400.0, close=18650.0, volume=1500000.0)]
            dates = [datetime.now().strftime("%Y-%m-%d")]
            index_detail = transform_hk_index_for_ui(index_code, index_name, hk_data, dates)
        else:
            # 处理A股指数
            # 示例数据，实际应用中需要替换为真实数据获取
            try:
                # 获取A股指数
                index_codes = ["000001.SH"]
                cn_indices = get_index_data(index_codes, trade_date=get_yesterday_yyyymmdd())
            except Exception as e:
                print(f"获取A股指数失败: {str(e)}")
            
            # # 转换为Pydantic模型
            # cn_index_base_data = CNIndexBaseData(**base_info)
            # cn_index_data = CNIndexData(**quote_info)
            
            # # 获取历史K线数据 (示例)
            # history_data = [cn_index_data]  # 实际应用中应该查询真实的历史数据
            
            # index_detail = transform_cn_index_for_ui(cn_index_base_data, history_data)
        
        return IndexResponse(data=cn_indices)
    
    except Exception as e:
        return IndexResponse(code=500, message=f"获取指数详情失败: {str(e)}", data={})

# 极简指数信息处理
def get_minial_market_indices(cn_market_indeices: List[Dict[str, Any]], global_market_indeices: List[GlobalIndexData]) -> IndexResponse:
    """
    """
    try:
        # 格式转换
        result = []
        for cn_market_index in cn_market_indeices:
            ts_code = cn_market_index["ts_code"]
            cn_base_data = cn_market_index["cn_index_base_data"]
            cn_index_data = cn_market_index.get("cn_index_data")
            
            # 转换为极简数据
            minimal_data = {
                "ts_code": ts_code,
                "name": cn_base_data.name,
                "current": cn_index_data.close.item() if len(cn_index_data) > 0 else 0,
                "change": cn_index_data.change.item() if len(cn_index_data) > 0 else 0,
                "pct_chg": cn_index_data.pct_chg.item() if len(cn_index_data) > 0 else 0,
            }
            
            result.append(minimal_data)
        
        for global_market_index in global_market_indeices:
            
            # 转换为极简数据
            minimal_data = {
                "ts_code": global_market_index.ts_code,
                "name": global_market_index.name,
                "current": global_market_index.close if global_market_index else 0,
                "change": global_market_index.change if global_market_index else 0,
                "pct_chg": global_market_index.pct_chg if global_market_index else 0,
            }
            
            result.append(minimal_data)
        
        return IndexResponse(data=result)
    except Exception as e:
        return IndexResponse(code=500, message=f"获取极简市场指数列表失败: {str(e)}", data={cn_market_indeices, global_market_indeices})


def get_index_kline(index_code: str, period: str = "day") -> IndexResponse:
    """
    获取指数K线数据API
    
    Args:
        index_code (str): 指数代码，如 000001 (上证指数)
        period (str): 周期，day/week/month/1m/5m/15m/30m/60m
        
    Returns:
        IndexResponse: API响应
    """
    try:
        # 确定时间范围
        end_date = datetime.now()
        
        if period == "day":
            days = 90  # 近90天日线
        elif period == "week":
            days = 365  # 近1年周线
        elif period == "month":
            days = 730  # 近2年月线
        elif period.endswith('m'):
            # 分钟级别数据，为了演示，都返回近100条
            days = 1
        else:
            days = 90  # 默认90天
            
        start_date = end_date - timedelta(days=days)
        
        # 这里应该是从数据库或外部API获取数据
        # 以下为示例，实际应用中需要替换为真实数据获取逻辑
        kline_data = []
        
        # 生成模拟数据
        current_date = start_date
        base_price = 3200 if index_code == "000001" else 10500  # 初始价格
        
        while current_date <= end_date:
            if period == "week" and current_date.weekday() != 0:  # 只在周一生成数据
                current_date += timedelta(days=1)
                continue
                
            if period == "month" and current_date.day != 1:  # 只在每月1日生成数据
                current_date += timedelta(days=1)
                continue
                
            # 模拟涨跌
            change_pct = (((current_date.day * 17) % 10) - 5) / 100  # 模拟-5%到5%的涨跌
            
            # 调整价格
            close_price = base_price * (1 + change_pct)
            open_price = close_price * (1 - change_pct / 2)
            high_price = close_price * 1.01
            low_price = open_price * 0.99
            
            # 更新基础价格为当前收盘价
            base_price = close_price
            
            # 格式化日期
            date_str = current_date.strftime("%Y-%m-%d")
            
            # 添加K线数据
            kline_data.append({
                "date": date_str,
                "open": round(open_price, 2),
                "close": round(close_price, 2),
                "high": round(high_price, 2),
                "low": round(low_price, 2),
                "volume": round(1000000 + current_date.day * 50000, 0),
                "amount": round(close_price * 1000000 * (1 + current_date.day / 30), 0)
            })
            
            # 根据周期增加日期
            if period == "day" or period.endswith('m'):
                current_date += timedelta(days=1)
            elif period == "week":
                current_date += timedelta(days=7)
            elif period == "month":
                # 增加一个月，简单处理
                if current_date.month == 12:
                    current_date = current_date.replace(year=current_date.year + 1, month=1)
                else:
                    current_date = current_date.replace(month=current_date.month + 1)
        
        # 只保留工作日数据（简化处理）
        if period == "day" or period.endswith('m'):
            kline_data = [data for data in kline_data if 
                         datetime.strptime(data["date"], "%Y-%m-%d").weekday() < 5]
        
        # 排序数据，最新的在前面
        kline_data.sort(key=lambda x: x["date"], reverse=True)
        
        # 分钟级数据特殊处理
        if period.endswith('m'):
            minutes = int(period[:-1])
            today = datetime.now().strftime("%Y-%m-%d")
            minute_data = []
            
            # 生成当天的分钟数据
            for i in range(240 // minutes):  # 假设4小时交易时间
                minute = i * minutes
                hour = 9 + minute // 60
                minute = minute % 60
                
                if hour >= 12:  # 跳过中午休市
                    hour += 1
                
                time_str = f"{today} {hour:02d}:{minute:02d}:00"
                
                # 模拟价格
                change_pct = ((i * 17) % 10 - 5) / 1000  # 更小的波动
                current_price = base_price * (1 + change_pct)
                
                minute_data.append({
                    "date": time_str,
                    "open": round(current_price * 0.999, 2),
                    "close": round(current_price, 2),
                    "high": round(current_price * 1.001, 2),
                    "low": round(current_price * 0.998, 2),
                    "volume": round(10000 + i * 1000, 0),
                    "amount": round(current_price * 10000 * (1 + i / 100), 0)
                })
            
            # 将分钟数据添加到前面
            kline_data = minute_data + kline_data[:5]  # 只保留前几天的日线数据用于参考
        
        return IndexResponse(data=kline_data)
    
    except Exception as e:
        return IndexResponse(code=500, message=f"获取K线数据失败: {str(e)}", data=[])

def get_market_indices() -> IndexResponse:
    """
    获取市场主要指数列表API
    
    Returns:
        IndexResponse: API响应
    """
    try:
        # 这里应该是从数据库或外部API获取数据
        # 以下为示例，实际应用中需要替换为真实数据获取逻辑
        
        # A股主要指数
        cn_indices = [
            {
                "code": "000001",
                "name": "上证指数",
                "current": 3273.76,
                "change": 28.89,
                "change_percent": 0.89
            },
            {
                "code": "399001",
                "name": "深证成指",
                "current": 10624.23,
                "change": 119.87,
                "change_percent": 1.14
            },
            {
                "code": "399006",
                "name": "创业板指",
                "current": 2145.98,
                "change": 32.76,
                "change_percent": 1.55
            },
            {
                "code": "000016",
                "name": "上证50",
                "current": 2865.12,
                "change": 21.34,
                "change_percent": 0.75
            }
        ]
        
        # 全球主要指数
        global_indices = [
            {
                "code": "DJI",
                "name": "道琼斯",
                "current": 34721.89,
                "change": 165.32,
                "change_percent": 0.48
            },
            {
                "code": "IXIC",
                "name": "纳斯达克",
                "current": 14356.78,
                "change": 87.21,
                "change_percent": 0.61
            },
            {
                "code": "HSI",
                "name": "恒生指数",
                "current": 18598.65,
                "change": -32.45,
                "change_percent": -0.17
            },
            {
                "code": "N225",
                "name": "日经225",
                "current": 28965.34,
                "change": 178.90,
                "change_percent": 0.62
            }
        ]
        
        return IndexResponse(data={"cn_indices": cn_indices, "global_indices": global_indices})
    
    except Exception as e:
        return IndexResponse(code=500, message=f"获取市场指数列表失败: {str(e)}", data={"cn_indices": [], "global_indices": []})

def get_stock_indicators(stock_code: str, period: str, indicators: List[str]) -> IndexResponse:
    """
    获取股票技术指标数据API
    
    Args:
        stock_code (str): 股票代码
        period (str): 周期
        indicators (List[str]): 指标列表
        
    Returns:
        IndexResponse: API响应
    """
    try:
        # 先获取K线数据
        kline_response = get_index_kline(stock_code, period)
        kline_data = kline_response.data
        
        # 计算指标
        indicator_data = {}
        
        for indicator in indicators:
            if indicator == "MACD":
                # 简化的MACD计算
                indicator_data["MACD"] = calculate_mock_macd(kline_data)
            elif indicator == "KDJ":
                # 简化的KDJ计算
                indicator_data["KDJ"] = calculate_mock_kdj(kline_data)
            elif indicator == "RSI":
                # 简化的RSI计算
                indicator_data["RSI"] = calculate_mock_rsi(kline_data)
            elif indicator == "BOLL":
                # 简化的BOLL计算
                indicator_data["BOLL"] = calculate_mock_boll(kline_data)
            elif indicator == "MA":
                # 简化的MA计算
                indicator_data["MA"] = calculate_mock_ma(kline_data)
            elif indicator == "VOL":
                # 简化的VOL计算
                indicator_data["VOL"] = calculate_mock_vol(kline_data)
            elif indicator == "EMA":
                # 简化的EMA计算
                indicator_data["EMA"] = calculate_mock_ema(kline_data)
        
        return IndexResponse(data=indicator_data)
    
    except Exception as e:
        return IndexResponse(code=500, message=f"获取技术指标数据失败: {str(e)}", data={})

# 模拟指标计算函数
# 混合计算策略：计算一次并存储，以便于大量的历史数据分析；对于近期（3个月内）的数据，实时计算或使用定时任务
# 如：用户首次请求时计算并缓存（懒加载）
# 改用TAB-Lib计算
def calculate_mock_macd(kline_data: List[Dict]) -> Dict:
    """计算MACD指标（模拟数据）"""
    dif = []
    dea = []
    macd = []
    hist = []
    
    for i, item in enumerate(kline_data):
        date = item["date"]
        close = item["close"]
        
        # 简化的计算逻辑
        dif_value = close * (0.9 + 0.2 * (i % 10) / 10)
        dea_value = dif_value * (0.95 + 0.1 * (i % 5) / 10)
        macd_value = (dif_value - dea_value) * 2
        
        dif.append([date, round(dif_value, 2)])
        dea.append([date, round(dea_value, 2)])
        macd.append([date, round(macd_value, 2)])
        hist.append([date, round(macd_value, 2)])
    
    return {
        "DIF": dif,
        "DEA": dea,
        "MACD": macd,
        "HIST": hist
    }

def calculate_mock_kdj(kline_data: List[Dict]) -> Dict:
    """计算KDJ指标（模拟数据）"""
    k = []
    d = []
    j = []
    
    for i, item in enumerate(kline_data):
        date = item["date"]
        
        # 模拟计算
        k_value = 50 + (i % 20) * 2 - 20
        d_value = k_value * (0.95 + 0.1 * (i % 5) / 10)
        j_value = 3 * k_value - 2 * d_value
        
        k.append([date, round(k_value, 2)])
        d.append([date, round(d_value, 2)])
        j.append([date, round(j_value, 2)])
    
    return {
        "K": k,
        "D": d,
        "J": j
    }

def calculate_mock_rsi(kline_data: List[Dict]) -> Dict:
    """计算RSI指标（模拟数据）"""
    rsi6 = []
    rsi12 = []
    rsi24 = []
    
    for i, item in enumerate(kline_data):
        date = item["date"]
        
        # 模拟计算
        rsi6_value = 40 + (i % 30) * 2 - 15 # 模拟范围30-75
        rsi12_value = 35 + (i % 25) * 2 - 10 # 模拟范围35-65
        rsi24_value = 30 + (i % 20) * 2 - 5  # 模拟范围30-55
        
        rsi6.append([date, round(rsi6_value, 2)])
        rsi12.append([date, round(rsi12_value, 2)])
        rsi24.append([date, round(rsi24_value, 2)])
    
    return {
        "RSI6": rsi6,
        "RSI12": rsi12,
        "RSI24": rsi24
    }

def calculate_mock_boll(kline_data: List[Dict]) -> Dict:
    """计算BOLL指标（模拟数据）"""
    upper = []
    mid = []
    lower = []
    
    for i, item in enumerate(kline_data):
        date = item["date"]
        close = item["close"]
        
        # 模拟计算
        mid_value = close * (0.99 + 0.02 * (i % 10) / 10)
        upper_value = mid_value * (1.02 + 0.01 * (i % 10) / 10)
        lower_value = mid_value * (0.98 - 0.01 * (i % 10) / 10)
        
        upper.append([date, round(upper_value, 2)])
        mid.append([date, round(mid_value, 2)])
        lower.append([date, round(lower_value, 2)])
    
    return {
        "UPPER": upper,
        "MID": mid,
        "LOWER": lower
    }

def calculate_mock_ma(kline_data: List[Dict]) -> Dict:
    """计算MA指标（模拟数据）"""
    ma5 = []
    ma10 = []
    ma20 = []
    
    for i, item in enumerate(kline_data):
        date = item["date"]
        close = item["close"]
        
        # 模拟计算
        ma5_value = close * (0.98 + 0.04 * (i % 5) / 10)
        ma10_value = close * (0.96 + 0.06 * (i % 10) / 20)
        ma20_value = close * (0.94 + 0.08 * (i % 20) / 30)
        
        ma5.append([date, round(ma5_value, 2)])
        ma10.append([date, round(ma10_value, 2)])
        ma20.append([date, round(ma20_value, 2)])
    
    return {
        "MA5": ma5,
        "MA10": ma10,
        "MA20": ma20
    }

def calculate_mock_vol(kline_data: List[Dict]) -> Dict:
    """计算成交量指标（模拟数据）"""
    vol_ma5 = []
    vol_ma10 = []
    
    for i, item in enumerate(kline_data):
        date = item["date"]
        volume = item["volume"]
        
        # 模拟计算
        ma5_value = volume * (0.9 + 0.2 * (i % 5) / 10)
        ma10_value = volume * (0.85 + 0.25 * (i % 10) / 20)
        
        vol_ma5.append([date, round(ma5_value, 0)])
        vol_ma10.append([date, round(ma10_value, 0)])
    
    return {
        "MA5": vol_ma5,
        "MA10": vol_ma10
    }

def calculate_mock_ema(kline_data: List[Dict]) -> Dict:
    """计算EMA指标（模拟数据）"""
    ema5 = []
    ema10 = []
    ema20 = []
    
    for i, item in enumerate(kline_data):
        date = item["date"]
        close = item["close"]
        
        # 模拟计算
        ema5_value = close * (0.97 + 0.05 * (i % 5) / 10)
        ema10_value = close * (0.95 + 0.07 * (i % 10) / 20)
        ema20_value = close * (0.93 + 0.09 * (i % 20) / 30)
        
        ema5.append([date, round(ema5_value, 2)])
        ema10.append([date, round(ema10_value, 2)])
        ema20.append([date, round(ema20_value, 2)])
    
    return {
        "EMA5": ema5,
        "EMA10": ema10,
        "EMA20": ema20
    }

# 快速API接口示例（FastAPI）

"""
如果使用FastAPI实现，代码大致如下：

from fastapi import FastAPI, Path, Query

app = FastAPI()

@app.get("/api/market/indices")
async def api_market_indices():
    response = get_market_indices()
    return response.dict()

@app.get("/api/index/{index_code}")
async def api_index_detail(
    index_code: str = Path(..., description="指数代码")
):
    response = get_index_detail(index_code)
    return response.dict()

@app.get("/api/index/{index_code}/kline")
async def api_index_kline(
    index_code: str = Path(..., description="指数代码"),
    period: str = Query("day", description="K线周期，day/week/month/1m/5m/15m/30m/60m")
):
    response = get_index_kline(index_code, period)
    return response.dict()

@app.get("/api/stock/{stock_code}/indicators")
async def api_stock_indicators(
    stock_code: str = Path(..., description="股票代码"),
    period: str = Query("day", description="K线周期"),
    indicators: str = Query(..., description="指标列表，逗号分隔")
):
    indicator_list = indicators.split(",")
    response = get_stock_indicators(stock_code, period, indicator_list)
    return response.dict()
"""

# 示例使用
if __name__ == "__main__":
    # 测试指数数据转换
    index_detail = get_index_detail("000001")
    print(json.dumps(index_detail.dict(), indent=2))
    
    # # 测试K线数据
    # kline_data = get_index_kline("000001", "day")
    # print(f"获取到{len(kline_data.data)}条K线数据")
    
    # # 测试技术指标
    # indicators = get_stock_indicators("000001", "day", ["MACD", "KDJ"])
    # print(f"计算了{len(indicators.data)}个技术指标")
    
    # # 测试市场指数列表
    # market_indices = get_market_indices()
    # print(f"获取到{len(market_indices.data['cn_indices'])}个A股指数和{len(market_indices.data['global_indices'])}个全球指数")