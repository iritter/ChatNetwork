from flask import Flask, request, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
import json
import datetime
import requests
import os

# Initialize SQLAlchemy to handle database operations.
db = SQLAlchemy()

# Define the User data-model.
# NB: Make sure to add flask_user UserMixin as this adds additional fields and properties required by Flask-User
class Channel(db.Model):
    __tablename__ = 'channels'
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column('is_active', db.Boolean(), nullable=False, server_default='1')
    name = db.Column(db.String(100, collation='NOCASE'), nullable=False)
    endpoint = db.Column(db.String(100, collation='NOCASE'), nullable=False, unique=True)
    authkey = db.Column(db.String(100, collation='NOCASE'), nullable=False)
    type_of_service = db.Column(db.String(100, collation='NOCASE'), nullable=False)
    last_heartbeat = db.Column(db.DateTime(), nullable=True, server_default=None)

# Class-based application configuration
class ConfigClass(object):
    """ Flask application config """

    # SECRET_KEY is used to sign session cookies and other security-related data.
    # In production, this should be a strong, random value stored securely.
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "default_insecure_key_for_dev_only")

    # Flask-SQLAlchemy settings
    SQLALCHEMY_DATABASE_URI = 'sqlite:///chat_server.sqlite'  # File-based SQL database
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Avoids SQLAlchemy warning

# Create Flask app
app = Flask(__name__)
app.config.from_object(__name__ + '.ConfigClass')  # configuration
app.app_context().push()  # create an app context before initializing db
db.init_app(app)  # initialize database
db.create_all()  # create database if necessary

SERVER_AUTHKEY = 'Crr-K24d-2N'

# The Home page is accessible to anyone
@app.route('/')
def home_page():
    """
    Home page route for the hub.
    Renders the home.html template and passes the list of registered channels.
    """
    channels = Channel.query.all()
    return render_template("home.html")


def health_check(endpoint, authkey):
    """
    Checks the health of a channel by sending a GET request to its /health endpoint.
    
    The function:
      - Sends a GET request with the proper authorization header.
      - Verifies that the response status is 200 and the response JSON contains a "name" key.
      - Confirms that the channel's name in the response matches the one stored in the database.
      - If all checks pass, updates the channel's last_heartbeat and returns True.
      - Otherwise, returns False.
    """
    response = requests.get(endpoint+'/health',
                            headers={'Authorization': 'authkey '+authkey})
    if response.status_code != 200:
        return False
    if 'name' not in response.json():
        return False
    channel = Channel.query.filter_by(endpoint=endpoint).first()
    if not channel:
        print(f"Channel {endpoint} not found in database")
        return False
    expected_name = channel.name
    if response.json()['name'] != expected_name:
        return False

    channel.last_heartbeat = datetime.datetime.now()
    db.session.commit()  # save to database
    return True


@app.route('/channels', methods=['POST'])
def create_channel():
    """
    Endpoint for creating or updating a channel.
    
    Expects a JSON payload with keys:
      - name: the name of the channel.
      - endpoint: the URL where the channel is hosted.
      - authkey: the channel's authentication key.
      - type_of_service: a string describing the type of service.
    
    The function verifies the authorization header, validates the payload,
    checks for an existing channel (and updates it if found), or creates a new channel.
    It then performs a health check on the channel.
    """

    global SERVER_AUTHKEY

    record = json.loads(request.data)

    # check if authorization header is present
    if 'Authorization' not in request.headers:
        return "No authorization header", 400
    # check if authorization header is valid
    if request.headers['Authorization'] != 'authkey ' + SERVER_AUTHKEY:
        return "Invalid authorization header ({})".format(request.headers['Authorization']), 400
    if 'name' not in record:
        return "Record has no name", 400
    if 'endpoint' not in record:
        return "Record has no endpoint", 400
    if 'authkey' not in record:
        return "Record has no authkey", 400
    if 'type_of_service' not in record:
        return "Record has no type of service representation", 400

    
    # Check if a channel with the provided endpoint already exists.
    update_channel = Channel.query.filter_by(endpoint=record['endpoint']).first()
    print("update_channel: ", update_channel)
    if update_channel:  # Channel already exists, update it
        update_channel.name = record['name']
        update_channel.authkey = record['authkey']
        update_channel.type_of_service = record['type_of_service']
        update_channel.active = False
        db.session.commit()
        if not health_check(record['endpoint'], record['authkey']):
            return "Channel is not healthy", 400
        return jsonify(created=False,
                       id=update_channel.id), 200
    else:  
        # create a new channel record
        channel = Channel(name=record['name'],
                          endpoint=record['endpoint'],
                          authkey=record['authkey'],
                          type_of_service=record['type_of_service'],
                          last_heartbeat=datetime.datetime.now(),
                          active=True)
        db.session.add(channel)
        db.session.commit()
        if not health_check(record['endpoint'], record['authkey']):
            #If the channel fails the health check, remove it from the database.
            db.session.delete(channel)
            db.session.commit()
            return "Channel is not healthy", 400

        return jsonify(created=True, id=channel.id), 200


@app.route('/channels', methods=['GET'])
def get_channels():
    """
    Endpoint to retrieve a list of all registered channels.
    
    Returns a JSON response containing channel details such as name, endpoint,
    authkey, and type of service.
    """
    channels = Channel.query.all()
    return jsonify(channels=[{'name': c.name,
                              'endpoint': c.endpoint,
                              'authkey': c.authkey,
                              'type_of_service': c.type_of_service} for c in channels]), 200


# Start development web server
if __name__ == '__main__':
    app.run(port=5555, debug=True)
