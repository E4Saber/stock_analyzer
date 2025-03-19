from datetime import datetime, timedelta

def get_yesterday_yyyymmdd():
    """
    获取昨天的日期字符串，格式为YYYYMMDD
    """
    return (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')