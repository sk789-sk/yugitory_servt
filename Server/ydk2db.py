from app import app
from models import *

def process_file(file=None,filepath=None):
    if file:
        file_content = file.read().decode('utf-8')
    elif filepath:
        with open(filepath, 'r' , encoding='utf-8') as f:
            file_content = f.read()
    else:
        raise ValueError("gimme something to work with")
    
    return file_content

def ydk_to_dict(file_content):
    #Assume we have the content for the file currently
    #YDK file has leading 0's, tcg api does not have leading and trailing 0's

    main_deck = {}
    side_deck = {}
    extra_deck = {}

    current_dict = None

    for line in file_content.splitlines():
        line = line.strip()

        if line == '#main':
            current_dict = main_deck
        elif line == '#extra':
            current_dict = extra_deck
        elif line == '!side':
            current_dict = side_deck

        elif line and line.isdigit():
            if current_dict is not None:
                if int(line) in current_dict:
                    current_dict[int(line)] +=1 
                else:
                    current_dict[int(line)] = 1
    
    print(main_deck)
    print(side_deck)
    print(extra_deck)

    deck = {
        'main': main_deck,
        'side' : side_deck,
        'extra' : extra_deck 
    }

    return deck

def deck_dictionary_to_db_objs(deck_dict, deck_id):
    #Cache for ygopro to card_id so we dont need to make db calls;

    ygproid_to_dbid = {}

    #need to get the corresponding card_id for it
    new_cards = []
    missing_cards = []

    for key,cards_in_location in deck_dict.items():
        location = key
        for ygo_pro_card_id , quantity in cards_in_location.items():
            if ygo_pro_card_id in ygproid_to_dbid:
                cards_db_id = ygproid_to_dbid[ygo_pro_card_id]
            else:
                card = Card.query.filter(Card.yg_pro_id==str(ygo_pro_card_id)).first()

                if card is None:
                    missing_cards.append(ygo_pro_card_id)
                    continue

                cards_db_id = card.id
                ygproid_to_dbid[ygo_pro_card_id] = cards_db_id
            
            card_in_deck = CardinDeck(
                quantity=quantity,
                location=location,
                deck_id=deck_id,
                card_id=cards_db_id
            )
            new_cards.append(card_in_deck)
    print(len(new_cards))
    print(new_cards)
    return new_cards

def commit_new_cards(card_list):
    db.session.add_all(card_list)
    db.session.commit()


if __name__ == "__main__":
    with app.app_context():
        file_path = '/home/shamsk/Dev/YugiInventory/Server/test_decks/Edison- Dark Plant.ydk'

        file_content = process_file(filepath=file_path)
        deck_output = ydk_to_dict(file_content)
        new_cards = deck_dictionary_to_db_objs(deck_dict=deck_output, deck_id=46)
        commit_new_cards(new_cards)
