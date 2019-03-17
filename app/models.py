from datetime import datetime
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
import copy


class BaseModel:
    """  模型基类，为每个模型补充创建时间与更新时间  """

    create_time = db.Column(db.DateTime, default=datetime.now())  # 记录创建时间
    update_time = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())  # 记录更新时间

    def to_json(self):
        data = copy.deepcopy(self.__dict__)
        if '_sa_instance_state' in data:
            del data['_sa_instance_state']

        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.strftime('%Y-%m-%d %H:%M:%S')

        return data


class User(BaseModel, db.Model):
    """ 用户表 """

    __tablename__ = 't_user'

    id = db.Column(db.Integer, primary_key=True)    # 用户ID
    username = db.Column(db.String(200), unique=True, nullable=False)    # 用户名
    nickname = db.Column(db.String(200), nullable=False)             # 用户昵称
    password_hash = db.Column(db.String(128), nullable=False)       # 加密后的密码
    logo = db.Column(db.String(128))                # 用户头像
    state = db.Column(db.Integer, default=0)        # 用户状态，是否在线，在线为1
    type = db.Column(db.Integer, default=2)     # 用户类型， {0: 站长，1：副站长， 2：用户}

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
            'create_time': self.create_time,
            'type': self.type
        }
        return user_dict


class Friends(BaseModel, db.Model):
    """  好友表 """

    __tablename__ = 't_friends'

    id = db.Column(db.Integer, primary_key=True)        # 好友表ID
    user_id = db.Column(db.Integer)
    friend_id = db.Column(db.Integer)
    remark = db.Column(db.String(1000))         # 备注名称


class Group(BaseModel, db.Model):
    """ 群组表 """

    __tablename__ = 't_group'

    id = db.Column(db.Integer, primary_key=True)                # 群组ID
    name = db.Column(db.String(200), nullable=False)       # 群组名称
    logo = db.Column(db.String(200), nullable=False)             # 群头像
    group_info = db.Column(db.TEXT)                             # 群公告


class GroupsToUser(BaseModel, db.Model):
    """  群组成员表 """

    __tablename__ = 't_groupuser'
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, nullable=False)         # 群组ID，外键群组
    user_id = db.Column(db.Integer, nullable=False)           # 成员ID，外键用户
    remark = db.Column(db.String(200))                                      # 备注名称
    type = db.Column(db.Integer, default=2)                     # 成员类型，{0: 群主，1:管理员，2：普通成员}


class Chat(BaseModel, db.Model):
    """  聊天列表 """

    __tablename__ = 't_chat'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)                 # 用户ID
    name = db.Column(db.String(200))                # 聊天名称
    type = db.Column(db.Integer)                 # 聊天类型, 1为单聊，2为群聊
    logo = db.Column(db.String(200))                # 聊天头像
    chat_obj_id = db.Column(db.Integer)             # 聊天对象ID
    message = db.Column(db.Text)                    # 聊天最后一条消息
    update_time = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())  # 记录更新时间
    __mapper_args__ = {
        "order_by": update_time.desc()
    }


class ChatMessage(BaseModel, db.Model):
    """  好友聊天消息表 """

    __tablename__ = 't_chatmessage'
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer)                 # 聊天ID
    message = db.Column(db.Text)                    # 消息内容
    user_id = db.Column(db.Integer, nullable=False)     # 发送者



