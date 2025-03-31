from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # 应用名称
    APP_NAME: str = "Stock Analysis Platform"
    # 数据库配置
    DATABASE_URL: str
    
    # 应用配置
    DEBUG: bool = False

    # tushare token
    tushare_token: str
    
    # SQL日志配置
    ENABLE_SQL_LOG: bool = False
    SQL_LOG_LEVEL: str = "INFO"

    # 允许额外字段
    model_config = SettingsConfigDict(
        extra='allow',  # 允许额外字段
        env_file=".env",
        env_file_encoding="utf-8"
    )

# 创建全局配置实例
settings = Settings()