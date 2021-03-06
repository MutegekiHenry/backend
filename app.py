import os

from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager

# import ORM
from flask_sqlalchemy import SQLAlchemy

# import kubernetes client
from kubernetes import client

# configure client
config = client.Configuration()
config.host = os.getenv('KUBE_HOST')
config.api_key['authorization'] = os.getenv('KUBE_TOKEN')
config.api_key_prefix['authorization'] = 'Bearer'
config.verify_ssl = False

# create API instance
kube = client.CoreV1Api(client.ApiClient(config))
extension_api = client.ExtensionsV1beta1Api(client.ApiClient(config))
appsv1_api = client.AppsV1Api(client.ApiClient(config))

# initialize sql-alchemy
db = SQLAlchemy()

# import blueprints
from routes.user import user_bp
from routes.admin import admin_bp
from routes.organisation_members import organisation_members_bp
from routes.organisation import organisation_bp
from routes.monitoring import monitor_bp
from routes.deployment import deployment_bp
from routes.namespaces import namespace_bp
#from routes.organisation import organisation_bp

def resource_not_found(e):
    response = jsonify(error=str(e))
    response.status_code = 404
    return response

def create_app(config_name):
    """ app factory """
    
    # import config options
    from config import app_config

    app = Flask(__name__)

    # allow cross-domain requests
    CORS(app)

    # use running config settings on app
    app.config.from_object(app_config[config_name])
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # register 404 error handler
    app.register_error_handler(404, resource_not_found)

    # register blueprints with the app
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(organisation_members_bp)
    app.register_blueprint(organisation_bp)
    app.register_blueprint(namespace_bp)
    app.register_blueprint(monitor_bp)
    app.register_blueprint(deployment_bp)
   # app.register_blueprint(organisation_bp)

    # register app with the db
    db.init_app(app)
    
    # initialize jwt with app
    JWTManager(app)
    
    return app

# create app instance using running config
app = create_app(os.getenv('FLASK_ENV'))

if __name__ == '__main__':
    app.run()
