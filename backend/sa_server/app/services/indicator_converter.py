# app/services/indicator_converter.py
from typing import List, Dict, Any, Optional, Union, TypeVar, Callable
from datetime import datetime
import re
from app.utils.json_utils import clean_nan_values

T = TypeVar('T')

class IndicatorConverter:
    """
    统一指标数据转换服务
    将不同指标的数据转换为前端图表组件需要的标准格式
    """
    
    @staticmethod
    def get_attr(obj: Any, attr: str, default: Any = None) -> Any:
        """
        从对象中获取属性值的通用方法，支持Pydantic模型和字典
        
        Args:
            obj: 要获取属性的对象，可以是Pydantic模型或字典
            attr: 属性名称
            default: 如果属性不存在，返回的默认值
            
        Returns:
            属性值，如果不存在则返回默认值
        """
        if hasattr(obj, attr):
            return getattr(obj, attr)
        elif isinstance(obj, dict) and attr in obj:
            return obj[attr]
        return default
    
    @staticmethod
    def ensure_dict_list(data_list: List[Any]) -> List[Dict[str, Any]]:
        """
        确保传入的数据列表中的每个项都是字典
        
        Args:
            data_list: 数据列表，可能包含Pydantic模型或字典
            
        Returns:
            包含字典的列表
        """
        result = []
        for item in data_list:
            if hasattr(item, 'dict') and callable(getattr(item, 'dict')):
                # 是Pydantic模型，转为字典
                result.append(item.dict())
            else:
                # 已经是字典或其他类型
                result.append(item)
        return result
    
    @staticmethod
    def convert_date_format(date_str: str, input_format: str = 'YYYYMM') -> str:
        """
        转换日期格式为标准的 YYYY-MM 格式
        
        Args:
            date_str: 输入的日期字符串
            input_format: 输入日期的格式
        
        Returns:
            标准格式的日期字符串 YYYY-MM 或 YYYY-QQ
        """
        if input_format == 'YYYYMM':
            # 处理月度数据 YYYYMM -> YYYY-MM
            if len(date_str) == 6:
                return f"{date_str[:4]}-{date_str[4:6]}"
        elif input_format == 'YYYYQQ':
            # 处理季度数据 YYYYQQ -> YYYY-QQ
            if len(date_str) == 6:
                return f"{date_str[:4]}-Q{date_str[5]}"
        
        # 如果格式不匹配，原样返回
        return date_str
    
    @staticmethod
    def convert_cpi_data(cpi_data: List[Any]) -> Dict[str, Any]:
        """
        转换CPI数据为标准格式
        
        Args:
            cpi_data: 原始CPI数据列表
        
        Returns:
            转换后的标准格式数据，包含national、urban、rural三个系列
        """
        # 清理NaN值
        clean_data = clean_nan_values(cpi_data)
        
        # 转换数据格式
        national_series = []
        urban_series = []
        rural_series = []
        
        for item in clean_data:
            # 转换日期格式
            month = IndicatorConverter.get_attr(item, 'month')
            if month is None:
                continue  # 跳过没有month字段的记录
                
            date = IndicatorConverter.convert_date_format(month)
            
            # 全国数据
            nt_val = IndicatorConverter.get_attr(item, 'nt_val')
            if nt_val is not None:
                national_series.append({
                    'date': date,
                    'value': nt_val,
                    'yoy': IndicatorConverter.get_attr(item, 'nt_yoy'),
                    'mom': IndicatorConverter.get_attr(item, 'nt_mom')
                })
            
            # 城市数据
            town_val = IndicatorConverter.get_attr(item, 'town_val')
            if town_val is not None:
                urban_series.append({
                    'date': date,
                    'value': town_val,
                    'yoy': IndicatorConverter.get_attr(item, 'town_yoy'),
                    'mom': IndicatorConverter.get_attr(item, 'town_mom')
                })
            
            # 农村数据
            cnt_val = IndicatorConverter.get_attr(item, 'cnt_val')
            if cnt_val is not None:
                rural_series.append({
                    'date': date,
                    'value': cnt_val,
                    'yoy': IndicatorConverter.get_attr(item, 'cnt_yoy'),
                    'mom': IndicatorConverter.get_attr(item, 'cnt_mom')
                })
        
        return {
            'national': {
                'name': '全国CPI',
                'color': '#1890ff',
                'data': national_series
            },
            'urban': {
                'name': '城市CPI',
                'color': '#52c41a',
                'data': urban_series
            },
            'rural': {
                'name': '农村CPI',
                'color': '#fa8c16',
                'data': rural_series
            }
        }
    
    @staticmethod
    def convert_gdp_data(gdp_data: List[Any]) -> Dict[str, Any]:
        """
        转换GDP数据为标准格式
        
        Args:
            gdp_data: 原始GDP数据列表
        
        Returns:
            转换后的标准格式数据，包含gdp、primaryIndustry、secondaryIndustry、tertiaryIndustry四个系列
        """
        # 清理NaN值
        clean_data = clean_nan_values(gdp_data)
        
        # 转换数据格式
        gdp_series = []
        primary_industry_series = []
        secondary_industry_series = []
        tertiary_industry_series = []
        
        for item in clean_data:
            # 转换日期格式 - GDP是季度数据
            quarter = IndicatorConverter.get_attr(item, 'quarter')
            if quarter is None:
                continue
                
            date = IndicatorConverter.convert_date_format(quarter, 'YYYYQQ')
            
            # GDP数据
            gdp = IndicatorConverter.get_attr(item, 'gdp')
            if gdp is not None:
                gdp_series.append({
                    'date': date,
                    'value': gdp,
                    'yoy': IndicatorConverter.get_attr(item, 'gdp_yoy')
                })
            
            # 第一产业
            pi = IndicatorConverter.get_attr(item, 'pi')
            if pi is not None:
                primary_industry_series.append({
                    'date': date,
                    'value': pi,
                    'yoy': IndicatorConverter.get_attr(item, 'pi_yoy')
                })
            
            # 第二产业
            si = IndicatorConverter.get_attr(item, 'si')
            if si is not None:
                secondary_industry_series.append({
                    'date': date,
                    'value': si,
                    'yoy': IndicatorConverter.get_attr(item, 'si_yoy')
                })
            
            # 第三产业
            ti = IndicatorConverter.get_attr(item, 'ti')
            if ti is not None:
                tertiary_industry_series.append({
                    'date': date,
                    'value': ti,
                    'yoy': IndicatorConverter.get_attr(item, 'ti_yoy')
                })
        
        return {
            'gdp': {
                'name': 'GDP总量',
                'color': '#1890ff',
                'data': gdp_series
            },
            'primaryIndustry': {
                'name': '第一产业',
                'color': '#52c41a',
                'data': primary_industry_series
            },
            'secondaryIndustry': {
                'name': '第二产业',
                'color': '#fa8c16',
                'data': secondary_industry_series
            },
            'tertiaryIndustry': {
                'name': '第三产业',
                'color': '#722ed1',
                'data': tertiary_industry_series
            }
        }
    
    @staticmethod
    def convert_m_data(m_data: List[Any]) -> Dict[str, Any]:
        """
        转换货币供应量数据为标准格式
        
        Args:
            m_data: 原始货币供应量数据列表
        
        Returns:
            转换后的标准格式数据，包含m0、m1、m2三个系列
        """
        # 清理NaN值
        clean_data = clean_nan_values(m_data)
        
        # 转换数据格式
        m0_series = []
        m1_series = []
        m2_series = []
        
        for item in clean_data:
            # 转换日期格式
            month = IndicatorConverter.get_attr(item, 'month')
            if month is None:
                continue
                
            date = IndicatorConverter.convert_date_format(month)
            
            # M0数据
            m0 = IndicatorConverter.get_attr(item, 'm0')
            if m0 is not None:
                m0_series.append({
                    'date': date,
                    'value': m0,
                    'yoy': IndicatorConverter.get_attr(item, 'm0_yoy'),
                    'mom': IndicatorConverter.get_attr(item, 'm0_mom')
                })
            
            # M1数据
            m1 = IndicatorConverter.get_attr(item, 'm1')
            if m1 is not None:
                m1_series.append({
                    'date': date,
                    'value': m1,
                    'yoy': IndicatorConverter.get_attr(item, 'm1_yoy'),
                    'mom': IndicatorConverter.get_attr(item, 'm1_mom')
                })
            
            # M2数据
            m2 = IndicatorConverter.get_attr(item, 'm2')
            if m2 is not None:
                m2_series.append({
                    'date': date,
                    'value': m2,
                    'yoy': IndicatorConverter.get_attr(item, 'm2_yoy'),
                    'mom': IndicatorConverter.get_attr(item, 'm2_mom')
                })
        
        return {
            'm0': {
                'name': 'M0货币供应量',
                'color': '#1890ff',
                'data': m0_series
            },
            'm1': {
                'name': 'M1货币供应量',
                'color': '#52c41a',
                'data': m1_series
            },
            'm2': {
                'name': 'M2货币供应量',
                'color': '#fa8c16',
                'data': m2_series
            }
        }
    
    @staticmethod
    def convert_pmi_data(pmi_data: List[Any]) -> Dict[str, Any]:
        """
        转换PMI数据为标准格式
        
        Args:
            pmi_data: 原始PMI数据列表
        
        Returns:
            转换后的标准格式数据，包含主要的PMI指数系列
        """
        # 清理NaN值
        clean_data = clean_nan_values(pmi_data)
        
        # 转换数据格式
        manufacturing_pmi_series = []
        nonmanufacturing_pmi_series = []
        composite_pmi_series = []
        
        for item in clean_data:
            # 转换日期格式
            month = IndicatorConverter.get_attr(item, 'month')
            if month is None:
                continue
                
            date = IndicatorConverter.convert_date_format(month)
            
            # 制造业PMI
            pmi010000 = IndicatorConverter.get_attr(item, 'pmi010000')
            if pmi010000 is not None:
                manufacturing_pmi_series.append({
                    'date': date,
                    'value': pmi010000
                })
            
            # 非制造业PMI (使用商务活动指数作为代表)
            pmi020100 = IndicatorConverter.get_attr(item, 'pmi020100')
            if pmi020100 is not None:
                nonmanufacturing_pmi_series.append({
                    'date': date,
                    'value': pmi020100
                })
            
            # 综合PMI
            pmi030000 = IndicatorConverter.get_attr(item, 'pmi030000')
            if pmi030000 is not None:
                composite_pmi_series.append({
                    'date': date,
                    'value': pmi030000
                })
        
        return {
            'manufacturingPMI': {
                'name': '制造业PMI',
                'color': '#1890ff',
                'data': manufacturing_pmi_series
            },
            'nonmanufacturingPMI': {
                'name': '非制造业PMI',
                'color': '#52c41a',
                'data': nonmanufacturing_pmi_series
            },
            'compositePMI': {
                'name': '综合PMI',
                'color': '#fa8c16',
                'data': composite_pmi_series
            }
        }
    
    @staticmethod
    def convert_by_indicator_type(indicator_type: str, data: List[Any]) -> Dict[str, Any]:
        """
        根据指标类型选择合适的转换方法
        
        Args:
            indicator_type: 指标类型标识，如'cpi'、'gdp'、'pmi'、'm'
            data: 原始数据列表
        
        Returns:
            转换后的标准格式数据
        """
        converters = {
            'cpi': IndicatorConverter.convert_cpi_data,
            'gdp': IndicatorConverter.convert_gdp_data,
            'm': IndicatorConverter.convert_m_data,
            'pmi': IndicatorConverter.convert_pmi_data
        }
        
        converter = converters.get(indicator_type.lower())
        if not converter:
            raise ValueError(f"未知的指标类型: {indicator_type}")
        
        return converter(data)