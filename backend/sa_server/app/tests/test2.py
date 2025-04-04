import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time
from datetime import datetime, timedelta
import random

# 设置页面配置
st.set_page_config(
    page_title="股票多维度分析系统",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 添加CSS样式
st.markdown("""
<style>
    .analyst-container {
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
    }
    .macro-analyst {
        background-color: rgba(100, 149, 237, 0.2);
        border-left: 5px solid cornflowerblue;
    }
    .technical-analyst {
        background-color: rgba(60, 179, 113, 0.2);
        border-left: 5px solid mediumseagreen;
    }
    .fundamental-analyst {
        background-color: rgba(255, 165, 0, 0.2);
        border-left: 5px solid orange;
    }
    .analyst-header {
        display: flex;
        align-items: center;
        margin-bottom: 10px;
    }
    .analyst-avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        margin-right: 10px;
    }
    .analyst-name {
        font-weight: bold;
        margin: 0;
    }
    .analyst-title {
        color: gray;
        font-size: 0.8em;
        margin: 0;
    }
    .message-time {
        color: gray;
        font-size: 0.7em;
        margin-left: auto;
    }
    .loading-dots {
        display: inline-block;
    }
    .last-update {
        font-size: 0.8em;
        color: gray;
        font-style: italic;
    }
</style>
""", unsafe_allow_html=True)

# 模拟数据生成函数
def generate_stock_data(ticker, days=180):
    np.random.seed(42)  # 保证可重复性
    date_today = datetime.now()
    dates = [date_today - timedelta(days=i) for i in range(days)]
    dates.reverse()
    
    # 生成价格数据
    base_price = 100
    if ticker == "AAPL":
        base_price = 170
    elif ticker == "TSLA":
        base_price = 200
    elif ticker == "NVDA":
        base_price = 750
    
    price = [base_price]
    for i in range(1, days):
        change = np.random.normal(0, 1) * base_price * 0.01
        # 加入一些趋势
        if ticker == "AAPL" and i > days - 30:
            change += 0.2  # 最近上涨
        elif ticker == "TSLA" and i > days - 40:
            change -= 0.15  # 最近下跌
        new_price = max(price[-1] + change, base_price * 0.5)  # 确保价格不会太低
        price.append(new_price)
    
    # 生成交易量
    volume = [int(np.random.normal(1000000, 200000)) for _ in range(days)]
    
    # 创建DataFrame
    df = pd.DataFrame({
        'Date': dates,
        'Price': price,
        'Volume': volume
    })
    return df

# 模拟宏观经济数据
def generate_macro_data():
    macro_indicators = {
        "GDP增长率": "2.5%",
        "CPI同比": "3.1%",
        "失业率": "3.8%",
        "美联储基准利率": "4.75%-5.00%",
        "10年期国债收益率": "4.32%",
        "市场恐慌指数(VIX)": "18.7"
    }
    
    # 趋势描述
    trends = {
        "GDP趋势": "GDP增长率较上季度小幅回升，但仍低于历史平均水平。消费支出增长3.2%，成为主要驱动因素。",
        "通胀趋势": "CPI同比增速连续三个月放缓，核心CPI已从高点回落。能源价格同比下降2.1%，食品价格上涨3.3%。",
        "就业趋势": "就业市场保持韧性，失业率近六个月维持在3.7%-3.9%区间。非农就业人数增速放缓但仍为正。",
        "利率环境": "美联储暗示接近加息周期尾声，市场预期未来6-12个月可能开启降息。短期利率曲线倒挂状态有所缓解。"
    }
    
    # 最新政策动向
    policies = [
        "财政部宣布新的减税计划，预计将为企业减负约2000亿美元",
        "美联储主席在最新讲话中强调，将密切关注通胀数据决定未来利率路径",
        "欧盟推出新的碳关税机制，可能影响全球贸易格局",
        "多国央行继续增加黄金储备，黄金需求上升"
    ]
    
    return macro_indicators, trends, policies

# 模拟宏观分析师回复
def macro_analysis(ticker):
    time.sleep(1)  # 模拟分析延迟
    
    # 获取模拟数据
    macro_indicators, trends, policies = generate_macro_data()
    
    # 股票特定分析
    if ticker == "AAPL":
        analysis = """
基于当前宏观经济环境，对苹果(AAPL)的影响评估如下：

**有利因素：**
1. 通胀压力逐步缓解，有利于消费者信心恢复，提升高端消费电子产品需求
2. 就业市场稳定，支持消费者购买力
3. 美联储加息周期接近尾声，可能降低融资成本

**不利因素：**
1. GDP增长低于历史平均水平，消费动能仍有限
2. 地缘政治紧张局势可能影响全球供应链
3. 利率仍处高位，抑制部分消费意愿

**行业政策影响：**
近期科技行业监管趋严，但主要集中在大数据和平台经济领域，对苹果硬件业务影响有限。碳关税机制可能增加跨境生产成本。

**总体判断：**
宏观环境对苹果呈中性略偏正面影响。利率见顶预期将支持估值修复，但经济增长乏力仍将制约业绩大幅增长。建议关注消费数据变化和供应链稳定性。
"""
    
    elif ticker == "TSLA":
        analysis = """
特斯拉(TSLA)在当前宏观环境下的处境分析：

**有利因素：**
1. 绿色能源政策支持，多国电动车补贴政策延续
2. 通胀见顶，原材料成本压力有望缓解
3. 碳关税机制有利于在环保标准高的地区生产的车企

**不利因素：**
1. 高利率环境增加消费者购车融资成本
2. 经济增长放缓可能影响高价位商品销售
3. 地缘政治紧张影响全球供应链和关键原材料供应

**关键宏观指标影响：**
利率环境对特斯拉影响显著——高利率直接影响汽车金融租赁成本，且压制高增长股票估值。美联储政策转向信号将是重要观察点。

**总体判断：**
宏观环境对特斯拉呈中性略偏负面影响。短期内高利率仍将压制需求和估值，但中长期绿色能源转型趋势未变。建议密切关注美联储政策变化和全球新能源补贴政策调整。
"""
    
    elif ticker == "NVDA":
        analysis = """
英伟达(NVDA)在当前宏观格局中的定位分析：

**有利因素：**
1. AI浪潮持续，大型科技公司资本支出计划维持高位
2. 科技创新政策支持，多国推动半导体产业本土化
3. 通胀缓解，缓解部分成本压力

**不利因素：**
1. 高利率环境对高估值科技股形成估值压制
2. 地缘政治紧张导致的半导体出口管制风险增加
3. 若经济衰退，部分企业可能延缓技术升级投资

**特殊宏观因素：**
半导体产业已成为地缘政治博弈焦点，各国产业政策变化将直接影响英伟达的市场准入和竞争格局。当前的供应紧张局面在政策影响下可能持续。

**总体判断：**
宏观环境对英伟达整体呈正面影响。尽管高利率环境对估值有压制，但产业政策支持和AI需求强劲足以抵消这一影响。建议关注地缘政治风险和美联储政策转向时点。
"""
    
    else:
        analysis = f"""
{ticker}在当前宏观环境下的分析：

基于当前宏观经济指标，整体经济增长略显疲软但保持韧性。通胀压力正在缓解，但利率仍处于相对高位。

对{ticker}的主要影响来自：
1. 当前的高利率环境可能抑制公司扩张和投资计划
2. 消费者支出谨慎，可能影响需求
3. 全球贸易政策变化可能影响供应链和成本结构

需要进一步了解{ticker}所在行业的具体情况以提供更精确的宏观影响分析。
"""
    
    # 返回完整分析结果
    return analysis, macro_indicators, trends, policies

# 模拟技术分析师回复
def technical_analysis(ticker):
    time.sleep(1.5)  # 模拟分析延迟
    
    # 获取股票数据
    df = generate_stock_data(ticker)
    
    # 计算一些技术指标
    df['SMA20'] = df['Price'].rolling(window=20).mean()
    df['SMA50'] = df['Price'].rolling(window=50).mean()
    df['RSI'] = 50 + np.random.normal(0, 10, len(df))  # 简化的RSI计算
    df['RSI'] = df['RSI'].clip(0, 100)  # 确保RSI在0-100之间
    
    # 最近的数据
    recent_data = df.iloc[-1]
    current_price = recent_data['Price']
    
    # 计算支撑位和阻力位 (简化模拟)
    support = current_price * 0.95
    resistance = current_price * 1.05
    
    # 股票特定分析
    if ticker == "AAPL":
        analysis = f"""
苹果(AAPL)技术面分析：

**价格走势：**
当前价格 ${current_price:.2f}，处于上升通道中。近期突破了${resistance-10:.2f}关键阻力位，显示出较强的上涨动能。

**关键技术指标：**
- RSI: {df['RSI'].iloc[-1]:.1f}，处于轻微超买区域但未达极值
- 20日均线(${df['SMA20'].iloc[-1]:.2f})向上穿越50日均线(${df['SMA50'].iloc[-1]:.2f})，形成黄金交叉
- 成交量温和放大，确认价格上涨有效性

**支撑与阻力：**
- 主要支撑位：${support:.2f}和${support-5:.2f}
- 主要阻力位：${resistance:.2f}和${resistance+5:.2f}

**形态识别：**
价格形成一个上升三角形形态，通常是看涨信号。近期的突破增强了这一看法。

**波动性分析：**
波动率低于历史平均水平，表明市场对苹果股价走向较为确定。

**总体技术面判断：**
短期内看涨，中期趋势强劲。可能会在${resistance:.2f}处遇到一定阻力，但整体技术面支持价格继续上行。建议关注${support:.2f}支撑位是否有效。
"""
    
    elif ticker == "TSLA":
        analysis = f"""
特斯拉(TSLA)技术面分析：

**价格走势：**
当前价格 ${current_price:.2f}，处于下降通道中。价格跌破了${current_price+15:.2f}重要支撑位，转化为阻力位。

**关键技术指标：**
- RSI: {df['RSI'].iloc[-1]:.1f}，处于超卖区域，存在反弹可能
- 20日均线(${df['SMA20'].iloc[-1]:.2f})位于50日均线(${df['SMA50'].iloc[-1]:.2f})下方，维持空头排列
- 成交量在下跌过程中逐渐增加，表明抛压较大

**支撑与阻力：**
- 主要支撑位：${support:.2f}和${support-10:.2f}
- 主要阻力位：${resistance:.2f}和${current_price+15:.2f}

**形态识别：**
价格可能正在形成头肩顶形态，如果颈线位被确认突破，可能引发进一步下跌。

**波动性分析：**
波动率高于历史平均水平，表明市场情绪不稳定，价格波动风险较大。

**总体技术面判断：**
短期内偏空，但已接近超卖，存在技术性反弹可能。中期趋势仍然偏弱，建议等待${support:.2f}支撑位确认后再考虑入场。关注成交量变化和RSI背离可能。
"""
    
    elif ticker == "NVDA":
        analysis = f"""
英伟达(NVDA)技术面分析：

**价格走势：**
当前价格 ${current_price:.2f}，处于强劲上升趋势中。价格远高于各周期均线，显示出极强的动能。

**关键技术指标：**
- RSI: {df['RSI'].iloc[-1]:.1f}，处于明显超买区域，但强势股往往能维持超买状态较长时间
- 20日均线(${df['SMA20'].iloc[-1]:.2f})和50日均线(${df['SMA50'].iloc[-1]:.2f})都呈现上升趋势，多头排列明显
- 成交量持续放大，表明大资金持续流入

**支撑与阻力：**
- 主要支撑位：${support:.2f}和${df['SMA20'].iloc[-1]:.2f}(20日均线)
- 主要阻力位：${resistance:.2f}(心理关口)

**形态识别：**
股价呈抛物线上升形态，表明市场情绪非常乐观，但也存在短期回调风险。

**波动性分析：**
波动率持续上升，表明价格波动幅度扩大，可能预示着转折点临近。

**总体技术面判断：**
短期超买严重，存在回调风险，但中长期上升趋势强劲。建议逢回调布局，关注${df['SMA20'].iloc[-1]:.2f}(20日均线)支撑情况。极端上涨后通常伴随剧烈回调，注意风险控制。
"""
    
    else:
        analysis = f"""
{ticker}技术面分析：

**价格走势：**
当前价格 ${current_price:.2f}，位于20日均线(${df['SMA20'].iloc[-1]:.2f})和50日均线(${df['SMA50'].iloc[-1]:.2f})之间，处于盘整状态。

**关键技术指标：**
- RSI: {df['RSI'].iloc[-1]:.1f}，处于中性区域
- 均线系统呈现交织状态，暂无明确方向
- 成交量近期萎缩，表明交投清淡

**支撑与阻力：**
- 主要支撑位：${support:.2f}
- 主要阻力位：${resistance:.2f}

**形态识别：**
价格形成箱体震荡形态，等待方向性突破。

**总体技术面判断：**
暂无明确方向，建议等待价格突破确认后再行动。需要进一步观察成交量变化以确认突破有效性。
"""
    
    return analysis, df

# 模拟基本面分析师回复
def fundamental_analysis(ticker):
    time.sleep(2)  # 模拟分析延迟
    
    # 模拟财务数据
    if ticker == "AAPL":
        financials = {
            "市值": "2.95万亿美元",
            "PE": "32.4",
            "预期PE": "28.7",
            "PEG": "2.1",
            "股息率": "0.5%",
            "毛利率": "44.3%",
            "净利率": "25.2%",
            "ROE": "147.9%",
            "负债/资产": "79.8%"
        }
        
        analysis = """
苹果(AAPL)基本面分析：

**业务概览：**
苹果主要收入来源仍是iPhone(约52%)，但服务业务(约23%)增长迅速，成为新的增长引擎。可穿戴设备、家居和配件类增速显著，Mac和iPad相对稳定。

**财务健康度：**
- 现金储备充足，约610亿美元净现金
- 持续的股票回购计划支持EPS增长
- 自由现金流充沛，同比增长7.8%
- 股息虽然率低但持续增长，连续9年上调

**增长前景：**
- iPhone 15系列销售良好，但增速已放缓
- 服务业务毛利率高达70%以上，对整体利润贡献显著
- AI集成可能为下一代产品带来增长契机
- 印度等新兴市场持续渗透，但面临本土竞争

**风险因素：**
- 产品更新周期拉长，创新感知下降
- 服务业务面临监管审查
- 地缘政治摩擦影响供应链和中国市场

**估值分析：**
当前PE(32.4)高于5年平均水平(26.8)，但考虑到服务业务占比提升带来的利润结构优化，一定溢价是合理的。与大型科技公司相比估值适中。

**总体基本面判断：**
基本面稳健，增长放缓但质量提升。短期内可能面临估值压力，但长期投资价值突出。建议关注服务业务增速和毛利率变化作为关键指标。
"""
    
    elif ticker == "TSLA":
        financials = {
            "市值": "6355亿美元",
            "PE": "54.2",
            "预期PE": "47.3",
            "PEG": "2.5",
            "股息率": "N/A",
            "毛利率": "18.2%",
            "净利率": "10.8%",
            "ROE": "23.7%",
            "负债/资产": "25.4%"
        }
        
        analysis = """
特斯拉(TSLA)基本面分析：

**业务概览：**
特斯拉主要收入来自电动车销售(约85%)，能源业务和服务占比提升。产品线包括Model S/X/3/Y/Cybertruck，在全球拥有多个超级工厂。

**财务健康度：**
- 现金储备约233亿美元，债务相对较低
- 毛利率持续下滑，从25%以上降至18%左右
- 自由现金流有所下降，受产能投资和价格调整影响
- 无股息分配，资本优先用于扩张

**增长前景：**
- 全球电动车渗透率持续提升，但竞争加剧
- Cybertruck已开始交付，但量产挑战大
- FSD(全自动驾驶)技术进展将是关键增长点
- 能源存储业务增速快，但体量仍小

**风险因素：**
- 竞争加剧导致价格战和毛利率下滑
- CEO注意力分散问题
- 电动车补贴政策变化
- 自动驾驶技术进展不及预期

**估值分析：**
当前PE(54.2)显著高于传统汽车企业，但低于历史峰值。估值仍包含对自动驾驶和机器人等领域突破的预期。考虑增长放缓，当前估值偏高。

**总体基本面判断：**
基本面处于转型期，从高速增长转向更可持续的增长模式。短期盈利能力承压，但长期成长性仍然可观。投资者需关注毛利率企稳信号和FSD进展。建议等待估值调整或技术突破后再考虑建仓。
"""
    
    elif ticker == "NVDA":
        financials = {
            "市值": "2.31万亿美元",
            "PE": "72.6",
            "预期PE": "39.8",
            "PEG": "1.3",
            "股息率": "0.03%",
            "毛利率": "70.1%",
            "净利率": "56.5%",
            "ROE": "98.7%",
            "负债/资产": "19.6%"
        }
        
        analysis = """
英伟达(NVDA)基本面分析：

**业务概览：**
英伟达已从游戏GPU厂商转型为AI计算领导者。数据中心业务(70%以上)超越游戏业务成为最大收入来源，专业可视化和汽车业务占比较小但增长潜力大。

**财务健康度：**
- 现金储备充足，约230亿美元，几乎无负债
- 毛利率极高(70%+)，创历史新高
- 净利率(56%+)表现惊人，显示极强的盈利能力
- 营收和利润增速超过100%，处于爆发式增长阶段

**增长前景：**
- AI芯片需求旺盛，H100/H200供不应求，已有排期到2025年
- 新一代Blackwell架构即将推出，性能大幅提升
- 云计算和大型科技公司持续加大AI基础设施投入
- 软件生态(CUDA)形成护城河，强化硬件销售

**风险因素：**
- 估值已处历史高位，市场预期极高
- 竞争对手(AMD、Intel、各创业公司)追赶
- 客户集中度高，前五大客户占比超40%
- 地缘政治导致的出口管制风险

**估值分析：**
当前PE(72.6)虽高，但考虑到增速，PEG仅1.3，相对合理。预期PE(39.8)已反映市场对高增长的预期。与历史和行业相比，虽不便宜但有业绩支撑。

**总体基本面判断：**
基本面极为强劲，处于难得的供不应求和高毛利率并存阶段。短期来看，业绩支撑估值；中长期仍有巨大成长空间。主要风险在于市场预期过高和竞争格局变化。建议重点关注供需平衡变化时点和竞争对手技术突破情况。
"""
    
    else:
        financials = {
            "市值": "待获取",
            "PE": "待获取",
            "预期PE": "待获取",
            "股息率": "待获取",
            "毛利率": "待获取",
            "净利率": "待获取",
            "ROE": "待获取"
        }
        
        analysis = f"""
{ticker}基本面分析：

需要获取更多该公司的财务数据和业务信息才能提供详细分析。

一般而言，基本面分析需要考察以下方面：
1. 业务模式和收入来源
2. 财务状况和盈利能力
3. 增长前景和行业地位
4. 管理团队和公司治理
5. 风险因素评估

建议查询最新的财务报表、盈利电话会议内容和分析师报告，以获取全面的基本面信息。
"""
    
    # 行业对比数据
    if ticker in ["AAPL", "TSLA", "NVDA"]:
        peer_comparison = {
            "AAPL": {"PE": 32.4, "增长率": 8.1, "毛利率": 44.3},
            "MSFT": {"PE": 37.1, "增长率": 13.2, "毛利率": 69.7},
            "GOOGL": {"PE": 25.2, "增长率": 15.6, "毛利率": 55.3},
            "AMZN": {"PE": 42.1, "增长率": 11.3, "毛利率": 46.8},
            "META": {"PE": 30.3, "增长率": 19.2, "毛利率": 54.1}
        } if ticker == "AAPL" else {
            "TSLA": {"PE": 54.2, "增长率": 15.3, "毛利率": 18.2},
            "GM": {"PE": 5.3, "增长率": 4.1, "毛利率": 13.5},
            "F": {"PE": 7.2, "增长率": 2.7, "毛利率": 10.8},
            "TM": {"PE": 10.6, "增长率": 6.2, "毛利率": 16.3},
            "RIVN": {"PE": "N/A", "增长率": 85.3, "毛利率": "-"}
        } if ticker == "TSLA" else {
            "NVDA": {"PE": 72.6, "增长率": 125.5, "毛利率": 70.1},
            "AMD": {"PE": 44.3, "增长率": 33.2, "毛利率": 47.6},
            "INTC": {"PE": 31.2, "增长率": -0.5, "毛利率": 38.7},
            "TSM": {"PE": 29.8, "增长率": 24.1, "毛利率": 52.3},
            "AVGO": {"PE": 52.6, "增长率": 38.3, "毛利率": 74.5}
        }
    else:
        peer_comparison = {}
    
    return analysis, financials, peer_comparison

# 模拟用户查询处理
def process_query(ticker, query):
    """处理用户查询并整合三位分析师的回应"""
    responses = []
    
    # 调用宏观分析师
    macro_result, macro_indicators, macro_trends, macro_policies = macro_analysis(ticker)
    responses.append(("macro", macro_result))
    
    # 调用技术分析师
    technical_result, stock_data = technical_analysis(ticker)
    responses.append(("technical", technical_result))
    
    # 调用基本面分析师
    fundamental_result, financials, peer_comparison = fundamental_analysis(ticker)
    responses.append(("fundamental", fundamental_result))
    
    return responses, macro_indicators, macro_trends, macro_policies, stock_data, financials, peer_comparison

# 创建股票选择器和主应用
def main():
    # 侧边栏设置
    st.sidebar.title("股票多维度分析系统")
    
    # 股票选择
    ticker_options = {
        "AAPL": "苹果 (AAPL)",
        "TSLA": "特斯拉 (TSLA)",
        "NVDA": "英伟达 (NVDA)",
        "OTHER": "其他股票"
    }
    
    selected_ticker = st.sidebar.selectbox(
        "选择股票",
        list(ticker_options.keys()),
        format_func=lambda x: ticker_options[x]
    )
    
    if selected_ticker == "OTHER":
        custom_ticker = st.sidebar.text_input("输入股票代码")
        if custom_ticker:
            selected_ticker = custom_ticker
        else:
            selected_ticker = "AAPL"  # 默认值
    
    # 用户查询输入
    st.sidebar.subheader("分析师咨询")
    user_query = st.sidebar.text_area("输入您的问题（可选）", 
                                      placeholder="例如：这支股票受最近利率变化的影响如何？")
    
    # 分析师选择
    st.sidebar.subheader("选择分析师")
    show_macro = st.sidebar.checkbox("宏观分析师", value=True)
    show_technical = st.sidebar.checkbox("技术分析师", value=True)
    show_fundamental = st.sidebar.checkbox("基本面分析师", value=True)
    
    # 更新时间设置
    last_update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.sidebar.markdown(f"<p class='last-update'>最后更新: {last_update_time}</p>", unsafe_allow_html=True)
    
    # 处理刷新按钮
    if st.sidebar.button("刷新分析"):
        st.experimental_rerun()
    
    # 主页面
    st.title(f"{ticker_options.get(selected_ticker, selected_ticker)} 多维度分析")
    
    # 处理用户查询
    responses, macro_indicators, macro_trends, macro_policies, stock_data, financials, peer_comparison = process_query(selected_ticker, user_query)
    
    # 股票图表展示
    st.subheader("股票价格走势")
    
    # 绘制股票价格图表
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(stock_data['Date'], stock_data['Price'], label='价格')
    ax.plot(stock_data['Date'], stock_data['SMA20'], label='20日均线', linestyle='--', alpha=0.7)
    ax.plot(stock_data['Date'], stock_data['SMA50'], label='50日均线', linestyle='-.', alpha=0.7)
    
    # 设置图表格式
    ax.set_xlabel('日期')
    ax.set_ylabel('价格 ($)')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 格式化x轴日期
    from matplotlib.dates import DateFormatter
    date_format = DateFormatter('%m-%d')
    ax.xaxis.set_major_formatter(date_format)
    fig.autofmt_xdate()
    
    st.pyplot(fig)
    
    # 创建三列布局
    col1, col2, col3 = st.columns([2, 1, 1])
    
    # 宏观数据展示
    with col1:
        st.subheader("宏观经济指标")
        macro_df = pd.DataFrame(list(macro_indicators.items()), columns=['指标', '数值'])
        st.dataframe(macro_df, hide_index=True)
    
    # 基本面数据展示
    with col2:
        st.subheader("公司财务指标")
        finance_df = pd.DataFrame(list(financials.items()), columns=['指标', '数值'])
        st.dataframe(finance_df, hide_index=True)
    
    # 技术指标展示
    with col3:
        st.subheader("技术指标")
        recent = stock_data.iloc[-1]
        tech_indicators = {
            "当前价格": f"${recent['Price']:.2f}",
            "20日均线": f"${recent['SMA20']:.2f}",
            "50日均线": f"${recent['SMA50']:.2f}",
            "RSI(14)": f"{recent['RSI']:.1f}",
            "成交量": f"{recent['Volume']:,}"
        }
        tech_df = pd.DataFrame(list(tech_indicators.items()), columns=['指标', '数值'])
        st.dataframe(tech_df, hide_index=True)
    
    # 分析师讨论区
    st.subheader("分析师讨论")
    
    # 如果有自定义查询，显示它
    if user_query:
        st.markdown(f"**您的问题:** {user_query}")
    
    # 定义分析师信息
    analysts = {
        "macro": {
            "name": "李宏观",
            "title": "宏观经济分析师",
            "avatar": "💼",
            "class": "macro-analyst"
        },
        "technical": {
            "name": "张技术",
            "title": "技术分析师",
            "avatar": "📊",
            "class": "technical-analyst"
        },
        "fundamental": {
            "name": "王基本",
            "title": "基本面分析师",
            "avatar": "📝",
            "class": "fundamental-analyst"
        }
    }
    
    # 展示分析师回应
    for analyst_type, content in responses:
        # 检查是否显示该分析师
        if (analyst_type == "macro" and not show_macro) or \
           (analyst_type == "technical" and not show_technical) or \
           (analyst_type == "fundamental" and not show_fundamental):
            continue
            
        analyst = analysts[analyst_type]
        current_time = datetime.now().strftime("%H:%M")
        
        st.markdown(f"""
        <div class="analyst-container {analyst['class']}">
            <div class="analyst-header">
                <div class="analyst-avatar">{analyst['avatar']}</div>
                <div>
                    <p class="analyst-name">{analyst['name']}</p>
                    <p class="analyst-title">{analyst['title']}</p>
                </div>
                <span class="message-time">{current_time}</span>
            </div>
            <div>{content}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # 行业对比展示（如果有）
    if peer_comparison and show_fundamental:
        st.subheader("行业对比")
        peer_df = pd.DataFrame.from_dict(peer_comparison, orient='index')
        
        # 绘制行业对比图表
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # 获取PE和增长率数据（过滤掉非数值）
        valid_pes = {k: v['PE'] for k, v in peer_comparison.items() if isinstance(v['PE'], (int, float))}
        
        companies = list(valid_pes.keys())
        pes = list(valid_pes.values())
        
        # 绘制条形图
        bars = ax.bar(companies, pes, color=['#ff9999' if company == selected_ticker else '#9999ff' for company in companies])
        
        ax.set_title('行业PE对比')
        ax.set_ylabel('市盈率 (PE)')
        ax.grid(axis='y', alpha=0.3)
        
        # 突出显示所选公司
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}', ha='center', va='bottom')
        
        st.pyplot(fig)
    
    # 最近宏观政策动向
    if show_macro:
        st.subheader("最新政策动向")
        for i, policy in enumerate(macro_policies):
            st.markdown(f"- {policy}")

# 运行应用
if __name__ == "__main__":
    main()