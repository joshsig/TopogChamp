from flask import Flask, request
from flask_cors import CORS

from getNetworkData import get_network_information

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost:5432/postgres_db'
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route('/home')
def hello_world():
    return 'Hello World!'


@app.route('/get_data_information', methods=['POST'])
def login():
    if request.method == 'POST':
        try:
            print(request.data)

            data = get_network_information()

            return {'data': data}, 200
        except Exception as e:
            print(f"Server error: {e}")
            return "Request Failed", 401


with app.app_context():
    pass

app.run()

