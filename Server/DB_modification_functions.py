import boto3


#Create 

from config import db
from models import ReleaseSet, Card, CardinSet
from seed import upload_images

session = boto3.Session(profile_name='shamsk')
s3 = session.client('s3')



def createDBReleaseSet(release_set): #releaseSet is the API object
    try:
        pack = ReleaseSet(
            name = release_set['set_name'],
            releaseDate = release_set.get('tcg_date', None),
            card_count = release_set['num_of_cards'],
            set_code = release_set['set_code']
        )
        # with app.app_context():
        db.session.add(pack)
        db.session.flush()
        return pack.id , pack.name
    except:
        error_name = release_set['set_name']
        return error_name
    

def createDBCard(card): #card is the card_obj from the API
    #lets assume that we have a valid card to be added 
    #upload the card image to s3, use the function we already have
    #try to create the card
    
    #s3 upload function
    img_url = card['card_images'][0]['image_url_small']

    s3_url = upload_images(img_url,card['id'])

    try:
        url = 'temp' #whatever the s3 function returns
        new_card = Card(
            yg_pro_id = card['id'],
            name = card['name'],
            description = card['desc'],
            attack = card.get('atk'),
            defense = card.get('def'), #card['def'] if card['def'] else None,
            level = card.get('level'),
            isEffect = False,
            isTuner = False,
            isFlip = False,
            isSpirit = False,
            isUnion = False,
            isGemini = False,
            isPendulum = False,
            isRitual = False,
            isToon = False,
            isFusion = False,
            isSynchro = False,
            isXYZ = False,
            isLink = False,
            card_type = card.get('card_type'),
            card_race = card.get('race'), 
            card_attribute = card.get('attribute'),
            LegalDate = None,
            card_image = url,
            frameType = card['frameType']
        )
        
        #toggle all of the cards flags as well. 
        db.session.add(new_card)
        db.session.flush()
        return new_card.id
    except: #error creating the card object
        print(f'Error creating card {card["id"]}')
        return card['id'] #add to the error list
    
def createDBCardinSet(release_set_id, card_id, set_name,card_obj):

    new_card_list = []

    for singleRelease in card_obj['card_sets']:
        if singleRelease['set_name'] == set_name:
            try: 
                new_release = CardinSet(
                    card_id = card_id,
                    set_id = release_set_id,
                    card_code = singleRelease['set_code'],
                    rarity = singleRelease['set_rarity']
                )
                new_card_list.append(new_release)
            except:
                print(f'Error creating {card_id} in {set_name}')
        db.session.add_all(new_card_list)
    return new_card_list

def fillcards(): #toggle the card flags
    pass