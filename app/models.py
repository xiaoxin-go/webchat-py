from datetime import datetime
from . import db
from werkzeug.security import generate_password_hash, check_password_hash

class BaseModel:
    """  模型基类，为每个模型补充创建时间与更新时间  """

    create_time = db.Column(db.DateTime, default=datetime.now)  # 记录创建时间
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)  # 记录更新时间


class User(BaseModel, db.Model):
    """ 用户表 """

    __tablename__ = 't_user'

    id = db.Column(db.Integer, primary_key=True)    # 用户ID
    username = db.Column(db.String(32), unique=True, nullable=False)    # 用户名
    nickname = db.Column(db.String(32))      # 用户昵称
    password_hash = db.Column(db.String(128), nullable=False)       # 加密后的密码
    logo = db.Column(db.String(128))        # 用户头像

    @property
    def password(self):
        """读取属性的函数行为"""
        return AttributeError('这个属性只能设置，不能读取')

    # 使用这个装饰器，对应设置属性操作
    @password.setter
    def password(self, value):
        """
        设置属性    user.password
        :param value:  str  设置的明文密码
        :return:
        """
        # 对明文密码进行加密
        self.password_hash = generate_password_hash(value)

    # 检查密码
    def check_password(self, passwd):
        """
        检验密码的正确性
        :param passwd: 用户登录时填写的原始密码
        :return:    如果正确，返回True, 否则返回False
        """
        return check_password_hash(self.password_hash, passwd)

    def to_dict(self):
        """ 将用户数据转换为字典 """
        user_dict = {
            'id': self.id,
            'username': self.username,
            'nickname': self.nickname,
            'logo': self.logo,
            'create_time': self.create_time
        }
        return user_dict