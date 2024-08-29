from flask import Blueprint, request, jsonify , make_response


#local imports
from config import db
from utils.tokenutils import issue_jwt_token , invalidate_refresh_token , token_required
from utils.server_responseutils import item_not_found_response , unauthorized_response
from models import User , RefreshToken , Inventory


auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/Login', methods = ["POST"])
def Login():    

    user_info = request.get_json()     
    
    user = User.query.filter(User.username == user_info['username']).first()
    

    # if 'refreshToken' in user_info:
    #     #Check if refreshToken is Valid
    #     #If Valid return an access Token
    #     #if invalid return that to client so they can ask for auth
    #     users_token = RefreshToken.query.filter(RefreshToken.user_id==user.id).first()
    #     if users_token.token==user_info['refreshToken'] and users_token.is_valid():
    #         jwt_token = issue_jwt_token(user.username,user.id)
    #         user_dict = user.to_dict()
    #         user_dict['accessToken'] = jwt_token
    #         user_dict['refreshToken'] = users_token.token
    #         response = make_response(jsonify(user_dict),201)

    if user:
        if 'refreshToken' in user_info:
        #Check if refreshToken is Valid
        #If Valid return an access Token
        #if invalid return that to client so they can ask for auth
            users_token = RefreshToken.query.filter(RefreshToken.user_id==user.id).first()

            if str(users_token.token)==user_info['refreshToken'] and users_token.is_valid():
                jwt_token = issue_jwt_token(user.username,user.id)
                user_dict = user.to_dict()
                user_dict['accessToken'] = jwt_token
                user_dict['refreshToken'] = users_token.token
                response = make_response(jsonify(user_dict),201)
                return response
            else:
                response = make_response({"Error":"Expired or invalid token login needed"},403)
                return response

        pass_match = user.authenticate(user_info['password'])
        if pass_match:
            #create JWT and refresh token
            #token = issue_jwt_token(user.username,user.id)            
            # refresh_token = issue_refresh_token(user.id)
            
            token = issue_jwt_token(user.username, user.id)
            refresh_token = RefreshToken.issue_refresh_token(user.id)

            #If we have a refresh token we need to just update that param

            has_refresh = RefreshToken.query.filter(RefreshToken.user_id == user.id).first()

            if has_refresh:
                has_refresh.token, has_refresh.expiration_time = refresh_token.token, refresh_token.expiration_time
                db.session.add(has_refresh)
            else:
                db.session.add(refresh_token)
            
            db.session.commit()
            
            user_dict = user.to_dict()
            user_dict['accessToken'] = token
            user_dict['refreshToken'] = refresh_token.token
            response = make_response( 
                jsonify(user_dict), 201
            )
        else:
           response = make_response({},401)
    else:
        response = make_response({},404)
    
    return response

@auth_bp.route('/Logout' , methods = ["POST"])
@token_required
def logout(user_id):
    #Send back the user id, delete that entry from the refreshToken table. 
    data = request.get_json()
    #expect the user_id 

    isLogOut = invalidate_refresh_token(data['user_id'])
    if isLogOut:
        response = make_response({},200)
        return response
    return make_response({},401)

@auth_bp.route('/RefreshAccessToken' , methods = ["POST"])
def refresh_access_token():
    #Passing the refresh token in the body
    #I could query either the refresh token directly or query the user_id and then look at the refresh token stored there and compare with what i get back. I think this would be quicker, but assumes I would always get the user id. Simple version first.
    data = request.get_json()
    received_token = data['refreshToken']

    refresh_token_record_uuid = RefreshToken.query.with_entities(RefreshToken.token,RefreshToken.expiration_time).filter(RefreshToken.user_id==data['user_id']).first()

    #Check if refresh token is valid also. 
    if refresh_token_record_uuid:
    
        saved_token = str(refresh_token_record_uuid[0])
        if saved_token == received_token: 
            print('match, return new access token')
            new_accesstoken = issue_jwt_token('temp',data['user_id'])
            response = make_response(jsonify({"accessToken":new_accesstoken})),201
        else:
            print('RefreshToken does not match, Log-in again')
            response = unauthorized_response()

    else:
        response = item_not_found_response()
        print('no record found')
    return response

@auth_bp.route('/TestAuth', methods=['GET'])
@token_required
def user_invent(user_id):
    card_info = Inventory.query.filter(Inventory.user_id==user_id).first()
    print('???')

    response = make_response(jsonify(card_info)),201
    return response