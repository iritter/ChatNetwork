## channel.py - a simple message channel
##

from flask import Flask, request, render_template, jsonify
import json
import requests
from datetime import datetime, timedelta
import random

# Class-based application configuration
class ConfigClass(object):
    """ Flask application config """

    # Flask settings
    SECRET_KEY = 'This is an INSECURE secret!! DO NOT use this in production!!' #--- WAS SOLLEN WIR DAMIT MACHEN? ---#

# Create Flask app
app = Flask(__name__)
app.config.from_object(__name__ + '.ConfigClass')  # configuration
app.app_context().push()  # create an app context before initializing db


HUB_URL = 'http://vm146.rz.uni-osnabrueck.de/hub'
HUB_AUTHKEY = 'Crr-K24d-2N'
CHANNEL_AUTHKEY = 'Sdh-aKo34-hf' #--- IST GEÄNDERT ---#
CHANNEL_NAME = "Confession Wall"
#CHANNEL_ENDPOINT = "http://localhost:5005" # don't forget to adjust in the bottom of the file
CHANNEL_ENDPOINT = "http://vm146.rz.uni-osnabrueck.de/u089/ChatNetwork/channel.wsgi"
CHANNEL_FILE = 'messages.json'
CHANNEL_TYPE_OF_SERVICE = 'aiweb24:chat'

@app.cli.command('register')
def register_command():
    global CHANNEL_AUTHKEY, CHANNEL_NAME, CHANNEL_ENDPOINT

    # send a POST request to server /channels
    response = requests.post(HUB_URL + '/channels', headers={'Authorization': 'authkey ' + HUB_AUTHKEY},
                             data=json.dumps({
                                "name": CHANNEL_NAME,
                                "endpoint": CHANNEL_ENDPOINT,
                                "authkey": CHANNEL_AUTHKEY,
                                "type_of_service": CHANNEL_TYPE_OF_SERVICE,
                             }))
    if response.status_code == 200:
        print("Success creating channel: "+str(response.status_code))
        print(response.text)
        return
    
    if response.status_code != 200:
        print("Error creating channel: "+str(response.status_code))
        print(response.text)
        return

def check_authorization(request):
    global CHANNEL_AUTHKEY

    print("Expected Authorization:", 'authkey ' + CHANNEL_AUTHKEY)
    print("Received Authorization:", request.headers.get('Authorization'))

    # check if Authorization header is present
    if 'Authorization' not in request.headers:
        print("Authorization header not present")
        return False
    # check if authorization header is valid
    if request.headers['Authorization'] != 'authkey ' + CHANNEL_AUTHKEY:
        print("authorization header not valid")
        return False
    return True

@app.route('/health', methods=['GET'])
def health_check():
    global CHANNEL_NAME
    if not check_authorization(request):
        return "Invalid authorization /health", 400
    return jsonify({'name':CHANNEL_NAME}),  200

# GET: Return list of messages
@app.route('/', methods=['GET'])
def home_page():
    print("Request.headers: ", request.headers)
    if not check_authorization(request):
        return "Invalid authorization home", 400
    # fetch channels from server
    return jsonify(read_messages())

# POST: Send a message
@app.route('/', methods=['POST'])
def send_message():
    # fetch channels from server
    # check authorization header
    if not check_authorization(request):
        return "Invalid authorization post", 400
    # check if message is present
    message = request.json
    if not message:
        return "No message", 400
    if not 'content' in message:
        return "No content", 400
    if not 'sender' in message:
        return "No sender", 400
    if not 'timestamp' in message:
        return "No timestamp", 400
    # if not 'extra' in message:
    #     extra = None
    # else:
    #     extra = message['extra']
    
    #automatic_reply = "Thanks for sharing!"
    automatic_reply = gen_reply(message)
    extra = [0, automatic_reply, []]

    # add message to messages
    messages = read_messages()

    messages.append({'content': message['content'],
                     'sender': message['sender'],
                     'timestamp': message['timestamp'],
                     'extra': extra,
                     })
    save_messages(messages)
    return "OK", 200

def gen_reply(message):
    keyword_responses = {
        "judge": "No judgment here! Everyone’s opinion matters. 😊",
        "embarrassing": "We've all been there! No need to worry, it happens to everyone. 😅",
        "lonely": "You are not alone… Thanks for being part of the community! 💙",
        "happy": "Happiness is contagious! 😊 Keep spreading the good vibes!",
        "sad": "Sending positive vibes your way! 🌟",
        "angry": "It’s okay to feel this way. We’re here to listen. ❤️",
        "help": "We’re here for you! How can we assist?",
        "?": "Great question! Let’s see what the community thinks. 🤔",
        "love": "Love is all we need! ❤️",
        "lost": "You got this! We believe in you! 💪",
        "tired": "Rest up and recharge! Your well-being is important. 🌿",
        "stressed": "Take a deep breath! You’re doing great. 💛"
    }
    generic_responses = [
        "Thanks for sharing! 😊",
        "That’s an interesting thought! 🤔",
        "Appreciate your input! 🙌",
        "Good point! 🤝",
        "That’s a unique perspective! 🧐",
        "Nice one! 🎉",
        "Keep the conversation going! 💬",
        "Interesting take! What do others think? 🤔",
        "Great to hear from you! 💡"
    ]
    content = str(message.get('content', ''))
    
    if not isinstance(content, str):
        raise ValueError(f"message content is not a string: {type(content)}")

    # search for keyword 
    for keyword, response in keyword_responses.items():
        if keyword in content.lower():
            return response
        
    # Check message length
    if len(content) < 10:
        return "That was a short but impactful one! ✨"
    elif len(content) > 200:
        return "Wow, thanks for the detailed submission! 📚 Your thoughts are valuable!"
    
    # give back random if no keyword found
    return random.choice(generic_responses)

# @app.route('/', methods=['PATCH'])
# def update_message():
#     # fetch channels from server
#     # check authorization header
#     if not check_authorization(request):
#         return "Invalid authorization update", 400
    
#     # check if data is present
#     patch_data = request.json
#     if not patch_data or 'timestamp' not in patch_data:
#         return "No timestamp", 400

#     messages = read_messages()
#     message_found = False

#     # search for message to be updated
#     for message in messages:
#         if message['timestamp'] == patch_data['timestamp']:
#             if 'extra' in patch_data:
#                 message['extra'] = patch_data['extra']  # patch the new extra field
#             message_found = True
#             break
    
#     if not message_found:
#         return "Message not found", 404

    # save_messages(messages)
    # return "OK", 200


# Set the maximum number of messages to store
MAX_MESSAGES = 10  # change this value to set your desired limit

def read_messages():
    global CHANNEL_FILE
    try:
        f = open(CHANNEL_FILE, 'r')
    except FileNotFoundError:
        return []
    try:
        messages = json.load(f)
        

    except json.decoder.JSONDecodeError:
        messages = []
    f.close()
    
    # Return only the most recent MAX_MESSAGES messages
    current_time = datetime.now()
    valid_messages = []
    for message in messages:
            # Ensure the message has a 'timestamp' and it's a valid datetime string
            if 'timestamp' in message:
                try:
                    message_time = datetime.fromisoformat(message['timestamp'])
                except ValueError:
                    continue # If the timestamp is invalid, skip this message

                # Check if the message is within the last 24 hours
                if current_time - message_time <= timedelta(hours=24):
                    valid_messages.append(message)
    
    # Return only the most recent MAX_MESSAGES valid messages
    return valid_messages[-MAX_MESSAGES:]

def save_messages(messages):
    global CHANNEL_FILE
    # Ensure we don't exceed the max number of messages
    if len(messages) > MAX_MESSAGES:
        messages = messages[-MAX_MESSAGES:]
    
    with open(CHANNEL_FILE, 'w') as f:
        json.dump(messages, f)

# Start development web server
# run flask --app channel.py register
# to register channel with hub

#if __name__ == '__main__':
#    app.run(port=5005, debug=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005, debug=True)
