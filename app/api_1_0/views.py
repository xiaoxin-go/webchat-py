from . import bp
from flask import request, jsonify, current_app, session, render_template, redirect, url_for
from flask_socketio import emit
from app import redis_store, socketio
from .chat import ChatHandler
from .user import UserHandler, UserInfoHandler
from .group import GroupHandler
from .group_user import GroupUserHandler
from .friend import FriendHandler
from .chat_message import ChatMessageHandler
from utils.restful import server_error, params_error, success, unauth_error
from utils.cut_image import CutImage
from app.models import *
from .libs.send_message import SendMessage

import time
import uuid
import json


@socketio.on('message')
def handle_json(request_data):
    # 获取发送的数据
    SendMessage(request_data)


@socketio.on('in_chat')
def in_chat():
    """
    用户进入聊天页面，将用户的id和sid绑定，为chat_sid_userid = sid
    :return:
    """
    print('---------------用户进入聊天页面---------------')
    print(session.get('nickname'), session.get('id'), request.sid)
    print('---------------end---------------')
    if not chat:
        return
    sid = request.sid
    user_id = session.get('id')
    sid_key = 'chat_sid_%s' % user_id
    redis_store.set(sid_key, sid, 3600*12)


@socketio.on('out_chat')
def out_chat():
    """
    用户退出聊天界面，删除用户的sid
    :return:
    """
    print('-----------------用户退出聊天页面----------------')
    print(session.get('nickname'), session.get('id'), request.sid)
    print('-----------------end-------------------')
    user_id = session.get('id')
    sid_key = 'chat_sid_%s' % user_id
    redis_store.delete(sid_key)


@bp.route('/user_info', methods=['GET'])
def user_info():
    user_handler = UserInfoHandler()
    return jsonify(user_handler.result)


@bp.route('/user', methods=['GET', 'POST', 'PUT', 'DELETE'])
def user():
    """  用户管理  """
    user_handler = UserHandler()
    return jsonify(user_handler.result)


@bp.route('/', methods=['GET'])
def index():
    if session.get('id'):
        return render_template('index.html')

    login_url = url_for('.login', _external=True)
    return redirect(login_url)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    用户登录
    用户名、 密码
    :return:
    """
    index_url = url_for('.index', _external=True)

    if session.get('id'):
        return redirect(index_url)

    if request.method == 'GET':
        return render_template('login.html', message='', success_message='')


    # 获取用户传输数据
    request_data = request.form
    username = request_data.get('username')
    password = request_data.get('password')

    if not all([username, password]):
        return render_template('login.html', message='缺少必要参数')

    # 获取用户登录IP
    user_ip = request.remote_addr
    try:
        access_nums = redis_store.get('access_num_%s' % user_ip)
    except Exception as e:
        current_app.logger.error(e)
    else:
        if access_nums and int(access_nums) >= 5:
            return render_template('login.html', message='错误次数过多，请稍后重试')

    # 从数据库查询用户对象
    try:
        user_obj = User.query.filter_by(username=username).first()
    except Exception as e:
        current_app.logger.error(e)
        return render_template('login.html', message='获取用户信息失败')

    # 取出用户密码与数据库密码对比
    if not user_obj or not user_obj.check_password(password):
        # 如果用户不存在或者用户密码不正确，返回错误消息，并记录错误次数
        try:
            # redis的incr可以对字符串类型数据进行加1操作，如果数据开始不存在，则默认设置为1
            redis_store.incr('access_num_%s' % user_ip)
            redis_store.expire('access_num_%s' % user_ip, 600)  # 数据保存600秒
        except Exception as e:
            current_app.logger.error(e)
        return render_template('login.html', message='用户名或密码错误')

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
        return render_template('login.html', message='登录异常')

    return redirect(index_url)


# @bp.route('/', methods=['GET'])
# def index():
#     #if session.get('id'):
#     return render_template('index.html')
#
#     #login_url = url_for('.login', _external=True)
#     #return redirect(login_url)


# @bp.route('/login', methods=['POST'])
# def login():
#     """
#     用户登录
#     用户名、 密码
#     :return:
#     """
#     #index_url = url_for('.index', _external=True)
#
#     #if session.get('id'):
#     #    return redirect(index_url)
#
#     #if request.method == 'GET':
#     #    return render_template('login.html')
#
#
#     # 获取用户传输数据
#     request_data = request.json
#     username = request_data.get('username')
#     password = request_data.get('password')
#
#     if not all([username, password]):
#         #return render_template('login.html', message='缺少必要参数')
#         return jsonify(params_error(message='缺少必要参数'))
#
#     # 获取用户登录IP
#     user_ip = request.remote_addr
#     try:
#         access_nums = redis_store.get('access_num_%s' % user_ip)
#     except Exception as e:
#         current_app.logger.error(e)
#     else:
#         if access_nums and int(access_nums) >= 5:
#             #return render_template('login.html', message='错误次数过多，请稍后重试')
#             return jsonify(unauth_error(message='错误次数过多，请稍后重试'))
#
#     # 从数据库查询用户对象
#     try:
#         user_obj = User.query.filter_by(username=username).first()
#     except Exception as e:
#         current_app.logger.error(e)
#         #return render_template('login.html', message='获取用户信息失败')
#         return jsonify(server_error(message = '获取用户信息失败'))
#
#     # 取出用户密码与数据库密码对比
#     if not user_obj or not user_obj.check_password(password):
#         # 如果用户不存在或者用户密码不正确，返回错误消息，并记录错误次数
#         try:
#             # redis的incr可以对字符串类型数据进行加1操作，如果数据开始不存在，则默认设置为1
#             redis_store.incr('access_num_%s' % user_ip)
#             redis_store.expire('access_num_%s' % user_ip, 600)  # 数据保存600秒
#         except Exception as e:
#             current_app.logger.error(e)
#         #return render_template('login.html', message='用户名或密码错误')
#         return jsonify(unauth_error(message='用户名或密码错误'))
#
#     # 登录成功
#     session['username'] = username
#     session['nickname'] = user_obj.nickname
#     session['id'] = user_obj.id
#
#     # 更改用户在线状态
#     user_obj.state = 1
#     try:
#         db.session.commit()
#     except Exception as e:
#         current_app.logger.error(e)
#         #return render_template('login.html', message='登录异常')
#         return jsonify(server_error('登录异常'))
#
#     #return redirect(index_url)
#     return jsonify(success(data=user_obj.to_dict(), message='用户登录成功'))


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
    return jsonify(success(data=user_obj.to_dict()))


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


@bp.route('/upload_image', methods=['POST'])
def upload_image():
    """   上传图片  """
    # 获取图片
    print('upload..................')
    file= request.files.get('file')
    print('file..',file)
    content_type = file.content_type
    if content_type != 'image/jpeg':
        return jsonify(params_error(message='文件类型不正确'))
    # 生成图片名称
    image_name = str(uuid.uuid1()) + '.' + file.filename.split('.')[-1]
    image_path = '/static/images/%s' % image_name
    try:
        with open('app' + image_path, 'wb') as f:
            f.write(file.read())
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(server_error(message='上传失败'))

    # ci = CutImage('app' + image_path, 'app' + image_path)
    # ci.cut()

    return jsonify(success(data={'url': image_path}))


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
