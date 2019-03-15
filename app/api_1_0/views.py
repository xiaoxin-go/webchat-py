from . import bp
from flask import request, jsonify, current_app, session, render_template
from flask_socketio import emit
from app import redis_store, socketio
from threading import Lock
from .chat import ChatHandler
from .user import UserHandler
from .group import GroupHandler
from .group_user import GroupUserHandler
from .friend import FriendHandler
from utils.restful import server_error, params_error, success, unauth_error
from utils.cut_image import CutImage
from app.models import *

import uuid


thread = None
thread_lock = Lock()
logined_userid = []


def ack(value):
    print(value)


@socketio.on('send_message')
def handle_json(msg):
    user = User.query.get(msg.get('send_id'))
    if user:
        return_msg = {
            'username': user.username,
            'msg': msg['data'],
            'cerate_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        emit('recive_msg', return_msg, broadcast=True, callback=ack)


@socketio.on('newLogin')
def newLogin(username):
    user = User.query.filter_by(username=username).first()
    if user.id not in logined_userid:
        logined_userid.append(user.id)
        emit('newLogin_return', username, broadcast=True)
    return 'success'


@socketio.on('newLogout')
def newLogout(user_id):
    user = User.query.get(user_id)
    emit('newLogout_return', user.username, broadcast=True)
    return 'success'

# def background_thread(users_to_json):
#     while True:
#         print(users_to_json)
#         users_to_json = [{'name': 'test' + str(random.randint(1,100))}]
#         socketio.sleep(0.5)
#         socketio.emit('user_response', {'data': users_to_json}, namespace='/websocket/user_refresh')
#
#
# @socketio.on('content', namespace='/websocket/user_refresh')
# def connect():
#     """  服务端自动发送通信请求 """
#     global thread
#     users_to_json = ''
#     with thread_lock:
#         if thread is None:
#             thread = socketio.start_background_task(background_thread, (users_to_json,))
#     print('.......')
#     emit('server_response', {'data': '试图连接客户端'})
#
#
# @socketio.on('connect_event', namespace='/websocket/user_refresh')
# def refresh_message(message):
#     """  服务端接受客户端发送的通信请求 """
#     print('message:',message)
#     emit('server_response', {'data': message['data']})


@socketio.on('request_for_response', namespace='/testnamespace')
def give_response(data):
    value = data.get('param')
    emit('response', {'code': '200', 'msg': 'start to process...'})

    emit('response', {'code': '200', 'msg': 'processed'})


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

    return jsonify(success(data=user_obj.to_dict, message='用户登录成功'))


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


@bp.route('/upload_logo', methods=['POST'])
def upload_logo():
    """   上传头像  """
    # 获取图片
    file= request.files.get('file')
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




# @socketio.on('message')
# def handle_message(message):
#     print('received message: ' + message)
#
#
# @socketio.on('json')
# def handle_json(json):
#     """  接收json字符串 """
#     print('received json: ' + str(json))
#
#
# @socketio.on('my event')
# def handle_my_custom_event(json):
#     """  自定义命名事件 """
#     print('received json:' + str(json))
#
#
# @socketio.on('my event')
# def handle_my_custom_event(arg1, arg2, arg3):
#     """  自定义命名事件接收多个参数 """
#     print('received args: ' + arg1 + arg2 + arg3)
#
#
# @socketio.on('my event', namespace='/test')
# def handle_my_custom_namespace_event(json):
#     print('received json: ' + str(json))
#
#
# socketio.on_event('my event', handle_my_custom_event, namespace='/test')
