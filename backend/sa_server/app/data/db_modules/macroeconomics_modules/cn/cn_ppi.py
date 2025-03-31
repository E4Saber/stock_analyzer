from typing import Optional
from pydantic import BaseModel, field_validator
import re


class CnPpiData(BaseModel):
    """
    Pydantic model for China monthly PPI data.
    
    Fields:
    - month: Month (e.g., '202301')
    - ppi_yoy: PPI for all industrial products - year-on-year
    - ppi_mom: PPI for all industrial products - month-on-month
    - ppi_accu: PPI for all industrial products - accumulated year-on-year
    - And many more detailed PPI categories
    """
    # 月份，作为主键
    month: str
    # PPI：全部工业品：当月同比
    ppi_yoy: Optional[float] = None
    # PPI：生产资料：当月同比
    ppi_mp_yoy: Optional[float] = None
    # PPI：生产资料：采掘业：当月同比
    ppi_mp_qm_yoy: Optional[float] = None
    # PPI：生产资料：原料业：当月同比
    ppi_mp_rm_yoy: Optional[float] = None
    # PPI：生产资料：加工业：当月同比
    ppi_mp_p_yoy: Optional[float] = None
    # PPI：生活资料：当月同比
    ppi_cg_yoy: Optional[float] = None
    # PPI：生活资料：食品类：当月同比
    ppi_cg_f_yoy: Optional[float] = None
    # PPI：生活资料：衣着类：当月同比
    ppi_cg_c_yoy: Optional[float] = None
    # PPI：生活资料：一般日用品类：当月同比
    ppi_cg_adu_yoy: Optional[float] = None
    # PPI：生活资料：耐用消费品类：当月同比
    ppi_cg_dcg_yoy: Optional[float] = None
    # PPI：全部工业品：环比
    ppi_mom: Optional[float] = None
    # PPI：生产资料：环比
    ppi_mp_mom: Optional[float] = None
    # PPI：生产资料：采掘业：环比
    ppi_mp_qm_mom: Optional[float] = None
    # PPI：生产资料：原料业：环比
    ppi_mp_rm_mom: Optional[float] = None
    # PPI：生产资料：加工业：环比
    ppi_mp_p_mom: Optional[float] = None
    # PPI：生活资料：环比
    ppi_cg_mom: Optional[float] = None
    # PPI：生活资料：食品类：环比
    ppi_cg_f_mom: Optional[float] = None
    # PPI：生活资料：衣着类：环比
    ppi_cg_c_mom: Optional[float] = None
    # PPI：生活资料：一般日用品类：环比
    ppi_cg_adu_mom: Optional[float] = None
    # PPI：生活资料：耐用消费品类：环比
    ppi_cg_dcg_mom: Optional[float] = None
    # PPI：全部工业品：累计同比
    ppi_accu: Optional[float] = None
    # PPI：生产资料：累计同比
    ppi_mp_accu: Optional[float] = None
    # PPI：生产资料：采掘业：累计同比
    ppi_mp_qm_accu: Optional[float] = None
    # PPI：生产资料：原料业：累计同比
    ppi_mp_rm_accu: Optional[float] = None
    # PPI：生产资料：加工业：累计同比
    ppi_mp_p_accu: Optional[float] = None
    # PPI：生活资料：累计同比
    ppi_cg_accu: Optional[float] = None
    # PPI：生活资料：食品类：累计同比
    ppi_cg_f_accu: Optional[float] = None
    # PPI：生活资料：衣着类：累计同比
    ppi_cg_c_accu: Optional[float] = None
    # PPI：生活资料：一般日用品类：累计同比
    ppi_cg_adu_accu: Optional[float] = None
    # PPI：生活资料：耐用消费品类：累计同比
    ppi_cg_dcg_accu: Optional[float] = None

    @field_validator('month')
    def validate_month(cls, value):
        """验证月份格式，应为'YYYYMM'格式，如'202301'"""
        if value is None or value == '':
            raise ValueError("月份不能为空")
        
        # 验证月份格式
        pattern = r"^\d{6}$"
        if not re.match(pattern, value):
            raise ValueError(f"无效的月份格式: {value}，正确格式应为'YYYYMM'，如'202301'")
        
        # 验证月份值
        year = int(value[:4])
        month = int(value[4:6])
        
        if year < 1900 or year > 2100:
            raise ValueError(f"无效的年份: {year}")
        
        if month < 1 or month > 12:
            raise ValueError(f"无效的月份: {month}")
        
        return value
    
    class Config:
        from_attributes = True