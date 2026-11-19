import os
import logging
from flask import Flask, jsonify
from hubmap_commons.hm_auth import AuthHelper

from routes.spatialquery.spatialquery import spatialquery_blueprint

# Specify the absolute path of the instance folder and load the config relative to it
app = Flask(__name__,
            instance_path=os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance'),
            instance_relative_config=True)
app.config.from_pyfile('app.cfg')

logging.basicConfig(format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
                    level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger()

# JSON error handlers
@app.errorhandler(400)
def http_bad_request(e):
    return jsonify(error=str(e)), 400

@app.errorhandler(401)
def http_unauthorized(e):
    return jsonify(error=str(e)), 401

@app.errorhandler(403)
def http_forbidden(e):
    return jsonify(error=str(e)), 403

@app.errorhandler(404)
def http_not_found(e):
    return jsonify(error=str(e)), 404

@app.errorhandler(500)
def http_internal_server_error(e):
    return jsonify(error=str(e)), 500

@app.errorhandler(502)
def http_bad_gateway(e):
    return jsonify(error=str(e)), 502

# Initialize AuthHelper class and ensure singleton
try:
    if not AuthHelper.isInitialized():
        auth_helper_instance = AuthHelper.create(app.config['APP_CLIENT_ID'],
                                                 app.config['APP_CLIENT_SECRET'])
        logger.info('Initialized auth_helper_instance successfully')
    else:
        auth_helper_instance = AuthHelper.instance()
except Exception:
    logger.exception('Failed to initialize the auth_helper_instance')
    raise

app.register_blueprint(spatialquery_blueprint)

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000)