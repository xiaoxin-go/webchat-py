import redis
import pymysql

class Config:
    """配置信息"""
    SECRET_KEY = 'XHSOI*Y9dfs9cshd9'

    # 数据库配置
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root!@#$@127.0.0.1:3306/webchat'
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # redis配置
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379

    # flask-session配置
    SESSION_TYPE = 'redis'
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    SESSION_USE_SIGNER = True       # 对cookie中session_id进行隐藏处理
    PERMANENT_SESSION_LIFETIME = 86400      # session数据的有效期，单位秒


class DevelopmentConfig(Config):
    """开发模式的配置信息"""
    DEBUG = True

class ProductionConfig(Config):
    """生产环境配置信息"""
    pass

config_map = {
    'develop': DevelopmentConfig,
    'product': ProductionConfig
}