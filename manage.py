from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_cors import *
from app import create_app, db


# 创建flask的应用对象
app = create_app('develop')
# 允许跨域访问
CORS(app, supports_credentials=True)
manager = Manager(app)
Migrate(app, db)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()