import json
import os
import secrets
import requests
from flask_login import LoginManager
from flask_jwt_extended import JWTManager
from trello import TrelloClient
from database import db
from utils.paypal import createProduct
from utils.razorpay import createRPProduct


def createApp(app):
    config = json.load(open("secret/config.json"))

    app.config["SECRET_KEY"] = handleSecretKey()
    app.config['PORT'] = config['port']
    app.config['HOST'] = config['host']
    app.config['DEBUG'] = config['debug']

    app.config["JWT_SECRET_KEY"] = handleSecretKey()
    app.config["JWT_TOKEN_LOCATION"] = ["cookies"]

    app.config["SQLALCHEMY_DATABASE_URI"] = config['db-uri']
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.config["TRELLO_ID"] = config['trello-id']
    app.config["TRELLO_KEY"] = config['trello-key']
    app.config["TRELLO_SECRET"] = config['trello-secret']
    app.config["TRELLO_TOKEN"] = config['trello-token']
    #app.config['TRELLO_BG_ID'] = createCustomBoard(app)

    app.config['PAYPAL_ID'] = config['paypal-id']
    app.config['PAYPAL_SECRET'] = config['paypal-secret']

    app.config['RAZORPAY_ID'] = config['razorpay-id']
    app.config['RAZORPAY_SECRET'] = config['razorpay-secret']

    trelloClient = TrelloClient(
        api_key=app.config["TRELLO_KEY"],
        api_secret=app.config["TRELLO_SECRET"],
        token=app.config["TRELLO_TOKEN"]
    )
    loginManager = LoginManager()
    jwt = JWTManager()

    app.config["trelloClient"] = trelloClient

    loginManager.init_app(app)
    app.config["loginManager"] = loginManager
    jwt.init_app(app)
    app.config["jwt"] = jwt
    db.init_app(app)
    app.config["database"] = db

    return app


def createDatabase(app):
    with app.app_context():
        if os.path.exists('database.txt'):
            pass
        else:
            createTables(app.config['database'])
            product = createProduct(app)
            app.config['database'].session.add(product)
            app.config['database'].session.commit()
            product = createRPProduct(app)
            app.config['database'].session.add(product)
            app.config['database'].session.commit()
            file = open('database.txt', 'w')
            file.write("Database Created")
            file.close()


def handleSecretKey():
    keys = json.load(open("secret/config.json"))
    if keys['secret-key']:
        return keys['secret-key']
    else:
        key = secrets.token_hex(16)
        keys['secret-key'] = key
        json.dump(keys, open("secret/config.json", 'w'), indent=4)
        return key


def createTables(database):
    database.create_all()
    database.session.commit()


def createCustomBoard(app):
    with open('static/trello.jpeg', 'rb') as f:
        data = f.read()
    url = "https://api.trello.com/1/members/" + app.config['TRELLO_ID'] + "/customBoardBackgrounds"
    headers = {
        "Accept": "application/json"
    }
    query = {
        'file': data,
        'key': app.config['TRELLO_KEY'],
        'token': app.config['TRELLO_TOKEN']
    }
    response = requests.post(
        url,
        headers=headers,
        params=query
    )
    return response

