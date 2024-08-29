from sqlalchemy_serializer import SerializerMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData, event
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.dialects.postgresql import UUID
import datetime
import uuid

from sqlalchemy.sql import func



from config import db, bcrypt
from error_handling.error_class import ValidationError

class RefreshToken(db.Model, SerializerMixin):
    __tablename__ = 'RefreshTokens'
    id = db.Column(db.Integer, primary_key = True)
    token = db.Column(UUID(as_uuid=True))
    expiration_time = db.Column(db.DateTime()) #timezone=true, not sure if this necessary tbh
    #FK
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False, unique=True)
    
    serialize_rules = ('-user_id',)


    def is_valid(self):
        return datetime.datetime.now() < self.expiration_time
        #datetime.timezone.utc if I want to store timezone info and normalize it to utc

    @staticmethod
    def issue_refresh_token(user_id):
        new_uuid = uuid.uuid4()
        expiration_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=60)
        refresh_token = RefreshToken(token=new_uuid, user_id=user_id,expiration_time=expiration_time)
        return refresh_token


class User(db.Model, SerializerMixin):
    __tablename__ = 'Users'

    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String, unique = True)
    _password_hash = db.Column(db.String) #hash after
    email = db.Column(db.String, unique = True)
    
    profile = db.Column(db.String) #path to profile
    created_at = db.Column(db.DateTime(timezone=True), default= db.func.now())
    
    #ForeignKeys

    #relationships    
    card_in_inventory = db.relationship("Inventory" , backref = "user")
    user_decks = db.relationship("Deck",backref = "user")
    refresh_token = db.relationship('RefreshToken', backref = "user")

    #validations
    @validates('username')
    def validate_quantity(self,key,username):
        if len(username) > 0:
            return username
        raise ValidationError(key,username)

    @validates('email')
    def validate_email(self,key,email):
        
        invalid_char_list = []

        if len(email) == 0:
            raise ValidationError(key,email)
        # if '@' not in email:
        #     raise ValueError
        if " " in email:
            raise ValidationError(key,email)
        return email
    
    @hybrid_property 
    def password_hash(self):
        return self._password_hash
    
    @password_hash.setter
    def password_hash(self, password):
        password_hash = bcrypt.generate_password_hash(password.encode('utf-8'))
        self._password_hash = password_hash.decode('utf-8')

    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password_hash, password.encode('utf-8'))

     
    #email validation,username length
    #username has to be unique
    
    #Serializer Rules


    serialize_rules = ('-card_in_inventory.user','-user_decks.user','-card_in_inventory.card','-user_decks.card_in_deck','-refresh_token')
    

  
class Inventory(db.Model, SerializerMixin):
    __tablename__ = 'Inventories'
    #table columns 
        #id, user id, card_id, quantity, created_at 
    id = db.Column(db.Integer, primary_key = True)
    quantity = db.Column(db.Integer)
    created_at = db.Column(db.DateTime(timezone=True), default= db.func.now())
    isFirstEd = db.Column(db.Boolean)

    #ForeignKeys
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'))
    cardinSet_id = db.Column(db.Integer, db.ForeignKey('CardsinSets.id'))
    
    #relationships
    #validations

    #adding validations returns html? why
    
    @validates('quantity')
    def validate_quantity(self,key,quantity):
        if int(quantity) >0:
            return quantity
        raise ValidationError(key,quantity,"Quantity must be greater than 0")

    #Serializer Rules
    serialize_rules = ('-user.card_in_inventory','-cardinSet.card_in_inventory','-card.releaseSet','-card.card_in_deck','-user.user_decks')  
    
    #repr
    # def __repr__(self):
    #     return f'Inventory belongs to user with id {self.user_id}'

    

class Card(db.Model, SerializerMixin):
    __tablename__ = 'Cards'
    #table columns
    id = db.Column(db.Integer, primary_key = True)
    yg_pro_id = db.Column(db.String)     
    name = db.Column(db.String)
    description = db.Column(db.String)
    attack = db.Column(db.Integer)
    defense = db.Column(db.Integer)
    level = db.Column(db.Integer)
    isEffect = db.Column(db.Boolean)
    isTuner = db.Column(db.Boolean)
    isFlip = db.Column(db.Boolean)
    isSpirit = db.Column(db.Boolean)
    isUnion = db.Column(db.Boolean)
    isGemini = db.Column(db.Boolean)
    isPendulum = db.Column(db.Boolean)
    isRitual = db.Column(db.Boolean)
    isToon = db.Column(db.Boolean)
    isFusion = db.Column(db.Boolean)
    isSynchro = db.Column(db.Boolean)
    isXYZ = db.Column(db.Boolean)
    isLink = db.Column(db.Boolean)
    card_type = db.Column(db.String) # monster, spell , trap, monster 
    card_race = db.Column(db.String) #this is card type spellcaster/gemini/winged beast for monsters. For spells it is quickplay, spell, etc, for traps cont counter etc
    card_attribute = db.Column(db.String) #Null for spells/traps
    LegalDate = db.Column(db.String) #first printing or when the card became legal
    card_image = db.Column(db.String) #Reference to location on s3
    frameType = db.Column(db.String) #

   
    #ForeignKeys
    
    #relationships
    
    card_in_deck = db.relationship("CardinDeck",backref = "card") 
    
    card_on_banlist = db.relationship('BanlistCard',backref='card')

    card_in_set = db.relationship('CardinSet', backref = 'card')
    
    #validations
    #Cards should have a name, and a set 

    #Serializer Rules
    serialize_rules = ('-card_in_inventory.card','-card_in_deck.card','-card_in_inventory.user','-card_on_banlist.card','-card_in_set.card')

    def __repr__(self):
        return f'detailed information can be found at endpoint {self.name}'

class Deck(db.Model, SerializerMixin):
    __tablename__ = 'Decks'
    __table_args__ = (
        db.UniqueConstraint('user_id','name'),
    )
        #table columns
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String)
    created_at = db.Column(db.DateTime(timezone=True), default= db.func.now())
    isPublic = db.Column(db.Boolean, default=False)

    #ForeignKeys
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'))

    #relationships

    card_in_deck = db.relationship('CardinDeck', backref = 'deck')

    #validations
    @validates('name')
    def validate_name(self,key,name):
        if len(str(name)) > 0:
            return name
        raise ValidationError(key, value=name,message="Name cannot be len 0")

    #Cards in a deck can not have more than 3 copies. 
    #Deck names cannot be the same

    #Serializer Rules
    
    serialize_rules = ('-card_in_deck.deck','-user.user_decks','-user.card_in_inventory')

    #repr

class CardinDeck(db.Model, SerializerMixin):
    __tablename__ = 'CardsinDecks'
    __table__args__ = (db.UniqueConstraint('deck_id','card_id','location'),)
    id = db.Column(db.Integer, primary_key = True)
    quantity = db.Column(db.Integer, nullable=False)
    location = db.Column(db.String)
    
    #foreignKeys
    deck_id = db.Column(db.Integer, db.ForeignKey('Decks.id'))
    card_id = db.Column(db.Integer, db.ForeignKey('Cards.id'))

    location_list = ['main','side','extra']

    #Validation
    #At its core can not have more than 3 of a card. If we reference accross a banlist that should be done at a higher level since banlist change and etc.
    @validates('location')
    def validate_location(self,key,location):
        if location not in self.location_list:
            raise ValidationError(key,location,'Invalid location')
        return location

    @validates('quantity')
    def validate_quantity(self,key,quantity):
        if  0 < int(quantity) <=3:
            print(quantity)
            print('>>>')
            return quantity
        raise ValidationError(key,quantity,'Invalid quantity?')
    
    def validate_self(self):
        location = self.location
        deck = Deck.query.filter(Deck.id==self.deck_id).first()
        limits = {
            'main':60,
            'side':15,
            'extra':15,
            'max_count':3
        }

        
        count = {
                'main':0,
                'side':0,
                'extra':0,
                'max_count': 0
        }     
        for val in deck.card_in_deck:
            #this gets every card_in_deck for the deck we are trying to insert into 
            count[val.location] += int(val.quantity)
            if val.card_id == int(self.card_id):
                count['max_count'] += int(val.quantity)
        
        #Now add the self quantity.

        count[self.location] += int(self.quantity)
        count['max_count'] += int(self.quantity)
        #issue here is that on a patch request we have the card already in a card_in_deck so if i try to update from 1 to 2 this will read it as we already have 1 and now we are adding 2. This will break the validation. We should if we already have the card in the deck we should remove it form the list and just add the new quantity and see if that breaks it. Implement it in the morning im about to pass out. 
        for key in limits:
            if count[key] > limits[key]:
                raise ValidationError('quantity',self.quantity,'Adding card exceeds deck limits')
    
    #Card in Deck event listener 

# event.listen(CardinDeck,'before_insert',validate_card_in_deck_insert_deck)


    #SeralizerRules

    serialize_rules = ('-deck.card_in_deck','-card.card_in_deck','-card.card_in_inventory','-card.releaseSet')


def validate_card_in_deck_insert_deck(mapper,connection,target):
    print(target)
    print('hahaxd')
    target.validate_self()

event.listen(CardinDeck, 'before_insert',validate_card_in_deck_insert_deck)
event.listen(CardinDeck, 'before_update',validate_card_in_deck_insert_deck)


class ReleaseSet(db.Model, SerializerMixin):
    __tablename__ = 'ReleaseSets'
    #table columns
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String)
    releaseDate = db.Column(db.String)
    card_count = db.Column(db.Integer)
    set_code = db.Column(db.String)

    #ForeignKeys

    #relationships

    card_in_set = db.relationship('CardinSet', backref = 'releaseSet')


    #validations
    #Serializer Rules

    serialize_rules = ('-cards_in_set.releaseSet',)

    #repr
    def __reper__(self):
        return f'{self.name} was released on {self.releaseDate}'
    

class CardinSet(db.Model,SerializerMixin):
    __tablename__ = 'CardsinSets'
    #table_columns
    id = db.Column(db.Integer, primary_key = True)
    card_code = db.Column(db.String)
    rarity = db.Column(db.String)

    #ForeignKeys
    set_id = db.Column(db.Integer, db.ForeignKey('ReleaseSets.id'))
    card_id = db.Column(db.Integer, db.ForeignKey('Cards.id'))

    #relationships
    card_in_inventory = db.relationship("Inventory" , backref = "cardinSet") 


    #Validations
    #Serializer Rules

    serialize_rules = ('-card.card_in_set','-releaseSet.card_in_set')

    def __repr__(self):
        return f'{self.card_id} released in {self.set_id} with a rarity of {self.rarity}'



#TODOLater if Time permits

#Extra DowntheLine
    
class Banlist(db.Model, SerializerMixin):
    __tablename__ = 'Banlists'
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String)
    start_date = db.Column(db.String)
    end_date = db.Column(db.String)

    #foreignKey

    #relationships

    card_on_banlist = db.relationship('BanlistCard',backref='banlist') 

    #seralizer rules
    serialize_rules = ('-card_on_list.banlist',)
        

    def __repr__(self):
        return f'Banlist {self.name} from {self.start_date} to {self.end_date}'


class BanlistCard(db.Model, SerializerMixin):
    #join table between banlist and cards
    __tablename__ = 'BanlistCards'
    id = db.Column(db.Integer,primary_key = True)
    quantity = db.Column(db.Integer)

    #foreignKeys
    banlist_id = db.Column(db.Integer, db.ForeignKey('Banlists.id'))
    card_id = db.Column(db.Integer, db.ForeignKey('Cards.id'))

    #seralizer rules
    serialize_rules = ('-banlist.card_on_banlist','-card.card_on_banlist')

    def __repr__(self):
        return f'Card with id {self.card_id} is limited to {self.quantity} copies in banlist {self.banlist_id}'
    



# #General Rule for serializer rules that works for me 
# 1. If you have the foreign key kill the backref.relationshipname
# 2. If you have the relationship kill the relationship.backref