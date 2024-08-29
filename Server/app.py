#!/usr/bin/env python3

# Standard library imports

# Remote library imports
# Local imports
from config import app

from routes.auth_routes import auth_bp
from routes.card_routes import cards_bp
from routes.set_routes import set_bp
from routes.user_routes import user_bp
from routes.inventory_routes import inventory_bp
from routes.deck_routes import deck_bp
from routes.cardindeck_routes import cardinDeck_bp
from routes.reconcile_routes import reconcile_bp

app.register_blueprint(auth_bp, url_prefix = '/auth')
app.register_blueprint(cards_bp, url_prefix = '/cards')
app.register_blueprint(set_bp, url_prefix = '/sets')
app.register_blueprint(user_bp, url_prefix='/user')
app.register_blueprint(inventory_bp, url_prefix='/inventory')
app.register_blueprint(deck_bp , url_prefix='/deck')
app.register_blueprint(cardinDeck_bp, url_prefix="/cardinDeck")
app.register_blueprint(reconcile_bp)

if __name__ == '__main__':

    app.run(port=5555, debug=True)


