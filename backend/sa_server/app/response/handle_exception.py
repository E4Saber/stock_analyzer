from functools import wraps
from fastapi import HTTPException
from .response_model import handle_exception


def api_exception_handler(func):
    """API异常处理装饰器"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            # 可以在这里添加日志记录
            response = handle_exception(e)
            raise HTTPException(
                status_code=response.code, 
                detail=response.model_dump()
            )
    return wrapper