from . import bp
from flask import request, jsonify, current_app, session
from app import redis_store, db
from app.models import User
from sqlalchemy.exc import IntegrityError

@bp.route('/user', methods=['POST'])
def register():
    """
    用户注册
    请求参数： 用户名， 密码
    :return:
    """
    request_data = request.json

    username = request_data.get('username')
    password = request_data.get('password')
    nickname = request_data.get('nickname')

    # 检查用户名和密码是否存在
    if not all([username, password]):
        return jsonify({'state': 2, 'message': '缺少必要参数'})

    # 添加用户
    user = User(username=username, nickname=nickname)

    # 设置密码
    user.password = password        # 已自动加密

    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError as e:
        # 数据库操作错误后的回滚
        db.session.rollback()
        # 此错误信息表示用户被注册过
        current_app.logger.error(e)
        return jsonify({'state': 2, 'message': '用户已存在'})
    except Exception as e:
        db.session.rollback()
        # 数据库操作异常
        current_app.logger.error(e)
        return jsonify({'state': 2, 'message': '添加用户异常'})

    # 注册成功
    return jsonify({'state': 1, 'message': '注册成功'})

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
        return jsonify({'state': 2, 'message': '缺少必要参数'})

    # 获取用户登录IP
    user_ip = request.remote_addr
    try:
        access_nums = redis_store.get('access_num_%s' % user_ip)
    except Exception as e:
        current_app.logger.error(e)
    else:
        if access_nums and int(access_nums) >= 5:
            return jsonify({'state': 2, 'message': '错误次数过多，请稍后重试'})

    # 从数据库查询用户对象
    try:
        user = User.query.filter_by(username=username).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify({'state': 2, 'message': '获取用户信息失败'})

    # 取出用户密码与数据库密码对比
    if not user or not user.check_password(password):
        # 如果用户不存在或者用户密码不正确，返回错误消息，并记录错误次数
        try:
            # redis的incr可以对字符串类型数据进行加1操作，如果数据开始不存在，则默认设置为1
            redis_store.incr('access_num_%s' % user_ip)
            redis_store.expire('access_num_%s' % user_ip, 600)  # 数据保存600秒
        except Exception as e:
            current_app.logger.error(e)

        return jsonify({'state': 2, 'message': '用户名或密码错误'})

    # 登录成功
    session['username'] = username
    session['nickname'] = user.nickname
    session['id'] = user.id

    return jsonify({'state': 1, 'message': '登录成功'})