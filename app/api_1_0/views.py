from . import bp
from flask import request, jsonify, current_app, session, render_template
from flask_socketio import emit
from app import redis_store, socketio
from .chat import ChatHandler
from .user import UserHandler
from .group import GroupHandler
from .group_user import GroupUserHandler
from .friend import FriendHandler
from .chat_message import ChatMessageHandler
from utils.restful import server_error, params_error, success, unauth_error
from utils.cut_image import CutImage
from app.models import *
from .common import now

import time
import uuid
import json


def ack(value):
    print(value)


@socketio.on('message')
def handle_json(request_data):
    # 获取发送的数据
    user_data = request_data.get('user_data')
    chat_id = request_data.get('chat_id')
    message = request_data.get('message')
    print(request_data)
    # 获取聊天信息，并将发送的数据保存到redis中，并更新聊天信息
    user_data['message'] = message
    user_data['add_time'] = now()
    chat_obj = Chat.query.get(chat_id)
    print('chat_obj.type',chat_obj.type)
    chat_key = 'chat_%s_%s' % (chat_id, now())
    redis_store.set(chat_key, user_data, 3600*24)
    chat_obj.message = message
    db.session.commit()

    # 发送消息，获取聊天类型，如果是1，则是单聊
    # 获取聊天对象ID，获取此聊天的sid，向此用户发送消息
    chat_obj_id = chat_obj.chat_obj_id
    if chat_obj.type == 1:
        print('------chat_obj.type')
        chat_key = 'chat_sid_%s' % chat_obj_id
        chat_sid = redis_store.get(chat_key)
        print(chat_key, chat_sid)
        if chat_sid:
            print(json.dumps(user_data))
            emit('message', user_data, room=chat_sid.decode())
            #emit('message', user_data, room=request.sid)

        chat_list_key = 'chat_list_sid_%s' % chat_obj_id
        chat_list_sid = redis_store.get(chat_list_key)
        if chat_list_sid:
            emit('message', chat_obj.to_json(), room=chat_list_sid.decode())

    # 否则为群组聊天，获取聊天对象ID
    else:
        group_user_query = GroupsToUser.query.filter_by(group_id=chat_obj_id)
        for group_user in group_user_query:
            if group_user.user_id == user_data.id:
                continue
            chat_key = 'chat_sid_%s' % group_user.user_id
            chat_sid = redis_store.get(chat_key)
            print('chat_key', chat_key, chat_sid)
            if chat_sid:
                emit('message', user_data, room=chat_sid.decode())

            chat_list_key = 'chat_list_sid_%s' % group_user.user_id

            chat_list_sid = redis_store.get(chat_list_key)
            print('chat_list_key', chat_list_key, chat_list_sid)
            if chat_list_sid:
                emit('message', chat_obj.to_json(), room=chat_list_sid.decode())

    print('message.............test')
    print(request.sid)
    # emit('message', 'test', room=request.sid, callback=ack)


@socketio.on('in_chat')
def in_chat(chat_id):
    """
    用户进入聊天页面，将用户的id和sid绑定，为chat_chatid_sid_userid = sid
    :return:
    """
    sid = request.sid
    user_id = session.get('id')
    chat_key = 'chat_sid_%s' % user_id
    print('进入聊天页面', chat_key, sid)
    redis_store.set(chat_key, sid)
    #emit('message', 'test', room=request.sid, callback=ack)


@socketio.on('out_chat')
def out_chat(chat_id):
    """
    用户退出聊天界面，删除用户的sid
    :return:
    """
    user_id = session.get('id')
    chat_key = 'chat_sid_%s' % user_id
    redis_store.delete(chat_key)
    #emit('message', 'test', room=request.sid, callback=ack)


@socketio.on('in_chat_list')
def in_chat_list():
    """
    用户进入聊天列表，将用户的id和sid绑定，为chat_list_sid_userid = sid
    :return:
    """
    sid = request.sid
    user_id = session.get('id')
    chat_key = 'chat_list_sid_%s' % user_id
    redis_store.set(chat_key, sid)
    #emit('message', 'test', room=request.sid, callback=ack)


@socketio.on('out_chat_list')
def out_chat_list():
    """
    退出聊天列表，清除用户sid
    :return:
    """
    user_id = session.get('id')
    chat_key = 'chat_list_sid_%s' % user_id
    redis_store.delete(chat_key)
    #emit('message', 'test', room=request.sid, callback=ack)



@bp.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@bp.route('/user_info', methods=['GET'])
def user_info():
    user_handler = UserHandler()
    return jsonify(user_handler.user_info())


@bp.route('/user', methods=['GET', 'POST', 'PUT', 'DELETE'])
def user():
    """  用户管理  """
    user_handler = UserHandler()
    return jsonify(user_handler.result)


@bp.route('/login', methods=['POST'])
def login():
    """
    用户登录
    用户名、 密码
    :return:
    """

    # 获取用户传输数据
    request_data = request.json
    username = request_data.get('username')
    password = request_data.get('password')

    if not all([username, password]):
        return jsonify(params_error(message='缺少必要参数'))

    # 获取用户登录IP
    user_ip = request.remote_addr
    try:
        access_nums = redis_store.get('access_num_%s' % user_ip)
    except Exception as e:
        current_app.logger.error(e)
    else:
        if access_nums and int(access_nums) >= 5:
            return jsonify(unauth_error(message='错误次数过多，请稍后重试'))

    # 从数据库查询用户对象
    try:
        user_obj = User.query.filter_by(username=username).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(server_error(message = '获取用户信息失败'))

    # 取出用户密码与数据库密码对比
    if not user_obj or not user_obj.check_password(password):
        # 如果用户不存在或者用户密码不正确，返回错误消息，并记录错误次数
        try:
            # redis的incr可以对字符串类型数据进行加1操作，如果数据开始不存在，则默认设置为1
            redis_store.incr('access_num_%s' % user_ip)
            redis_store.expire('access_num_%s' % user_ip, 600)  # 数据保存600秒
        except Exception as e:
            current_app.logger.error(e)

        return jsonify(unauth_error(message='用户名或密码错误'))

    # 登录成功
    session['username'] = username
    session['nickname'] = user_obj.nickname
    session['id'] = user_obj.id

    # 更改用户在线状态
    user_obj.state = 1
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(server_error('登录异常'))

    return jsonify(success(data=user_obj.to_dict(), message='用户登录成功'))


@bp.route('/check_login', methods=['GET'])
def check_login():
    """
    检查用户是否登录
    :return:
    """
    user_id = session.get('id')
    if not user_id:
        return jsonify(unauth_error(message='用户未登录'))

    user_obj = User.query.filter_by(id=user_id).first()
    if not user_obj:
        return jsonify(unauth_error(message='用户不存在'))

    # 返回已登录状态，和用户数据
    return jsonify(success(data=user_obj.to_dict))


@bp.route('/logout', methods=['POST'])
def logout():
    """ 用户退出登录 """
    id = session.get('id')
    try:
        user_obj = User.query.get(id)
        user_obj.state = 0
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
    session.clear()     # 清除用户session
    return jsonify(success())


@bp.route('/group', methods=['GET', 'POST', 'PUT', 'DELETE'])
def group():
    """  群组管理 """
    group_handler = GroupHandler()
    return jsonify(group_handler.result)


@bp.route('/group_user', methods=['GET','POST', 'PUT', 'DELETE'])
def group_user():
    """  群组成员管理 """
    group_user_handler = GroupUserHandler()
    return jsonify(group_user_handler.result)


@bp.route('/friend', methods=['GET', 'POST', 'PUT', 'DELETE'])
def friend():
    """  好友管理 """
    friend_handler = FriendHandler()
    return jsonify(friend_handler.result)


@bp.route('/chat', methods=['GET', 'POST', 'DELETE'])
def chat():
    """ 聊天列表管理 """
    chat_handler = ChatHandler()
    return jsonify(chat_handler.result)


@bp.route('/chat_message', methods=['GET', 'POST'])
def chat_message():
    chat_message_handler = ChatMessageHandler()
    return jsonify(chat_message_handler.result)


@bp.route('/upload_logo', methods=['POST'])
def upload_logo():
    """   上传头像  """
    # 获取图片
    print('upload..................')
    file= request.files.get('file')
    print('file..',file)
    content_type = file.content_type
    if content_type != 'image/jpeg':
        return jsonify(params_error(message='文件类型不正确'))
    # 生成图片名称
    image_name = str(uuid.uuid1()) + '.' + file.filename.split('.')[-1]
    image_path = '/static/logo/%s' % image_name
    try:
        with open('app' + image_path, 'wb') as f:
            f.write(file.read())
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(server_error(message='上传失败'))

    ci = CutImage('app' + image_path, 'app' + image_path)
    ci.cut()

    return jsonify(success(data={'url': image_path}))
