import datetime
from typing import Optional
from pydantic import BaseModel
from pydantic import field_validator


class StockCompanyData(BaseModel):
    """
    Pydantic model for stock company data.
    
    Fields:
    - ts_code: Stock code
    - com_name: Company full name
    - com_id: Unified social credit code
    - exchange: Exchange code
    - chairman: Legal representative
    - manager: General manager
    - secretary: Board secretary
    - reg_capital: Registered capital (10,000 yuan)
    - setup_date: Registration date
    - province: Province
    - city: City
    - introduction: Company introduction
    - website: Company website
    - email: Email
    - office: Office
    - employees: Number of employees
    - main_business: Main business and products
    - business_scope: Business scope
    """
    # 股票代码，主键
    ts_code: str
    # 公司全称
    com_name: str
    # 统一社会信用代码，非必须字段
    com_id: Optional[str] = None
    # 交易所代码，非必须字段
    exchange: Optional[str] = None
    # 法人代表，非必须字段
    chairman: Optional[str] = None
    # 总经理，非必须字段
    manager: Optional[str] = None
    # 董秘，非必须字段
    secretary: Optional[str] = None
    # 注册资本(万元)，非必须字段
    reg_capital: Optional[float] = None
    # 注册日期，非必须字段
    setup_date: Optional[datetime.date] = None
    # 所在省份，非必须字段
    province: Optional[str] = None
    # 所在城市，非必须字段
    city: Optional[str] = None
    # 公司介绍，非必须字段
    introduction: Optional[str] = None
    # 公司主页，非必须字段
    website: Optional[str] = None
    # 电子邮件，非必须字段
    email: Optional[str] = None
    # 办公室，非必须字段
    office: Optional[str] = None
    # 员工人数，非必须字段
    employees: Optional[int] = None
    # 主要业务及产品，非必须字段
    main_business: Optional[str] = None
    # 经营范围，非必须字段
    business_scope: Optional[str] = None

    @field_validator('setup_date', mode='before')
    def parse_date(cls, value):
        if value is None or value == '':
            return None
        
        if isinstance(value, datetime.date):
            return value
        
        try:
            # 假设日期格式为 'YYYYMMDD'
            if isinstance(value, str) and value.isdigit() and len(value) == 8:
                year = int(value[:4])
                month = int(value[4:6])
                day = int(value[6:8])
                return datetime.date(year, month, day)
            # 其他常见格式
            return datetime.date.fromisoformat(value)
        except (ValueError, TypeError):
            raise ValueError(f"无效的日期格式: {value}")
    
    @field_validator('employees')
    def validate_employees(cls, value):
        if value is not None and value < 0:
            raise ValueError("员工人数不能为负数")
        return value
    
    class Config:
        from_attributes = True