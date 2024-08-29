from sqlalchemy import text
from config import db


def deleteSet(set_name):
    #https://db.ygoprodeck.com/api/v7/cardinfo.php?cardset=Abyss%20Rising
    try:        
        result = db.session.execute(text('SELECT * FROM "ReleaseSets" WHERE name=:set_name'), {'set_name' : set_name})
        #print(f'Simple query result: {result.fetchone()}')

        if result:
            id = result.fetchone()[0]
            delete_query = 'DELETE FROM "CardsinSets" WHERE set_id=:set_id'
            
            db.session.execute(text('DELETE FROM "CardsinSets" WHERE set_id=:id'), {'id' : id})

            db.session.execute(text('DELETE FROM "ReleaseSets" WHERE id=:id'), {'id':id})
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f'{e}')