from functools import wraps
from fastapi import HTTPException
from .error_code import ErrorCode
from pydantic import BaseModel, Field
from typing import Optional, Any, Union


class ResponseModel(BaseModel):
    """通用响应模型"""
    code: int = Field(200, description="响应状态码")
    success: bool = Field(True, description="是否成功")
    message: str = Field("操作成功", description="响应消息")
    data: Optional[Any] = Field(None, description="响应数据")

    @classmethod
    def success(cls, data: Optional[Any] = None, message: str = "操作成功"):
        """成功响应"""
        return cls(code=ErrorCode.SUCCESS.code, success=True, message=message, data=data)
    
    @classmethod
    def error(cls, error_code: Union[ErrorCode, int], message: Optional[str] = None, data: Optional[Any] = None):
        """错误响应"""
        if isinstance(error_code, ErrorCode):
            code = error_code.code
            default_message = error_code.message
        else:
            code = error_code
            default_message = "未知错误"
        
        return cls(
            code=code, 
            success=False, 
            message=message or default_message, 
            data=data
        )


def handle_exception(exc: Exception, default_error_code: ErrorCode = ErrorCode.INTERNAL_SERVER_ERROR) -> ResponseModel:
    """
    统一异常处理函数
    
    Args:
        exc: 捕获的异常
        default_error_code: 默认错误码
    
    Returns:
        ResponseModel: 格式化的错误响应
    """
    # 可以根据不同异常类型返回不同错误码
    if isinstance(exc, ValueError):
        return ResponseModel.error(ErrorCode.INVALID_PARAMETER, str(exc))
    elif isinstance(exc, TypeError):
        return ResponseModel.error(ErrorCode.BAD_REQUEST, str(exc))
    else:
        return ResponseModel.error(default_error_code, str(exc))


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