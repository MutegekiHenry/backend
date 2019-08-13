import requests, os

from flask import request, jsonify, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity

# registry authentication
basic_auth_header = requests.auth.HTTPBasicAuth(
    os.getenv("HARBOR_USERNAME"), os.getenv("HARBOR_PASSWORD")
)

# registry base url
base_url = os.getenv("HARBOR_BASE_URL")

# registry blueprint
registry_bp = Blueprint("registry", __name__)


@registry_bp.route("/registries", methods=["POST"])
def create_new_registry_account():
    """ create new registry account """

    payload = {
        "email": request.get_json()["email"],
        "password": request.get_json()["password"],
        "username": request.get_json()["username"],
        "realname": request.get_json()["realname"],
    }

    res = requests.post(base_url + "/users", json=payload, auth=basic_auth_header)

    response = jsonify({"msg": res.text})
    response.status_code = res.status_code

    return response
