from flask import jsonify


def server_error_response():
    return jsonify({'Error': 'Server Error'}),500

def item_not_found_response():
    return jsonify({'Error': 'Item not found'}), 404

def validation_error_response():
    return jsonify({'Error': 'Validation Error'}), 403

def bad_request_response():
    return jsonify({'Error':'Bad Request'}),400
#item_not_found_response = make_response({'Error':'Item not found'},404)

def unauthorized_response():
    return jsonify({'Error':'Unauthorized'}),401

def paginate(query,page, per_page):
    return query.paginate(page=page,per_page=per_page) #these all have to be deinfed with keyword only?