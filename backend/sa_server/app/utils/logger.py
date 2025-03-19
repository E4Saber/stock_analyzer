from loguru import logger

#
# rotation: 日志轮转（即日志文件的自动切割）触发条件。可按时间、大小或自定义条件
# retention: 日志保留时间，超时自动清理
logger.add("logs/daily_task.log", rotation="1 day", retention="7 days", level="INFO")
