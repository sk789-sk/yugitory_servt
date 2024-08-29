import requests
from app import app
from models import * 
from tempfile import NamedTemporaryFile
import boto3
import pickle
import time

#Fill the database with card information

# https://db.ygoprodeck.com/api/v7/cardinfo.php has all the card information 

#Card_Sets has information on the set namde, code, rarity, 

#We fill out information on the ReleaseSets, Cards, CardsinSets

# session = boto3.Session(profile_name='shamsk')
# s3 = session.client('s3')

card_endpoint = 'https://db.ygoprodeck.com/api/v7/cardinfo.php'
set_endpoint = 'https://db.ygoprodeck.com/api/v7/cardsets.php'

# set_to_id_map = {} 
# card_to_id_map = {}
failed_cards = []
failed_released_cards = []
# released_cards = []

def upload_images(img_url,id): #imgURL is the ygoAPI link to the image, id is the ygproid from the API
    bucket_name = 'yugitorybuckettest'
    s3_key = f'{id}.jpg'
    s3_url = f'https://{bucket_name}.s3.amazonaws.com/{s3_key}' 
    retries = 0 

    while retries < 3: 
        try:
            img_bin = requests.get(img_url).content
            with NamedTemporaryFile(suffix="'jpg") as temp_file:
                temp_file.write(img_bin)
                file_name=temp_file.name
                s3.upload_file(file_name,bucket_name,s3_key)
            break
        
        except Exception as e:
            retries +=1 
            if retries == 3:
                print(f'Error getting image for id {id} Error :{e}')
                break
            print(f'Error: Retrying attepmt {retries}')        
        time.sleep(60)

    return s3_url

def get_release_sets():
    response = requests.get(set_endpoint)
    sets_info = response.json()
    setlist = [] #set for db 
    error_list = [] 
    #Since we are seeding with an empty db we can assume its all incrementing from 0. In that case instead of checking for the existance of the value in the database constantly we can assume it will be uploaded in the same order as we go through the set info and create a dictionary (set to id map) that we can use to refer to what the primary key. This would only work when the database is created for the first time. 
    set_to_id_map = {} #referenced


    j = 0 
    for card_set in sets_info:
        # print(card_set)
        try:
            pack = ReleaseSet(
                name = card_set['set_name'],
                releaseDate = card_set.get('tcg_date', None),
                card_count = card_set['num_of_cards'],
                set_code = card_set['set_code']
            )
            j+=1 
            set_to_id_map[card_set['set_name']] = j
            setlist.append(pack)
        except:
            error_list.append(card_set)
    return setlist , set_to_id_map

#A couple ideas for seeding the card data. All cards will have the following parameters: id, name, type, frameType, desc
#Monster cards have an atk, def, level, race, attribute
#Spell/Trap cards have a race
#Pendulums have a scale

#We have other ways to check for boolean values from different end points and we can use those to modify the values before submitting to the db. 

def getinitcards(set2idmap):
    response = requests.get('https://db.ygoprodeck.com/api/v7/cardinfo.php?fname=')
    card_data = response.json()
    init_card_arr = []    #for testing purposes 
    card_to_id_map = {}   #init cards searchable by id 
    released_cards_arr = []  #arr for db 

    print(len(card_data['data']))

    i = 0
    for card in card_data['data']:
        #create the image and upload it to s3
        #then create the skeleton object and add it to my dictionary of cards
        if "card_sets" in card: #Card has a tcg printing not an anime/namga card
            i+=1
            card_id = card['id']
            img_url = card['card_images'][0]['image_url_small']

            card_type = card['type']
            
            if 'Spell' in card_type:
                card_type = 'Spell'
            elif 'Trap' in card_type:
                card_type = 'Trap'
            else:
                card_type = 'Monster'

            #image upload section                
            s3_url = 'temp' #upload_images(img_url=img_url,id=card_id)
            #create the card 
            try:
                init_card = Card(
                    yg_pro_id = card_id,
                    name = card['name'],
                    description = card['desc'],
                    attack = card.get('atk'), #card['atk'] if card['atk'] else None,
                    defense = card.get('def'), #card['def'] if card['def'] else None,
                    level = card.get('level'), #card['level'] if card['level'] else None,
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
                    card_type = card_type,
                    card_race = card.get('race'), #card['race'] if card['race'] else None,
                    card_attribute = card.get('attribute'), #card['attribute'] if card['attribute'] else None,
                    LegalDate = None,
                    card_image = s3_url,
                    frameType = card['frameType']
                )        
                card_to_id_map[card_id] = init_card
                init_card_arr.append(init_card)
                print(f'{i} of {len(card_data["data"])}')

                #Create the releaseCards now

                for cardSet in card['card_sets']:
                    try:
                        released_card = CardinSet(
                            card_code = cardSet['set_code'],
                            rarity = cardSet['set_rarity'],
                            card_id = i,
                            set_id = set2idmap[cardSet['set_name']]
                        )
                        released_cards_arr.append(released_card)
                    except Exception as e:
                        #failed_to_create_released card
                        print(f'failed to create: {e}')
                        failed_released_cards.append((card_id,cardSet['set_code']))
            except:
                #failed to create the card
                failed_cards.append(card_id)
        else:
            print('anime/manga_card')
    # print(card_to_id_map)
    # print(failed_cards)
    return init_card_arr ,released_cards_arr , card_to_id_map 

def fillCards(init_cards):
    #fill out the information in the Cards thar are None
    #We can have the enpoint we are searching for and the values to toggle on 

    type_endpoint_dict = {
        "Effect Monster" : ['isEffect'],
        "Flip Effect Monster" : ['isFlip', 'isEffect'],
        "Gemini Monster" : ['isGemini'], 
        # "Normal Monster" : [], 
        "Normal Tuner Monster" : ['isTuner'],
        "Pendulum Effect Monster" : ['isEffect','isPendulum'], 
        "Pendulum Flip Effect Monster" : ['isEffect','isFlip','isPendulum'], 
        "Pendulum Normal Monster" : ['isPendulum'], 
        "Pendulum Tuner Effect Monster" : ['isPendulum','isTuner','isEffect'], 
        "Ritual Effect Monster" : ['isRitual', 'isEffect'],
        "Ritual Monster" : ['isRitual'],
        # "Spell Card" : [],
        "Spirit Monster" : ['isSpirit'],
        "Toon Monster" : ['isToon'],
        # "Trap Card" : [],
        "Tuner Monster" : ['isTuner'],
        "Union Effect Monster" : ['isUnion'], 
        "Fusion Monster" : ['isFusion'],
        "Link Monster" : ['isLink'],
        "Pendulum Effect Fusion Monster" : ['isPendulum','isFusion','isEffect'],
        "Synchro Monster" : ['isSynchro'], 
        "Synchro Pendulum Effect Monster" : ['isSynchro','isPendulum','isEffect'],
        "Synchro Tuner Monster" : ['isSynchro','isTuner'],
        "XYZ Monster" : ['isXYZ'],
        "XYZ Pendulum Effect Monster" : ['isXYZ','isPendulum','isEffect']
    }
    
    # test_dict = {
    #     "Ritual Effect Monster" : ['isRitual', 'isEffect'],
    # }


    base_url = 'https://db.ygoprodeck.com/api/v7/cardinfo.php?type='

    print('Adding Toggles')

    for key in type_endpoint_dict: #type_endpoint_dict
        #get the api results
        #search for the cards and the flip the toggle
        i = 0 
        toggles = type_endpoint_dict[key]
        req_url = base_url + key

        req_info = requests.get(req_url)
        card_data = req_info.json()
        print(f'Current Key {key}')
        total_entries = len(card_data['data'])

        for card in card_data['data']:
            if init_cards.get(card['id']):
                i+=1
                card_info = init_cards[card['id']]
                #update card toggles
                for toggle in toggles:
                    setattr(card_info, toggle , True)
                #update dict
                init_cards[card['id']] = card_info
                print(f'{i} of {total_entries}')
    cards_array = list(init_cards.values())

    return cards_array , init_cards


if __name__ == "__main__":
    with app.app_context():
        releaseSet_info , set2idmap_real = get_release_sets()
        db.session.add_all(releaseSet_info)

        init_cards , released_cards_arr, card_to_id_map = getinitcards(set2idmap_real)
        filled_cards , updated_card_dict = fillCards(card_to_id_map)
        

        db.session.add_all(filled_cards)
        db.session.add_all(released_cards_arr)
        db.session.commit()
        
        print('seeding complete')

        with open('set2idmap_real.pkl' ,'wb') as f:
            pickle.dump(set2idmap_real, f)
        
        with open('card2idmap.pkl', 'wb') as f:
            pickle.dump(card_to_id_map, f)
        