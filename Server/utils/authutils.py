#f


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
            print('Auth in here')
        if not token:
            return jsonify({'message': 'No Token'}), 401
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            print(data)
            user_id = data['user_id']
        except Exception as e:
            print(e)
            return jsonify({"message":"invalid token"}), 401
        # kwargs['test'] = 5
        return f(user_id, *args, **kwargs)
    return decorated

def authorize(check_func): 
    def decorator(f):
        @wraps(f)
        def decorated(user_id,*args,**kwargs): 
            data = request.get_json()
            if not check_func(user_id, *args, **data):
                return jsonify({"Error":"Unauthorized"}), 403
            return f(user_id,*args,**kwargs)
        return decorated
    return decorator

def is_authorized_to_create(user_id, *args, **kwargs): 
    #Check if user can create the resource
    ##Unpack args/kwargs in the function
    return True


def is_authorized_to_modify(user_id, *args,**kwargs): #check if user owns the resource

    resource_location = kwargs["table_name"]
    resource_id = kwargs["resource_id"]


    model_map = {
        'cards': Card , 
        'decks': Deck,
        'cardsindecks': CardinDeck, #this is a special case since no direct link to user_id. it goes cardindeck->deck->user_id
        'inventory' : Inventory
    }

    model_class = model_map.get(resource_location.lower())
    #Get the Resource

    resource = db.session.query(model_class).filter(model_class.id == resource_id).first()

    if resource and resource.user_id == user_id:
        return True
    return False











