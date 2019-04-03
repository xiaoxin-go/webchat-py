from flask import request, current_app, session, render_template, redirect
from app import redis_store, db
from app.models import User
from utils.restful import params_error, success, unauth_error
from .common import BaseHandler


class LoginHandler:
    def __init__(self, index_url):
        self.index_url = index_url

    def get_(self):
        return render_template('login.html', message='', success_message='')

    def post_(self):
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

        return redirect(self.index_url)


class LogoutHandler(BaseHandler):
    def add_(self):
        user_obj = self.check_user()
        if not user_obj:
            return
        user_obj.state = 0
        if not self.commit():
            return
        session.clear()  # 清除用户session
        self.result = success()