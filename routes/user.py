from flask import request, jsonify, Blueprint, render_template, url_for
import json
import sys
from flask_jwt_extended import (
    JWTManager,
    jwt_required,
    create_access_token,
    get_jwt_identity,
)
from flask_bcrypt import Bcrypt
from models.user import User
from models.organisation_members import *
from models.organisation import *
from routes.organisation import register_organisation, get_organisations
from routes.organisation_members import *

from helpers.token import generate_token, validate_token
from helpers.email import send_email
# from app import food
# user blueprint
user_bp = Blueprint("user", __name__)

#  User registration
@user_bp.route("/")
def hello():
    gat = sys.path
    response = jsonify({
        "path": gat
        # "food": food
    })
    return response

@user_bp.route("/register", methods=["POST"])
def register():
    """ create new user """

    email = request.get_json()["email"]
    name = request.get_json()["name"]
    password = request.get_json()["password"]

    # validate input
    if str(email).strip() and str(password).strip():
        user = User(email, name, password)
        user.save()

        # send verification token
        token = generate_token(user.email)
        verify_url = url_for("user.verify_email", token=token, _external=True)
        html = render_template("user/verify.html", verify_url=verify_url)
        # html = render_template("user/verify.html")
        subject = "Please confirm your email"
        send_email(user.email, subject, html)

        response = jsonify(
            {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "password": user.password,
                "date_created": user.date_created,
            }
        )

        response.status_code = 201

        return response
    else:
        response = jsonify({"message": "Register failure, wrong information"})
        response.status_code = 401
        return response

# User Login
@user_bp.route("/login", methods=["POST"])
def login():
    """ user login """

    email = request.get_json()["email"]
    password = request.get_json()["password"]

    # validate input
    if str(email).strip() and str(password).strip():
        user = User.query.filter_by(email=email).first()

        if user and user.password_is_valid(password):
            """ right credentials """

            # generate access token
            access_token = user.generate_token(user.id)
            if access_token:
                response = jsonify(
                    {"access_token": access_token, "message": "login success"}
                )

                response.status_code = 200

                return response
            else:
                response = jsonify({"message": "Unable to generate token"})
                response.status_code = 401
                return response
        else:
            """ wrong credentials """

            response = jsonify({"message": "login failure"})

            response.status_code = 401

            return response
    else:
        response = jsonify({"message": "Login failure, wrong information"})
        response.status_code = 401
        return response

@user_bp.route('/confirm/<token>')
def verify_email(token):

    try:
        email = validate_token(token)
    except:
        response = jsonify({"message": 'The confirmation link is invalid or has expired.'})
        response.status_code = 401
        return response

    user = User.query.filter_by(email=email).first()

    if user.verified:
        response = jsonify({"message": 'Account already confirmed. Please login.'})
        response.status_code = 409
        return response

    user.verified = True
    db.session.commit()
    response = jsonify({"message": "You've confirmed your account. Thanks!"})
    response.status_code = 200

    return response


# Delete User account
@user_bp.route('/delete/user', methods=['DELETE'])
def delete_user_account():
    email = request.get_json()['email']
    user = User.query.filter_by(email = email).first()

    if user is not None:
        user.delete()
        response = jsonify({
            'message': 'Successfully deleted'
        })
        response.status_code = 201
        return response 
    else:
        response = jsonify({
            'message': 'User does not exist'
        })
        response.status_code = 401
        return response 

# Creating an Organisation
@user_bp.route('/create/organisation', methods=['POST'])
@jwt_required
def create_organisation():
    current_user = get_jwt_identity()
    org_name = request.get_json()['organisation_name']
    if(current_user is not None):
        """ Register the organisation """

        organisation_resp = register_organisation(org_name)
        
        if(organisation_resp['status_code'] == 201):
            """ Register them into the association table """
            response = register_organisation_member(current_user, organisation_resp['id'], True)
            return organisation_resp, 201
        else:
            response = jsonify({
                'message': 'Organisation failure'
            })
            response.status_code = 401
            return response
    else:
        response = jsonify({
                'message': 'Current user not authorised'
        })
        response.status_code = 401
        return response


# Adding a member to an organisation
@user_bp.route('/add/member', methods=['POST'])
@jwt_required
def add_member():
    current_user_id = get_jwt_identity()
    email = request.get_json()['email']
    organisation_name = request.get_json()['organisation_name']
    current_user = OrganisationMembers.query.filter_by(user_id = current_user_id).first()
    
    # check if current user in an admin
    if current_user.is_admin is True:
        user = User.query.filter_by(email=email).first()
        organisation = Organisation.query.filter_by(name=organisation_name).first()
        if user and organisation:
            response = register_organisation_member(user.id, organisation.id, False)
            return response
        else:
            response = jsonify({
                'message': 'User or Organisation does not exist'
            })
            response.status_code = 401
            return response 
    else:
        response = jsonify({
            'message': 'User is not an Admin'
        })
        response.status_code = 401
        return response 

# Removing Member from an Organisation
@user_bp.route('/delete/member/organisation', methods=['DELETE'])
@jwt_required
def remove_organisation_member():
    current_user_id = get_jwt_identity()
    email = request.get_json()['email']
    organisation_name = request.get_json()['organisation_name']
    current_user = OrganisationMembers.query.filter_by(user_id = current_user_id).first()
    
    # check if current user in an admin
    if current_user.is_admin is True:
        user = User.query.filter_by(email=email).first()
        organisation = Organisation.query.filter_by(name=organisation_name).first()
        
        if user and organisation: 
            response = delete_organisation_member(user.id, organisation.id)
            return response
        else:
            response = jsonify({
                'message': 'User or Organisation does not exist'
            })
            response.status_code = 401
            return response 
    else:
        response = jsonify({
            'message': 'User is not an Admin'
        })
        response.status_code = 401
        return response

# Show organisations list
@user_bp.route('/user/get/organisations', methods=['GET'])
@jwt_required
def get_user_organisation():
    current_user = get_jwt_identity()
    user = User.query.filter_by(id=current_user).first()

    if user:
        org_association = OrganisationMembers.query.filter_by(user_id=user.id).all()
        repsArr = []

        for i in org_association:
            dict_obj = i.toDict()
            organisation = get_organisations(dict_obj["organisation_id"])
            organisation = json.loads(organisation)
            if len(organisation) > 0:
                repsArr.append(organisation[0])

        response = json.dumps(repsArr)
        return response
    else:
        response = jsonify({
            "message": "Not registered user"
        })
        return response

# Show all users in the database
@user_bp.route('/show/all/users', methods=['GET'])
@jwt_required
def show_all_users():
    users = User.query.all()
    respArr = []
    names ={}

    for user in users:
        dict_obj = user.toDict()
        names['name'] = dict_obj['name']
        names['email'] = dict_obj['email']
        respArr.append(names)
    response = json.dumps(respArr)
    return response

# Updating User
@user_bp.route('/update/user', methods=['POST'])
@jwt_required
def update_user():
    current_user = get_jwt_identity()
    req = request.get_json()
    new_email = ''
    new_name = ''
    new_password = ''
    if "new_email" in req:
        new_email = req["new_email"]
    if "new_name" in req:
        new_name = req["new_name"]
    if "new_password" in req:
        new_password = req["new_password"]

    user = User.query.filter_by(id = current_user).first()
    if user:
        if new_name:
            user.name = new_name
        if new_password:
            user.password = Bcrypt().generate_password_hash(new_password).decode()
        if new_email:
            user.email = new_email

        user.update()

        response = jsonify({
            'message': 'Successfully Updated'
        })
        response.status_code = 201
        return response 
    else:
        response = jsonify({
            'message': 'User does not exist'
        })
        response.status_code = 401
        return response 
