from flask import Blueprint

# 创建蓝图对象
bp = Blueprint('', __name__)

# 导入蓝图的视图
from . import views