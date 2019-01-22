from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from app import create_app, db

# 创建flask的应用对象
app = create_app('develop')

manager = Manager(app)
Migrate(app, db)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()