from models import *


ALLOWED_ATTRIBUTES = {
    User : {'username', 'password', 'email'}, 
    Inventory : {'quantity' , 'isFirstEd'},
    Deck : {'name'},
    CardinDeck : {'quantity','location'},
    User : {''}, 
    Card : {}, 
    ReleaseSet : {},

}

MODEL_MAP = {
        'users': User , 
        'decks': Deck,
        'cardsindecks': CardinDeck, #this is a special case since no direct link to user_id. it goes cardindeck->deck->user_id
        'inventory' : Inventory,
        'cardsinsets' : CardinSet,
        'cards' : Card
    }

