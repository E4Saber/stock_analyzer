import warnings
import numpy as np
import pandas as pd
from app.external.tushare_client import get_tushare_client


warnings.filterwarnings('ignore')

class CapitalFlowCalculator:
    """
    资金流向计算器类
    用于获取并计算沪深港通资金流向、外资持股等基础数据
    """
    def __init__(self):
        """初始化资金流向计算器"""
        self.pro = get_tushare_client()
        # 使用历史日期，避免使用未来日期导致数据为空
        self.end_date = '20240901'  # 可调整为需要的结束日期
        self.start_date = '20250324'  # 默认分析一年数据
        
        # 存储各类数据
        self.hsgt_flow = None  # 沪深港通资金流向
        self.ggt_daily = None  # 港股通每日成交
        self.foreign_hold = None  # 外资持股
        self.margin_data = None  # 融资融券数据(作为本地资金参考)
        self.index_data = {}   # 指数数据
        
        # 调试模式，用于打印更多信息以便排查问题
        self.debug_mode = True
    
    def set_date_range(self, start_date, end_date):
        """设置日期范围"""
        self.start_date = start_date
        self.end_date = end_date
        return self
    
    def fetch_all_data(self):
        """获取所有相关数据"""
        print(f"获取日期范围: {self.start_date} 至 {self.end_date} 的资金流向数据")
        self._fetch_hsgt_flow()
        self._fetch_ggt_daily()
        self._fetch_foreign_investment()
        self._fetch_margin_data()
        self._fetch_index_data()
        
        # 打印数据汇总
        self._print_data_summary()
        
        return self
    
    def _print_data_summary(self):
        """打印数据汇总信息"""
        print("\n===== 资金流向数据汇总 =====")
        
        # 沪深港通资金流向汇总
        if not self.hsgt_flow.empty:
            north_sum = self.hsgt_flow['north_money'].sum()
            north_avg = self.hsgt_flow['north_money'].mean()
            south_sum = self.hsgt_flow['south_money'].sum()
            south_avg = self.hsgt_flow['south_money'].mean()
            
            print("\n沪深港通资金流向:")
            print(f"北向资金累计净流入: {north_sum:.2f}亿元")
            print(f"北向资金日均净流入: {north_avg:.2f}亿元")
            print(f"南向资金累计净流入: {south_sum:.2f}亿元")
            print(f"南向资金日均净流入: {south_avg:.2f}亿元")
            
            # 流入/流出天数统计
            north_inflow_days = (self.hsgt_flow['north_money'] > 0).sum()
            north_outflow_days = (self.hsgt_flow['north_money'] < 0).sum()
            south_inflow_days = (self.hsgt_flow['south_money'] > 0).sum()
            south_outflow_days = (self.hsgt_flow['south_money'] < 0).sum()
            
            print(f"北向资金净流入天数: {north_inflow_days}天")
            print(f"北向资金净流出天数: {north_outflow_days}天")
            print(f"南向资金净流入天数: {south_inflow_days}天")
            print(f"南向资金净流出天数: {south_outflow_days}天")
        
        # 港股通每日成交汇总
        if not self.ggt_daily.empty:
            buy_sum = self.ggt_daily['buy_amount'].sum()
            sell_sum = self.ggt_daily['sell_amount'].sum()
            net_flow = self.ggt_daily['net_flow'].sum()
            
            print("\n港股通成交汇总:")
            print(f"总买入金额: {buy_sum:.2f}亿元")
            print(f"总卖出金额: {sell_sum:.2f}亿元")
            print(f"净买入金额: {net_flow:.2f}亿元")
            
            if 'buy_volume' in self.ggt_daily.columns and 'sell_volume' in self.ggt_daily.columns:
                buy_vol = self.ggt_daily['buy_volume'].sum()
                sell_vol = self.ggt_daily['sell_volume'].sum()
                print(f"总买入量: {buy_vol:.2f}亿股")
                print(f"总卖出量: {sell_vol:.2f}亿股")
        
        # 外资持股汇总
        if not self.foreign_hold.empty:
            print("\n外资持股汇总:")
            if 'foreign_flow' in self.foreign_hold.columns:
                foreign_sum = self.foreign_hold['foreign_flow'].sum()
                foreign_avg = self.foreign_hold['foreign_flow'].mean()
                print(f"外资累计净流入(估计): {foreign_sum:.2f}亿元")
                print(f"外资日均净流入(估计): {foreign_avg:.2f}亿元")
            elif 'hold_value' in self.foreign_hold.columns and len(self.foreign_hold) > 1:
                first_hold = self.foreign_hold['hold_value'].iloc[0]
                last_hold = self.foreign_hold['hold_value'].iloc[-1]
                change = last_hold - first_hold
                print(f"外资持股市值(期初): {first_hold:.2f}亿元")
                print(f"外资持股市值(期末): {last_hold:.2f}亿元")
                print(f"外资持股市值变化: {change:.2f}亿元")
        
        # 融资融券数据汇总
        if not self.margin_data.empty:
            print("\n融资融券数据汇总:")
            rzye_first = self.margin_data['rzye'].iloc[0]
            rzye_last = self.margin_data['rzye'].iloc[-1]
            rzye_change = rzye_last - rzye_first
            
            print(f"融资余额(期初): {rzye_first:.2f}亿元")
            print(f"融资余额(期末): {rzye_last:.2f}亿元")
            print(f"融资余额变化: {rzye_change:.2f}亿元")
        
        # 指数数据汇总
        if self.index_data:
            print("\n指数表现汇总:")
            for code, data in self.index_data.items():
                name = self._get_index_name(code)
                if not data.empty:
                    first_close = data['close'].iloc[0]
                    last_close = data['close'].iloc[-1]
                    change_pct = (last_close / first_close - 1) * 100
                    print(f"{name} 变化: {change_pct:.2f}%，收盘价: {first_close:.2f} -> {last_close:.2f}")
    
    def _get_index_name(self, code):
        """根据指数代码获取指数名称"""
        index_names = {
            '000001.SH': '上证指数',
            'HSI.HK': '恒生指数',
            '399001.SZ': '深证成指'
        }
        return index_names.get(code, code)
    
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
                    # 尝试不同的API获取外资持股数据
                    foreign_data = pd.DataFrame()
                    api_tried = []
                    
                    # 尝试使用qfii_hold接口
                    try:
                        foreign_data = self.pro.query('qfii_hold', trade_date=date)
                        api_tried.append('qfii_hold')
                    except Exception as e:
                        if self.debug_mode:
                            print(f"获取 {date} 的qfii_hold数据出错: {e}")
                    
                    # 如果qfii_hold失败，尝试qfii_shareholding接口
                    if foreign_data.empty:
                        try:
                            foreign_data = self.pro.query('qfii_shareholding', trade_date=date)
                            api_tried.append('qfii_shareholding')
                        except Exception as e:
                            if self.debug_mode:
                                print(f"获取 {date} 的qfii_shareholding数据出错: {e}")
                    
                    # 如果有其他可能的API，继续尝试
                    if foreign_data.empty:
                        try:
                            foreign_data = self.pro.query('foreign_holdings', trade_date=date)
                            api_tried.append('foreign_holdings')
                        except Exception as e:
                            if self.debug_mode:
                                print(f"获取 {date} 的foreign_holdings数据出错: {e}")
                    
                    if not foreign_data.empty:
                        foreign_data['trade_date'] = pd.to_datetime(date)
                        all_foreign_data.append(foreign_data)
                        print(f"获取到 {date} 的外资持股数据 ({len(foreign_data)}条), 使用接口: {', '.join(api_tried)}")
                    else:
                        print(f"未能获取到 {date} 的外资持股数据，尝试了接口: {', '.join(api_tried)}")
                except Exception as e:
                    print(f"获取 {date} 的外资持股数据出错: {e}")
            
            if all_foreign_data:
                self.foreign_hold = pd.concat(all_foreign_data, ignore_index=True)
                # 根据获取到的数据结构进行处理
                if 'hold_vol' in self.foreign_hold.columns and 'price' in self.foreign_hold.columns:
                    # 计算外资持股市值总和
                    self.foreign_hold['hold_value'] = self.foreign_hold['hold_vol'] * self.foreign_hold['price']
                    self.foreign_hold = self.foreign_hold.groupby('trade_date').agg({'hold_value': 'sum'}).reset_index()
                    self.foreign_hold['hold_value'] = self.foreign_hold['hold_value'] / 100000000  # 转换为亿元
                    print(f"合并后获取到 {len(self.foreign_hold)} 个日期点的外资持股数据")
                else:
                    print("外资持股数据列名与预期不符，使用可用列进行计算")
            else:
                print("未获取到任何外资持股数据，将使用替代方法估算")
                
                # 如果无法获取QFII数据，使用北向资金作为外资流入的替代指标
                if not self.hsgt_flow.empty:
                    # 假设外资流入与北向资金有一定关联，但外资更加分散
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
            'HSI.HK': '恒生指数',
            '399001.SZ': '深证成指'
        }
        
        print("\n正在获取相关指数行情数据...")
        for code, name in indices.items():
            try:
                # 尝试获取指数数据
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
                    print(f"未获取到 {name} 数据，尝试备选方法...")
                    
                    # 尝试备选方法获取恒生指数
                    if code == 'HSI.HK':
                        try:
                            # 尝试使用港股指数API
                            alt_data = self.pro.hk_index_daily(ts_code=code, start_date=self.start_date, end_date=self.end_date)
                            if not alt_data.empty:
                                alt_data = alt_data.sort_values('trade_date')
                                alt_data['trade_date'] = pd.to_datetime(alt_data['trade_date'])
                                alt_data['pct_change'] = alt_data['close'].pct_change()
                                self.index_data[code] = alt_data
                                print(f"使用备选API获取到 {name} ({len(alt_data)}条记录)")
                            else:
                                print(f"备选方法仍未获取到 {name} 数据")
                        except Exception as e:
                            print(f"备选方法获取 {name} 出错: {e}")
            except Exception as e:
                print(f"获取 {name} 数据出错: {e}")
                
                # 对于恒生指数，尝试备选方法
                if code == 'HSI.HK':
                    try:
                        alt_data = self.pro.hk_index_daily(ts_code=code, start_date=self.start_date, end_date=self.end_date)
                        if not alt_data.empty:
                            alt_data = alt_data.sort_values('trade_date')
                            alt_data['trade_date'] = pd.to_datetime(alt_data['trade_date'])
                            alt_data['pct_change'] = alt_data['close'].pct_change()
                            self.index_data[code] = alt_data
                            print(f"使用备选API获取到 {name} ({len(alt_data)}条记录)")
                    except Exception as e:
                        print(f"备选方法获取 {name} 出错: {e}")
    
    def export_data(self, filename=None):
        """导出数据到Excel文件"""
        if filename is None:
            filename = f"capital_flow_{self.start_date}_to_{self.end_date}.xlsx"
        
        try:
            with pd.ExcelWriter(filename) as writer:
                # 导出沪深港通资金流向
                if not self.hsgt_flow.empty:
                    self.hsgt_flow.to_excel(writer, sheet_name='沪深港通资金流向', index=False)
                
                # 导出港股通每日成交
                if not self.ggt_daily.empty:
                    self.ggt_daily.to_excel(writer, sheet_name='港股通每日成交', index=False)
                
                # 导出外资持股
                if not self.foreign_hold.empty:
                    self.foreign_hold.to_excel(writer, sheet_name='外资持股', index=False)
                
                # 导出融资融券数据
                if not self.margin_data.empty:
                    self.margin_data.to_excel(writer, sheet_name='融资融券数据', index=False)
                
                # 导出指数数据
                for code, data in self.index_data.items():
                    if not data.empty:
                        name = self._get_index_name(code)
                        data.to_excel(writer, sheet_name=f'指数_{name}', index=False)
            
            print(f"\n数据已成功导出到文件: {filename}")
            return True
        except Exception as e:
            print(f"导出数据到Excel出错: {e}")
            return False
    
    def get_monthly_summary(self):
        """获取月度资金流向汇总"""
        print("\n===== 月度资金流向汇总 =====")
        
        # 按月汇总沪深港通资金流向
        if not self.hsgt_flow.empty:
            # 创建月份列
            self.hsgt_flow['year_month'] = self.hsgt_flow['trade_date'].dt.strftime('%Y-%m')
            
            # 按月汇总
            monthly_hsgt = self.hsgt_flow.groupby('year_month').agg({
                'north_money': 'sum',
                'south_money': 'sum'
            }).reset_index()
            
            print("\n月度沪深港通资金流向:")
            for _, row in monthly_hsgt.iterrows():
                print(f"{row['year_month']}  北向: {row['north_money']:.2f}亿元  南向: {row['south_money']:.2f}亿元")
        
        # 按月汇总外资流入
        if not self.foreign_hold.empty and 'foreign_flow' in self.foreign_hold.columns:
            # 创建月份列
            self.foreign_hold['year_month'] = self.foreign_hold['trade_date'].dt.strftime('%Y-%m')
            
            # 按月汇总
            monthly_foreign = self.foreign_hold.groupby('year_month').agg({
                'foreign_flow': 'sum'
            }).reset_index()
            
            print("\n月度外资资金流向(估计):")
            for _, row in monthly_foreign.iterrows():
                print(f"{row['year_month']}  外资: {row['foreign_flow']:.2f}亿元")
        
        return self
    
    def run_calculation(self):
        """运行完整计算流程"""
        self.fetch_all_data()
        self.get_monthly_summary()
        return self

# 示例用法
if __name__ == "__main__":
    calculator = CapitalFlowCalculator()
    calculator.run_calculation()