import warnings
import numpy as np
import pandas as pd
from app.external.tushare_client import get_tushare_client


warnings.filterwarnings('ignore')

class CapitalFlowAnalyzer:
    def __init__(self):
        self.pro = get_tushare_client()
        # 使用历史日期，避免使用未来日期导致数据为空
        self.end_date = '20230331'  # 可调整为需要的结束日期
        self.start_date = '20220401'  # 默认分析一年数据
        
        # 存储各类数据
        self.hsgt_flow = None  # 沪深港通资金流向
        self.ggt_daily = None  # 港股通每日成交
        self.foreign_hold = None  # 外资持股
        self.margin_data = None  # 融资融券数据(作为本地资金参考)
        self.index_data = {}   # 指数数据
    
    def fetch_all_data(self):
        """获取所有相关数据"""
        print(f"分析日期范围: {self.start_date} 至 {self.end_date}")
        self._fetch_hsgt_flow()
        self._fetch_ggt_daily()
        self._fetch_foreign_investment()
        self._fetch_margin_data()
        self._fetch_index_data()
        return self
    
    def _fetch_hsgt_flow(self):
        """获取沪深港通资金流向"""
        try:
            print("\n正在获取沪深港通资金流向数据...")
            self.hsgt_flow = self.pro.moneyflow_hsgt(start_date=self.start_date, end_date=self.end_date)
            if not self.hsgt_flow.empty:
                # 格式化和处理数据
                self.hsgt_flow = self.hsgt_flow.sort_values('trade_date')
                self.hsgt_flow['trade_date'] = pd.to_datetime(self.hsgt_flow['trade_date'])
                # 单位转换：将元转换为亿元
                self.hsgt_flow['north_money'] = self.hsgt_flow['north_money'] / 100000000
                self.hsgt_flow['south_money'] = self.hsgt_flow['south_money'] / 100000000
                # 计算累计流入
                self.hsgt_flow['north_money_cumsum'] = self.hsgt_flow['north_money'].cumsum()
                self.hsgt_flow['south_money_cumsum'] = self.hsgt_flow['south_money'].cumsum()
                print(f"获取到 {len(self.hsgt_flow)} 条沪深港通流向记录")
            else:
                print("未获取到沪深港通资金流向数据")
        except Exception as e:
            print(f"获取沪深港通资金流向出错: {e}")
            self.hsgt_flow = pd.DataFrame()
    
    def _fetch_ggt_daily(self):
        """获取港股通每日成交统计"""
        try:
            print("\n正在获取港股通每日成交统计...")
            self.ggt_daily = self.pro.ggt_daily(start_date=self.start_date, end_date=self.end_date)
            if not self.ggt_daily.empty:
                # 格式化和处理数据
                self.ggt_daily = self.ggt_daily.sort_values('trade_date')
                self.ggt_daily['trade_date'] = pd.to_datetime(self.ggt_daily['trade_date'])
                # 计算净流入
                self.ggt_daily['net_flow'] = self.ggt_daily['buy_amount'] - self.ggt_daily['sell_amount']
                # 计算累计净流入
                self.ggt_daily['net_flow_cumsum'] = self.ggt_daily['net_flow'].cumsum()
                print(f"获取到 {len(self.ggt_daily)} 条港股通每日成交记录")
            else:
                print("未获取到港股通每日成交统计数据")
        except Exception as e:
            print(f"获取港股通每日成交统计出错: {e}")
            self.ggt_daily = pd.DataFrame()
    
    def _fetch_foreign_investment(self):
        """获取外资(QFII/RQFII)持股数据"""
        try:
            print("\n正在获取外资持股数据...")
            # 获取特定日期的外资持股数据
            # 因为外资持股数据通常按季度或月度发布，我们选择几个关键日期点
            sample_dates = []
            
            # 尝试获取季度末数据
            current_date = pd.to_datetime(self.start_date)
            end_date = pd.to_datetime(self.end_date)
            
            while current_date <= end_date:
                # 获取每个季度末的数据
                if current_date.month in [3, 6, 9, 12]:
                    # 获取月末日期
                    month_end = pd.Timestamp(current_date.year, current_date.month, 1) + pd.offsets.MonthEnd(1)
                    sample_dates.append(month_end.strftime('%Y%m%d'))
                current_date += pd.DateOffset(months=1)
            
            # 如果日期太少，添加更多日期点
            if len(sample_dates) < 2:
                sample_dates = [self.start_date, self.end_date]
            
            print(f"将获取以下日期的外资持股数据: {sample_dates}")
            
            all_foreign_data = []
            for date in sample_dates:
                try:
                    # 尝试使用 Tushare 的 QFII持股 API (如果可用)
                    foreign_data = self.pro.query('qfii_hold', trade_date=date)
                    if not foreign_data.empty:
                        foreign_data['trade_date'] = pd.to_datetime(date)
                        all_foreign_data.append(foreign_data)
                        print(f"获取到 {date} 的外资持股数据 ({len(foreign_data)}条)")
                except Exception as e:
                    print(f"获取 {date} 的外资持股数据出错: {e}")
            
            if all_foreign_data:
                self.foreign_hold = pd.concat(all_foreign_data, ignore_index=True)
                # 计算外资持股市值总和
                self.foreign_hold['hold_value'] = self.foreign_hold['hold_vol'] * self.foreign_hold['price']
                self.foreign_hold = self.foreign_hold.groupby('trade_date').agg({'hold_value': 'sum'}).reset_index()
                self.foreign_hold['hold_value'] = self.foreign_hold['hold_value'] / 100000000  # 转换为亿元
                print(f"合并后获取到 {len(self.foreign_hold)} 个日期点的外资持股数据")
            else:
                print("未获取到任何外资持股数据，将使用替代方法估算")
                
                # 如果无法获取QFII数据，使用北向资金作为外资流入的替代指标
                if not self.hsgt_flow.empty:
                    # 假设外资流入与北向资金有一定关联，但外资更加分散
                    # 根据一般经验，我们假设外资流入约为北向资金的60-70%
                    self.foreign_hold = self.hsgt_flow[['trade_date']].copy()
                    self.foreign_hold['foreign_flow'] = self.hsgt_flow['north_money'] * 0.65
                    self.foreign_hold['foreign_flow_cumsum'] = self.foreign_hold['foreign_flow'].cumsum()
                    print("已使用北向资金数据估算外资流入")
                else:
                    # 如果北向资金也没有，创建一个空的DataFrame
                    self.foreign_hold = pd.DataFrame(columns=['trade_date', 'foreign_flow', 'foreign_flow_cumsum'])
        except Exception as e:
            print(f"获取外资数据整体出错: {e}")
            # 创建空的DataFrame
            self.foreign_hold = pd.DataFrame(columns=['trade_date', 'foreign_flow', 'foreign_flow_cumsum'])
    
    def _fetch_margin_data(self):
        """获取融资融券数据作为本地资金参考"""
        try:
            print("\n正在获取融资融券数据...")
            # 获取融资融券汇总数据
            self.margin_data = self.pro.margin(start_date=self.start_date, end_date=self.end_date)
            if not self.margin_data.empty:
                # 格式化和处理数据
                self.margin_data = self.margin_data.sort_values('trade_date')
                self.margin_data['trade_date'] = pd.to_datetime(self.margin_data['trade_date'])
                # 计算融资余额变化（作为本地资金流向的参考）
                self.margin_data['rzye'] = self.margin_data['rzye'] / 100000000  # 转换为亿元
                self.margin_data['rzye_change'] = self.margin_data['rzye'].diff()
                print(f"获取到 {len(self.margin_data)} 条融资融券记录")
            else:
                print("未获取到融资融券数据")
        except Exception as e:
            print(f"获取融资融券数据出错: {e}")
            self.margin_data = pd.DataFrame()
    
    def _fetch_index_data(self):
        """获取相关指数数据"""
        indices = {
            '000001.SH': '上证指数',
            'HSI.HK': '恒生指数'
        }
        
        print("\n正在获取相关指数行情数据...")
        for code, name in indices.items():
            try:
                index_data = self.pro.index_daily(ts_code=code, start_date=self.start_date, end_date=self.end_date)
                if not index_data.empty:
                    # 格式化和处理数据
                    index_data = index_data.sort_values('trade_date')
                    index_data['trade_date'] = pd.to_datetime(index_data['trade_date'])
                    # 计算收益率
                    index_data['pct_change'] = index_data['close'].pct_change()
                    self.index_data[code] = index_data
                    print(f"获取到 {name} ({len(index_data)}条记录)")
                else:
                    print(f"未获取到 {name} 数据")
            except Exception as e:
                print(f"获取 {name} 数据出错: {e}")
    
    def analyze_fund_proportions(self):
        """分析南向资金和外资的比例"""
        print("\n===== 南向资金和外资比例分析 =====")
        
        # 准备数据
        has_south_data = not self.hsgt_flow.empty
        has_foreign_data = not self.foreign_hold.empty
        has_margin_data = not self.margin_data.empty
        
        if not has_south_data and not has_foreign_data:
            print("没有足够的数据进行南向资金和外资比例分析")
            return self
        
        # 1. 分析南向资金和外资的累计流入
        print("\n累计资金流入比较:")
        
        if has_south_data:
            south_total = self.hsgt_flow['south_money'].sum()
            print(f"南向资金累计净流入: {south_total:.2f}亿元")
        
        if has_foreign_data and 'foreign_flow' in self.foreign_hold.columns:
            foreign_total = self.foreign_hold['foreign_flow'].sum()
            print(f"外资累计净流入(估计): {foreign_total:.2f}亿元")
        elif has_foreign_data and 'hold_value' in self.foreign_hold.columns:
            # 如果只有持仓数据，计算持仓变化
            if len(self.foreign_hold) > 1:
                foreign_change = self.foreign_hold['hold_value'].iloc[-1] - self.foreign_hold['hold_value'].iloc[0]
                print(f"外资持股市值变化: {foreign_change:.2f}亿元")
            else:
                print(f"外资总持股市值: {self.foreign_hold['hold_value'].iloc[0]:.2f}亿元")
        
        # 2. 计算南向资金与外资的比例
        if has_south_data and has_foreign_data and 'foreign_flow' in self.foreign_hold.columns:
            south_total = self.hsgt_flow['south_money'].sum()
            foreign_total = self.foreign_hold['foreign_flow'].sum()
            
            if south_total != 0 and foreign_total != 0:
                if south_total > 0 and foreign_total > 0:
                    # 两者都是正的，计算比例
                    ratio = south_total / foreign_total
                    print(f"\n南向资金与外资流入比例: {ratio:.2f} (南向资金 / 外资)")
                    if ratio > 1:
                        print(f"南向资金流入是外资流入的 {ratio:.2f} 倍")
                    else:
                        print(f"外资流入是南向资金流入的 {1/ratio:.2f} 倍")
                elif south_total < 0 and foreign_total < 0:
                    # 两者都是负的，计算流出比例
                    ratio = abs(south_total) / abs(foreign_total)
                    print(f"\n南向资金与外资流出比例: {ratio:.2f} (南向资金 / 外资)")
                    if ratio > 1:
                        print(f"南向资金流出是外资流出的 {ratio:.2f} 倍")
                    else:
                        print(f"外资流出是南向资金流出的 {1/ratio:.2f} 倍")
                else:
                    # 一正一负
                    print("\n南向资金和外资流向相反")
                    if south_total > 0:
                        print(f"南向资金净流入 {south_total:.2f}亿元，而外资净流出 {abs(foreign_total):.2f}亿元")
                    else:
                        print(f"南向资金净流出 {abs(south_total):.2f}亿元，而外资净流入 {foreign_total:.2f}亿元")
        
        # 3. 分析本地资金(融资余额变化)与外资和南向资金的对比
        if has_margin_data and (has_south_data or has_foreign_data):
            margin_change = self.margin_data['rzye_change'].sum()
            print(f"\n本地融资余额变化: {margin_change:.2f}亿元")
            
            if has_south_data:
                south_total = self.hsgt_flow['south_money'].sum()
                if margin_change != 0 and south_total != 0:
                    local_south_ratio = abs(margin_change) / abs(south_total)
                    print(f"本地融资余额变化与南向资金的比例: {local_south_ratio:.2f}")
            
            if has_foreign_data and 'foreign_flow' in self.foreign_hold.columns:
                foreign_total = self.foreign_hold['foreign_flow'].sum()
                if margin_change != 0 and foreign_total != 0:
                    local_foreign_ratio = abs(margin_change) / abs(foreign_total)
                    print(f"本地融资余额变化与外资的比例: {local_foreign_ratio:.2f}")
        
        # 4. 分析三者的相对贡献
        if has_south_data and has_foreign_data and has_margin_data and 'foreign_flow' in self.foreign_hold.columns:
            south_total = self.hsgt_flow['south_money'].sum()
            foreign_total = self.foreign_hold['foreign_flow'].sum()
            margin_change = self.margin_data['rzye_change'].sum()
            
            total_fund = abs(south_total) + abs(foreign_total) + abs(margin_change)
            if total_fund > 0:
                south_pct = abs(south_total) / total_fund * 100
                foreign_pct = abs(foreign_total) / total_fund * 100
                margin_pct = abs(margin_change) / total_fund * 100
                
                print("\n各类资金占比分析:")
                print(f"南向资金占比: {south_pct:.2f}%")
                print(f"外资占比: {foreign_pct:.2f}%")
                print(f"本地融资余额变化占比: {margin_pct:.2f}%")
                
                # 确定最主要的资金来源
                max_pct = max(south_pct, foreign_pct, margin_pct)
                if max_pct == south_pct:
                    print("在观察期内，南向资金是最主要的资金流向")
                elif max_pct == foreign_pct:
                    print("在观察期内，外资是最主要的资金流向")
                else:
                    print("在观察期内，本地融资余额变化是最主要的资金流向")
        
        # 5. 分析最近趋势
        if has_south_data and has_foreign_data and 'foreign_flow' in self.foreign_hold.columns:
            # 确保外资数据和南向资金数据在同一时间点上
            if len(self.hsgt_flow) >= 10 and len(self.foreign_hold) >= 10:
                # 取南向资金最近10天数据
                recent_south = self.hsgt_flow.tail(10)['south_money'].sum()
                # 创建外资日期索引用于匹配
                foreign_dates = self.foreign_hold['trade_date'].tolist()
                # 筛选出最近10天在外资日期列表中的南向资金数据
                recent_south_foreign_dates = self.hsgt_flow[self.hsgt_flow['trade_date'].isin(foreign_dates)].tail(10)
                
                if not recent_south_foreign_dates.empty:
                    recent_south_matched = recent_south_foreign_dates['south_money'].sum()
                    recent_foreign = self.foreign_hold.tail(len(recent_south_foreign_dates))['foreign_flow'].sum()
                    
                    print("\n最近趋势比较:")
                    print(f"南向资金最近流入: {recent_south:.2f}亿元")
                    print(f"外资最近流入(估计): {recent_foreign:.2f}亿元")
                    
                    if recent_south_matched != 0 and recent_foreign != 0:
                        # 计算最近的比例变化
                        recent_ratio = abs(recent_south_matched) / abs(recent_foreign)
                        print(f"最近南向资金与外资比例: {recent_ratio:.2f}")
                        
                        # 判断趋势变化
                        south_total = self.hsgt_flow['south_money'].sum()
                        foreign_total = self.foreign_hold['foreign_flow'].sum()
                        if south_total != 0 and foreign_total != 0:
                            overall_ratio = abs(south_total) / abs(foreign_total)
                            ratio_change = recent_ratio - overall_ratio
                            
                            if abs(ratio_change) > 0.2:  # 至少20%的变化才有意义
                                if ratio_change > 0:
                                    print("近期南向资金相对于外资的重要性正在增加")
                                else:
                                    print("近期外资相对于南向资金的重要性正在增加")
                            else:
                                print("近期南向资金与外资的相对重要性保持稳定")
        
        return self
    
    def analyze_hk_market_detail(self):
        """详细分析港股市场资金流入情况"""
        print("\n===== 港股市场资金流入详细分析 =====")
        
        # 分析南向资金流入港股的特点
        if not self.hsgt_flow.empty:
            # 南向资金总体分析
            south_total = self.hsgt_flow['south_money'].sum()
            south_avg = self.hsgt_flow['south_money'].mean()
            
            print("\n南向资金流入港股分析:")
            print(f"期间总净流入: {south_total:.2f}亿元")
            print(f"日均净流入: {south_avg:.2f}亿元")
            
            # 计算持续流入/流出天数
            inflow_days = (self.hsgt_flow['south_money'] > 0).sum()
            outflow_days = (self.hsgt_flow['south_money'] < 0).sum()
            total_days = len(self.hsgt_flow)
            
            print(f"净流入天数: {inflow_days} ({inflow_days/total_days*100:.1f}%)")
            print(f"净流出天数: {outflow_days} ({outflow_days/total_days*100:.1f}%)")
            
            # 计算最大连续流入/流出天数
            south_sign = np.sign(self.hsgt_flow['south_money'])
            count = 1
            max_inflow_streak = 0
            max_outflow_streak = 0
            current_streak = 0
            current_sign = 0
            
            for sign in south_sign:
                if sign == current_sign:
                    current_streak += 1
                else:
                    if current_sign > 0 and current_streak > max_inflow_streak:
                        max_inflow_streak = current_streak
                    elif current_sign < 0 and current_streak > max_outflow_streak:
                        max_outflow_streak = current_streak
                    current_streak = 1
                    current_sign = sign
            
            # 检查最后一个连续序列
            if current_sign > 0 and current_streak > max_inflow_streak:
                max_inflow_streak = current_streak
            elif current_sign < 0 and current_streak > max_outflow_streak:
                max_outflow_streak = current_streak
            
            print(f"最大连续净流入天数: {max_inflow_streak}")
            print(f"最大连续净流出天数: {max_outflow_streak}")
        
        # 分析港股通详细买卖情况
        if not self.ggt_daily.empty:
            print("\n港股通成交分析:")
            total_buy = self.ggt_daily['buy_amount'].sum()
            total_sell = self.ggt_daily['sell_amount'].sum()
            total_volume = (self.ggt_daily['buy_volume'].sum() + self.ggt_daily['sell_volume'].sum()) / 2
            
            print(f"总买入: {total_buy:.2f}亿元")
            print(f"总卖出: {total_sell:.2f}亿元")
            print(f"净买入: {total_buy - total_sell:.2f}亿元")
            print(f"总成交量: {total_volume:.2f}亿股")
            print(f"平均成交价: {(total_buy + total_sell) / (2 * total_volume):.2f}元/股")
            
            # 分析买卖活跃度
            if total_buy > 0 and total_sell > 0:
                buy_sell_ratio = total_buy / total_sell
                print(f"买卖比: {buy_sell_ratio:.2f}")
                
                if buy_sell_ratio > 1.2:
                    print("买入意愿明显强于卖出意愿")
                elif buy_sell_ratio < 0.8:
                    print("卖出意愿明显强于买入意愿")
                else:
                    print("买卖意愿较为平衡")
        
        # 分析港股通与外资的共同影响
        if not self.ggt_daily.empty and not self.foreign_hold.empty and 'foreign_flow' in self.foreign_hold.columns:
            # 尝试合并数据并分析
            try:
                combined_dates = set(self.ggt_daily['trade_date']).intersection(set(self.foreign_hold['trade_date']))
                if combined_dates:
                    filtered_ggt = self.ggt_daily[self.ggt_daily['trade_date'].isin(combined_dates)]
                    filtered_foreign = self.foreign_hold[self.foreign_hold['trade_date'].isin(combined_dates)]
                    
                    # 确保日期匹配并合并
                    merged_data = pd.merge(
                        filtered_ggt[['trade_date', 'net_flow']], 
                        filtered_foreign[['trade_date', 'foreign_flow']],
                        on='trade_date', how='inner'
                    )
                    
                    if not merged_data.empty:
                        # 计算南向资金和外资的相关性
                        corr = merged_data['net_flow'].corr(merged_data['foreign_flow'])
                        print(f"\n南向资金与外资流向相关系数: {corr:.4f}")
                        
                        if abs(corr) > 0.5:
                            print("南向资金与外资流向具有较强的相关性")
                            if corr > 0:
                                print("两者趋势基本一致，可能反映共同市场看法")
                            else:
                                print("两者趋势基本相反，可能代表不同投资策略")
                        elif abs(corr) > 0.3:
                            print("南向资金与外资流向具有中等相关性")
                        else:
                            print("南向资金与外资流向相关性较弱，可能受不同因素驱动")
                        
                        # 计算南向资金和外资在港股市场的综合影响
                        total_impact = merged_data['net_flow'].sum() + merged_data['foreign_flow'].sum()
                        print(f"南向资金和外资对港股的综合影响: {total_impact:.2f}亿元")
                        
                        # 分析两者对港股的相对贡献
                        ggt_contribution = merged_data['net_flow'].sum() / abs(total_impact) * 100
                        foreign_contribution = merged_data['foreign_flow'].sum() / abs(total_impact) * 100
                        
                        print(f"南向资金贡献: {ggt_contribution:.2f}%")
                        print(f"外资贡献: {foreign_contribution:.2f}%")
                        
                        if abs(ggt_contribution) > abs(foreign_contribution):
                            print("南向资金对港股市场的影响更为显著")
                        else:
                            print("外资对港股市场的影响更为显著")
            except Exception as e:
                print(f"分析南向资金与外资共同影响时出错: {e}")
        
        # 分析港股市场表现与资金流向的关系
        if not self.hsgt_flow.empty and 'HSI.HK' in self.index_data:
            try:
                # 合并数据
                hsi_data = self.index_data['HSI.HK']
                combined_data = pd.merge(
                    self.hsgt_flow[['trade_date', 'south_money']], 
                    hsi_data[['trade_date', 'pct_change']],
                    on='trade_date', how='inner'
                )
                
                if not combined_data.empty:
                    # 计算相关系数
                    corr = combined_data['south_money'].corr(combined_data['pct_change'])
                    print(f"\n南向资金与恒生指数涨跌相关系数: {corr:.4f}")
                    
                    if abs(corr) > 0.5:
                        print(f"南向资金与恒生指数涨跌具有较强的{('正相关' if corr > 0 else '负相关')}关系")
                    elif abs(corr) > 0.3:
                        print(f"南向资金与恒生指数涨跌具有中等{('正相关' if corr > 0 else '负相关')}关系")
                    else:
                        print("南向资金与恒生指数涨跌相关性较弱")
                    
                    # 分析滞后效应
                    for lag in [1, 3, 5]:
                        combined_data[f'south_money_lag{lag}'] = combined_data['south_money'].shift(lag)
                        lag_corr = combined_data[f'south_money_lag{lag}'].corr(combined_data['pct_change'])
                        print(f"南向资金滞后{lag}日与恒生指数涨跌相关系数: {lag_corr:.4f}")
                        
                        if abs(lag_corr) > abs(corr) and abs(lag_corr) > 0.3:
                            print(f"南向资金对恒生指数存在{lag}日的滞后效应")
            except Exception as e:
                print(f"分析南向资金与恒生指数关系时出错: {e}")
        
        return self
    
    def generate_summary_report(self):
        """生成综合分析报告"""
        print("\n========== 港股资金流向综合分析报告 ==========")
        
        # 汇总数据准备
        has_south_data = not self.hsgt_flow.empty
        has_ggt_data = not self.ggt_daily.empty
        has_foreign_data = not self.foreign_hold.empty
        has_hsi_data = 'HSI.HK' in self.index_data
        
        if not has_south_data and not has_ggt_data and not has_foreign_data:
            print("没有足够的数据生成报告")
            return self
        
        # 报告概览
        print(f"\n分析期间: {self.start_date} 至 {self.end_date}")
        
        # 1. 资金流向总结
        print("\n资金流向总结:")
        total_flows = {}
        
        if has_south_data:
            south_total = self.hsgt_flow['south_money'].sum()
            total_flows['南向资金'] = south_total
            print(f"南向资金累计净流入: {south_total:.2f}亿元")
        
        if has_foreign_data and 'foreign_flow' in self.foreign_hold.columns:
            foreign_total = self.foreign_hold['foreign_flow'].sum()
            total_flows['外资'] = foreign_total
            print(f"外资累计净流入(估计): {foreign_total:.2f}亿元")
        
        if has_ggt_data:
            net_total = self.ggt_daily['net_flow'].sum()
            total_flows['港股通净流入'] = net_total
            print(f"港股通累计净流入: {net_total:.2f}亿元")
        
        # 2. 资金比例分析
        if len(total_flows) > 1:
            print("\n资金来源比例:")
            total_abs_flow = sum(abs(v) for v in total_flows.values())
            for source, amount in total_flows.items():
                percentage = abs(amount) / total_abs_flow * 100
                print(f"{source}: {percentage:.2f}%")
        
        # 3. 市场影响分析
        if has_hsi_data and has_south_data:
            hsi_change = (self.index_data['HSI.HK']['close'].iloc[-1] / self.index_data['HSI.HK']['close'].iloc[0] - 1) * 100
            print(f"\n期间恒生指数变化: {hsi_change:.2f}%")
            
            # 计算相关性
            merged_data = pd.merge(
                self.hsgt_flow[['trade_date', 'south_money']], 
                self.index_data['HSI.HK'][['trade_date', 'pct_change']],
                on='trade_date', how='inner'
            )
            
            if not merged_data.empty:
                corr = merged_data['south_money'].corr(merged_data['pct_change'])
                print(f"南向资金与恒生指数相关性: {corr:.4f}")
        
        # 4. 南向资金与外资对比
        if has_south_data and has_foreign_data and 'foreign_flow' in self.foreign_hold.columns:
            south_total = total_flows.get('南向资金', 0)
            foreign_total = total_flows.get('外资', 0)
            
            if south_total != 0 and foreign_total != 0:
                ratio = abs(south_total) / abs(foreign_total)
                print(f"\n南向资金与外资比例: {ratio:.2f}")
                
                if south_total > 0 and foreign_total > 0:
                    print("南向资金和外资均呈净流入趋势")
                elif south_total < 0 and foreign_total < 0:
                    print("南向资金和外资均呈净流出趋势")
                else:
                    print("南向资金和外资流向相反")
        
        # 5. 结论与建议
        print("\n结论与建议:")
        
        # 基于资金流向的市场判断
        if has_south_data:
            south_total = total_flows.get('南向资金', 0)
            recent_south = self.hsgt_flow.tail(10)['south_money'].sum() if len(self.hsgt_flow) >= 10 else None
            
            # 分析整体趋势
            if south_total > 0:
                print("- 南向资金整体呈净流入趋势，港股市场基本面较为稳健")
            else:
                print("- 南向资金整体呈净流出趋势，港股市场可能面临压力")
            
            # 分析最近趋势
            if recent_south is not None:
                if recent_south > 0 and south_total > 0:
                    print("- 近期南向资金持续净流入，保持看好港股市场")
                elif recent_south > 0 and south_total < 0:
                    print("- 南向资金近期由净流出转为净流入，港股市场情绪可能正在改善")
                elif recent_south < 0 and south_total > 0:
                    print("- 南向资金近期由净流入转为净流出，需警惕港股市场走势变化")
                else:
                    print("- 南向资金持续净流出，对港股市场保持谨慎")
        
        if has_foreign_data and 'foreign_flow' in self.foreign_hold.columns:
            foreign_total = total_flows.get('外资', 0)
            if foreign_total > 0:
                print("- 外资整体呈净流入趋势，国际资金对港股市场态度偏积极")
            else:
                print("- 外资整体呈净流出趋势，国际资金对港股市场态度偏谨慎")
        
        # 南向资金与外资比较
        if has_south_data and has_foreign_data and 'foreign_flow' in self.foreign_hold.columns:
            south_total = total_flows.get('南向资金', 0)
            foreign_total = total_flows.get('外资', 0)
            
            if (south_total > 0 and foreign_total < 0) or (south_total < 0 and foreign_total > 0):
                print("- 南向资金与外资流向不一致，可能反映内地与国际投资者对港股市场的看法存在分歧")
            elif south_total > 0 and foreign_total > 0:
                print("- 南向资金与外资均呈净流入，反映内地和国际投资者对港股市场均持积极态度")
            else:
                print("- 南向资金与外资均呈净流出，反映内地和国际投资者对港股市场均持谨慎态度")
        
        return self
    
    def run_analysis(self):
        """运行完整分析流程"""
        self.fetch_all_data()
        self.analyze_fund_proportions()
        self.analyze_hk_market_detail()
        self.generate_summary_report()
        return self

# 示例用法
if __name__ == "__main__":
    analyzer = CapitalFlowAnalyzer()
    analyzer.run_analysis()