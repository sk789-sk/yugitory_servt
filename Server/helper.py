import requests
import time
from app import app
from config import db
from models import *
from sqlalchemy import text

#Helper Functions

#testing imports
from testingfunctions import deleteSet

from DB_modification_functions import createDBCard, createDBCardinSet , createDBReleaseSet

#Update Database functions

card_endpoint = 'https://db.ygoprodeck.com/api/v7/cardinfo.php'
set_endpoint = 'https://db.ygoprodeck.com/api/v7/cardsets.php'
release_set_endpoint = 'https://db.ygoprodeck.com/api/v7/cardinfo.php?cardset='

def update_database():
#First we want to figure out which releaseSets we do not have in the database. 
#We can then go through the releasesets individual cards.
#If that card already exists, then we will create new cardinSets entry. 
#If that card doesn't exist, then we will create a new card entry. We will also create a new cardinSets entry. 
#New cards would also need to be created on S3. 
#afaik all cards are released in new sets or promotions etc. Can i query for cards by a release set? i think i should be able 
    release_sets = getApiReleaseSets()    
    saved_sets = getDBReleaseSets()
    update_list = reconcileReleaseSets(release_sets, saved_sets)
    for record in update_list: #iterate over the list of sets we do not have
        out = createDBReleaseSet(record) #create the record if success returns id and name
        #get a list of cards from the set
        
        if isinstance(out,tuple):
            set_id = out[0]
            set_name = out[1]
            response = requests.get(release_set_endpoint + set_name,timeout=30.0)
            cardsinSet_List = response.json()
            for card in cardsinSet_List['data']: #Go through the cards in each set
                #check if we have the card
                card_exists = Card.query.filter(Card.name==str(card['name'])).first()
                try:
                    if card_exists:
                        createDBCardinSet(set_id,card_exists.id,set_name,card)
                    else:
                        card_id = createDBCard(card)  #Returns the id for the new card. 
                        createDBCardinSet(set_id, card_id, set_name,card)
                except:
                    return
            db.session.commit()    
        #If we put together a full releaseSet with no errors we can commit that to the db. 
        else:
            #Error We didnt create a sucessfull record
            return
        
def getApiReleaseSets():
    response = requests.get(set_endpoint)
    allSets = response.json()
    setlist = []
    for releaseset in allSets:
        setlist.append(releaseset) 
    return setlist

def getDBReleaseSets():
    setdict = {}
    with app.app_context():
        release_list = ReleaseSet.query.all()
        for set in release_list:
            setdict[set.name] = set.id
    return setdict

def reconcileReleaseSets(setlist, setdict): #given a list of entries see if they are in out database(db is the setdict for id access and faster lookup)
    unadded_sets = []
    for releaseSet in setlist:
        if releaseSet['set_name'] not in setdict:
            unadded_sets.append(releaseSet)
    return unadded_sets

# def createDBReleaseSet(release_set): #releaseSet is the API object
#     try:
#         pack = ReleaseSet(
#             name = release_set['set_name'],
#             releaseDate = release_set.get('tcg_date', None),
#             card_count = release_set['num_of_cards'],
#             set_code = release_set['set_code']
#         )
#         # with app.app_context():
#         db.session.add(pack)
#         db.session.flush()
#         return pack.id , pack.name
#     except:
#         error_name = release_set['set_name']
#         return error_name

# def createDBCard(card): #card is the card_obj from the API
#     #lets assume that we have a valid card to be added 
#     #upload the card image to s3, use the function we already have
#     #try to create the card
    
#     #s3 upload function

#     try:
#         url = 'temp' #whatever the s3 function returns
#         new_card = Card(
#             yg_pro_id = card['id'],
#             name = card['name'],
#             description = card['desc'],
#             attack = card.get('atk'),
#             defense = card.get('def'), #card['def'] if card['def'] else None,
#             level = card.get('level'),
#             isEffect = False,
#             isTuner = False,
#             isFlip = False,
#             isSpirit = False,
#             isUnion = False,
#             isGemini = False,
#             isPendulum = False,
#             isRitual = False,
#             isToon = False,
#             isFusion = False,
#             isSynchro = False,
#             isXYZ = False,
#             isLink = False,
#             card_type = card.get('card_type'),
#             card_race = card.get('race'), 
#             card_attribute = card.get('attribute'),
#             LegalDate = None,
#             card_image = url,
#             frameType = card['frameType']
#         )
        
#         #toggle all of the cards flags as well. 
#         db.session.add(new_card)
#         db.session.flush()
#         return new_card.id
#     except: #error creating the card object
#         print(f'Error creating card {card["id"]}')
#         return card['id'] #add to the error list

# def createDBCardinSet(release_set_id, card_id, set_name,card_obj):

#     new_card_list = []

#     for singleRelease in card_obj['card_sets']:
#         if singleRelease['set_name'] == set_name:
#             print('we made it ')
#             try: 
#                 new_release = CardinSet(
#                     card_id = card_id,
#                     set_id = release_set_id,
#                     card_code = singleRelease['set_code'],
#                     rarity = singleRelease['set_rarity']
#                 )
#                 new_card_list.append(new_release)
#             except:
#                 print(f'Error creating {card_id} in {set_name}')
#         db.session.add_all(new_card_list)
#     return new_card_list

# def fillcards(): #toggle the card flags
#     pass

if __name__ == "__main__":

    with app.app_context():
        deleteSet('Absolute Powerforce')
        deleteSet('Abyss Rising')
        update_database()












