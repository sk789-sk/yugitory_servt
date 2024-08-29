INSERT INTO Users (username) VALUES ('sk789')
INSERT INTO Users (username, password) VALUES ('sk2','t1')

INSert INTO Users (username,password,email,profile) VALUES ('DEFAULT','NONE', NULL, NULL);
INSERT INTO Users (username,password,email,profile) VALUES ('sk789','test','skm478@gmail.com','https://images.ygoprodeck.com/images/cards/60482781.jpg');


INSERT INTO Decks (name,user_id) VALUES ('Dark Magician',2);
INSERT INTO Decks (name,user_id) VALUES ('Blue Eyes',2);
INSERT INTO Decks (name,user_id) VALUES ('Red Eyes',1);

INSERT INTO Cards (name,description,attack,defense,level, isEffect, isTuner, isFlip, isSpirit, isUnion, isGemini, isPendulum,isRitual, isToon, isFusion, isSynchro, isXYZ, isLink, card_type, card_race,card_attribute) VALUES ('Dark Magician','The ultimate wizard in attack and defense',2500,2100,7,False, False,False,False,False,False,False,False,False,False,False,False,False, 'Monster','Spellcaster','Dark');

INSERT INTO Cards (name,description,attack,defense,level, isEffect, isTuner, isFlip, isSpirit, isUnion, isGemini, isPendulum,isRitual, isToon, isFusion, isSynchro, isXYZ, isLink, card_type, card_race,card_attribute) VALUES ('Blue Eyes White Dragon','The ultimate dragon in attack and defense',3000,2500,8,False, False,False,False,False,False,False,False,False,False,False,False,False, 'Monster','Dragon','Light');

INSERT INTO Cards (name,description,attack,defense,level, isEffect, isTuner, isFlip, isSpirit, isUnion, isGemini, isPendulum,isRitual, isToon, isFusion, isSynchro, isXYZ, isLink, card_type, card_race,card_attribute) VALUES ('Red Eyes Black Dragon','A ferociious dragon with a deadly attack',2400,2000,7,False, False,False,False,False,False,False,False,False,False,False,False,False, 'Monster','Dragon','Dark');

INSERT INTO Cards (name,description,attack,defense,level, isEffect, isTuner, isFlip, isSpirit, isUnion, isGemini, isPendulum,isRitual, isToon, isFusion, isSynchro, isXYZ, isLink, card_type, card_race,card_attribute, LegalDate, card_image) 

INSERT INTO Cards (name,description,attack,defense,level, isEffect, isTuner, isFlip, isSpirit, isUnion, isGemini, isPendulum,isRitual, isToon, isFusion, isSynchro, isXYZ, isLink, card_type, card_race,card_attribute, LegalDate, card_image) 

INSERT Into CardsinSets (card_code, rarity, set_id,card_id) VALUES ('LOB-EN070','ultra',1,3);
INSERT Into CardsinSets (card_code, rarity, set_id,card_id) VALUES ('LDB1-EN070','super',3,3);
INSERT Into CardsinSets (card_code, rarity, set_id,card_id) VALUES ('SDCC-EN070','common',6,3);

INSERT INTO ReleaseSets (name,releaseDate,card_count,set_code) VALUES('Legen of Blue Eyes','08-08-08',100,'LOB');



INSERT INTO CardsinDecks (deck_id,card_id,quantity) VALUES (3,2,1);
INSERT INTO CardsinDecks (deck_id,card_id,quantity) VALUES (3,1,2);
INSERT INTO CardsinDecks (deck_id,card_id,quantity) VALUES (3,3,3);

INSERT INTO CardsinDecks (deck_id,card_id,quantity) VALUES (1,3,1);
INSERT INTO CardsinDecks (deck_id,card_id,quantity) VALUES (1,1,3);
INSERT INTO CardsinDecks (deck_id,card_id,quantity) VALUES (1,2,3);


INSERT INTO CardsinDecks (deck_id,card_id,quantity) VALUES (2,3,1);
INSERT INTO CardsinDecks (deck_id,card_id,quantity) VALUES (2,2,3);
INSERT INTO CardsinDecks (deck_id,card_id,quantity) VALUES (2,1,3);


INSERT INTO Inventories (quantity,isFirstEd,user_id,cardinSet_id) VALUES (1,TRUE,2,1);
INSERT INTO Inventories (quantity,isFirstEd,user_id,cardinSet_id) VALUES (1,TRUE,2,2);
INSERT INTO Inventories (quantity,isFirstEd,user_id,cardinSet_id) VALUES (1,TRUE,2,3);
INSERT INTO Inventories (quantity,isFirstEd,user_id,cardinSet_id) VALUES (1,False,2,1);
INSERT INTO Inventories (quantity,isFirstEd,user_id,cardinSet_id) VALUES (1,False,2,2);

INSERT INTO Inventories (quantity,isFirstEd,user_id,cardinSet_id) VALUES(1,TrUE,1,1);

DELETE FROM Cards;
DELETE FROM Users;
DELETE FROM Inventories;
DELETe FRom CardsinDecks;
DELETE FROM Decks;
DELETE FROM CardsinSets;

DELETE FROM Inventories WHERE id=8;

UPDATE Decks SET isPublic = 1 Where id=3;


UPDATE Decks Set created_at = '2023-09-05 23:43:24' where id <4;

SELECT * FROM CardsinSets Where card_code='YS15-ENY09';
SELECT * From Cards Where name='DUCKER Mobile Cannon';

SELECT * From Cards Where id=12319;

SELECt * FROM ReleaseSets Where set_code = 'YS15';

SELECT * FROM CardsinSets WHEre card_code = 'TDGS-EN040';