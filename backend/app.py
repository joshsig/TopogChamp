from datetime import datetime

from flask import Flask, request, redirect, session, url_for, jsonify, Response, make_response


#from sqlalchemy import create_engine

#from database import db, User, Session, Log, Alert

import json
from flask_cors import CORS, cross_origin  # Import CORS extension

from getNetworkData import get_network_information

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

#API_AUDIENCE = "https://dev-htyfpjzs.us.auth0.com/api/v2/"

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost:5432/postgres_db'
app.config['CORS_HEADERS'] = 'Content-Type'

#db.app = app
#db.init_app(app)


@app.route('/home')
def hello_world():
    return 'Hello World!'

@app.route('/get_data_information', methods=['POST'])
def login():
    if request.method == 'POST':
        try:
            print(request.data)

            #username = request.json.get('username')
            #password = request.json.get('password')

            #if username is None or password is None:
            #    return "Missing username or password", 400

            #print(username, password)

            data = get_network_information()

            return {'data': data}, 200
        except Exception as e:
            print(f"Server error: {e}")
            return "Request Failed", 401



with app.app_context():
    pass
    #db.create_all()

    #users = User.query.all()
    #print(users)

app.run()

