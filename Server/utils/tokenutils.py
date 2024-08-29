import jwt
import datetime

from flask import request , jsonify
from config import app,db
from functools import wraps

from models import RefreshToken , CardinDeck , Deck , Inventory , User
from utils.constants import MODEL_MAP


def issue_jwt_token(username,user_id):
    token = jwt.encode(
        {'username':username,
         'user_id':user_id,
         'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=240),
         'iat': datetime.datetime.now(datetime.timezone.utc)
         },app.config['SECRET_KEY'])            
    return token

def invalidate_jwt_token():
    pass

def validate_jwt():
    pass

def invalidate_refresh_token(user_id):
    #this would be deleted from the server
    refreshToken = RefreshToken.query.filter(RefreshToken.user_id == user_id).first()
    if refreshToken:
        db.session.delete(refreshToken)
        db.session.commit()
        return True
    return False

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        if not token:
            return jsonify({'message': 'No Token'}), 401
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            user_id = int(data['user_id']) #extracting from token returns a str. 
        except Exception as e:
            print(e)
            print(type(e))
            return jsonify({"message":"invalid token"}), 401
        return f(user_id, *args, **kwargs)
    return decorated

def authorize(check_func , edit=False): 
    def decorator(f):
        @wraps(f)
        def decorated(user_id,*args,**kwargs): 
            
            data = request.get_json()
            
            if edit:
                resource_location = data.get("resource_location")
                resource_id = data.get("resource_id")
                resource = resource_exists(resource_location,resource_id)
                if not resource:
                    return jsonify({"Error":"Resource does not existskibidibap"}),404
                kwargs['resource'] = resource
            kwargs.update(data)
            if not check_func(user_id, *args, **kwargs):
                return jsonify({"Error":"Unauthorized"}), 403
            return f(user_id,*args,**kwargs)
        return decorated
    return decorator

def is_authorized_to_create(user_id, *args, **kwargs): 
    #Check if user can create the resource
    ##Unpack args/kwargs in the functio
    ## For Card in Deck can you create the resource if you own the deck

    resource_location = kwargs["resource_location"]
    if resource_location.lower() == 'cardsinsets':
        exists = resource_exists(resource_location, kwargs["resource_id"])
        if exists:
            return True
        return False
    if resource_location.lower() == 'cardsindecks':
        deck_id = kwargs.get("deck_id")
        if not deck_id:
            return False
        deck = Deck.query.filter(Deck.id==deck_id).first()
        if deck and deck.user_id==user_id:
            return True
        return False
    return True


def is_authorized_to_modify(user_id, *args,**kwargs): #check if user owns the resource

    resource_location = kwargs["resource_location"]
    resource_id = kwargs["resource_id"]

    model_map = {
        'users': User , 
        'decks': Deck,
        'cardsindecks': CardinDeck, #this is a special case since no direct link to user_id. it goes cardindeck->deck->user_id
        'inventory' : Inventory
    }

    model_class = model_map.get(resource_location.lower())
    #Get the Resource
    if not model_class:
        return False
    
    if model_class== CardinDeck:
        card_to_edit = CardinDeck.query.filter(CardinDeck.id==resource_id).first()
        if card_to_edit:
            deck = Deck.query.filter(Deck.id==card_to_edit.deck_id).first()
            if deck and deck.user_id == user_id:
                return True
        return False
    
    
    resource = db.session.query(model_class).filter(model_class.id == resource_id).first()

    if resource and resource.user_id == user_id:
        return True
    return False

def resource_exists(resource_location, resource_id):
    #This is since when we authorize we do need to check if the resource exists and we want to return 404 if it doesnt instead of 403. 
    model_class = MODEL_MAP.get(resource_location.lower())
    
    if model_class:
        return db.session.query(model_class).filter(model_class.id == resource_id).first()    #might need to be all for deletes where we are deleting many
    return None




#Model Map will end up refrencing the repository objects instead of the model itself since the repository will handle getting the data













###For my own learning/testing

def check(f):
    def added_functionality(*arg,**kwargs):
        new_var = 5
        if 4 in arg:
            print('unequal')
            return
        return f(new_var,*arg,**kwargs)
    return added_functionality

@check #check = check(test)
def test(*args):
    return sum(args)

##If i am understanding this properly this works as follows.
##We created a function check that takes in 1 function as an input.
##Inside the check function we define a new function called add_functionality that takes in a variable amount of arguements. 
##This added_functionality fcn returns the function that was inputted to check with the old parameters and a new one called new_var
##Check functions return statement is added_functionality so it just "executes" that function. Its not really executing its just replacing the function.
## In this case the function f is the function test(*args)
#Execution is as follows
#check(test(*args)) 
#added_functionality(test(*args))
#test(new_var,*args)

#esoteric example below of how we can make a decorator that is a function that returns a decorator
#https://stackoverflow.com/questions/35572663/using-python-decorator-with-or-without-parentheses second explanation is nice imo



# def some_decorator(arg=None):
#     def decorator(func):
#         def wrapper(*a, **ka):
#             return func(*a, **ka)
#         return wrapper

#     if callable(arg):
#         return decorator(arg) # return 'wrapper'
#     else:
#         return decorator # ... or 'decorator'


if __name__ =='__main__':
    print(test(3, 4))
    print(test(1,3,5))