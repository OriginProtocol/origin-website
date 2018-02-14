from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from app import app, app_config
from database import db

app_config.init_prod_app(app)

migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
