from enum import Enum


class ErrorCode(Enum):
    """统一错误码枚举"""
    # 成功
    SUCCESS = 200, "操作成功"
    
    # 通用客户端错误
    BAD_REQUEST = 400, "请求错误"
    UNAUTHORIZED = 401, "未授权"
    FORBIDDEN = 403, "禁止访问"
    NOT_FOUND = 404, "资源未找到"
    
    # 服务器错误
    INTERNAL_SERVER_ERROR = 500, "服务器内部错误"
    DATABASE_ERROR = 501, "数据库操作失败"
    EXTERNAL_API_ERROR = 502, "外部API调用失败"
    
    # 业务相关错误
    DATA_NOT_EXISTS = 1001, "数据不存在"
    INVALID_PARAMETER = 1002, "参数校验失败"
    DUPLICATE_RECORD = 1003, "记录重复"
    
    def __new__(cls, code: int, message: str):
        obj = object.__new__(cls)
        obj._value_ = code
        obj.message = message
        return obj

    @property
    def code(self) -> int:
        return self.value