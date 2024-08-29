from flask import Blueprint, make_response , jsonify, request
from sqlalchemy.exc import SQLAlchemyError , IntegrityError
from psycopg2.errors import UniqueViolation , NoDataFound

field = 'p'

{
    "error":"Error Type( Unique Violation)",
    "message": f"{field} is already taken",
    "value": "name"
}

ERROR_MESSAGES = {
    'uq_Users_username':{},
    'uq_Users_email':{},
    
}


def server_error_response():
    return jsonify({'Error': 'Server Error'}),500

def item_not_found_response():
    return jsonify({'Error': 'Item not found'}), 404

def validation_error_response():
    return jsonify({'Error': 'Validation Error'}), 403

def bad_request_response():
    return jsonify({'Error':'Bad Request'}),400

def unauthorized_response():
    return jsonify({'Error':'Unauthorized'}),401

##Validation functions

##HTTP responses

##Logging
