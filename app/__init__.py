from flask import Flask
from memory_profiler import profile

@profile
def create_app():
	app = Flask(__name__)

	from .routes import bp
	app.register_blueprint(bp)

	return app