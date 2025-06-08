from flask import Flask
from memory_profiler import profile
from database.db import close_db

def close_db_at_end(e=None):
    close_db(e)

@profile
def create_app():
	app = Flask(__name__)

	from .routes import bp
	app.register_blueprint(bp)

	app.teardown_appcontext(close_db_at_end)

	return app

