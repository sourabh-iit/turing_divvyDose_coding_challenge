from flask import Flask
import flask

import logging
from logging.handlers import RotatingFileHandler

def create_app(config_filename):
  app = Flask(__name__)
  app.config.from_object(config_filename)

  from app.routes import api_bp
  app.register_blueprint(api_bp, url_prefix='/api')

  return app

if __name__=='__main__':
  app = create_app('config')
  handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=1)
  app.logger.addHandler(handler)
  app.run(debug=True)