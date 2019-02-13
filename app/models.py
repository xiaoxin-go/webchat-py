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
    nickname = db.Column(db.String(32))             # 用户昵称
    password_hash = db.Column(db.String(128), nullable=False)       # 加密后的密码
    logo = db.Column(db.String(128))                # 用户头像
    state = db.Column(db.Integer, default=0)        # 用户状态，是否在线，在线为1
    is_admin = db.Column(db.Integer, default=0)     # 是否是管理员，默认为0

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


class Friends(BaseModel, db.Model):
    """  好友表 """

    __tablename__ = 't_friends'

    id = db.Column(db.Integer, primary_key=True)        # 好友表ID
    user_id = db.column(db.Integer, db.ForeignKey('t_user.id'))    # 用户ID
    friend_id = db.column(db.Integer, db.ForeignKey('t_user.id'))  # 好友ID
    remark = db.Column(db.String(32))   # 备注名称


class Group(BaseModel, db.Model):
    """ 群组表 """

    __tablename__ = 't_group'

    id = db.Column(db.Integer, primary_key=True)        # 群组ID
    group_name = db.Column(db.String(32))               # 群组名称


class GroupsToUser(BaseModel, db.Model):
    """  群组成员表 """

    __tablename__ = 't_groupuser'
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('t_group.id'), nullable=False)         # 群组ID，外键群组
    user_id = db.Column(db.Integer, db.ForeignKey('t_user.id'), nullable=False)           # 成员ID，外键用户
    remark = db.Column(db.String(32))                                      # 备注名称
    type = db.Column(db.Integer, default=2)                     # 成员类型，{0: 群主，1:管理员，2：普通成员}


class GroupsMsgContent(BaseModel, db.Model):
    """  群消息表 """

    __tablename__ = 't_groupsmsgcontent'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)        # 消息内容
    from_id = db.Column(db.Integer, db.ForeignKey('t_user.id'), nullable=False)     # 发送者ID
    from_name = db.Column(db.String(32), nullable=False)    # 发送者昵称

    def to_dict(self):
        msg_dict = {
            'id': self.id,
            'content': self.content,
            'from_id': self.from_id,
            'from_name': self.from_name
        }
        return msg_dict


class Messages(BaseModel, db.Model):
    """  聊天记录表 """

    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)        # 消息内容
    from_id = db.Column(db.Integer, db.ForeignKey('t_user.id'), nullable=False)   # 发送者ID
    to_id = db.Column(db.Integer, db.ForeignKey('t_user.id'), nullable=False)     # 接收者ID
    message_type = db.Column(db.String(32), default='text')     # 消息类型

    def to_dict(self):
        msg_dict = {
            'id': self.id,
            'content': self.content,
            'from_id': self.from_id,
            'to_id': self.to_id
        }
        return msg_dict
