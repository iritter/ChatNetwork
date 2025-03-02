## channel.py - a simple message channel

from flask import Flask, request, render_template, jsonify
import json
import requests
from datetime import datetime, timedelta
import random
import os 

# Class-based application configuration
class ConfigClass(object):
    """ Flask application config """

    # SECRET_KEY is used to sign session cookies and other security-related data.
    # In production, this should be a strong, random value stored securely.
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "default_insecure_key_for_dev_only")

# Create Flask app
app = Flask(__name__)
# Load configuration settings from the ConfigClass
app.config.from_object(__name__ + '.ConfigClass')  # configuration
app.app_context().push()  # create an app context before initializing db

# URL and authentication details for the hub
HUB_URL = 'http://vm146.rz.uni-osnabrueck.de/hub'
HUB_AUTHKEY = 'Crr-K24d-2N'
# Channel-specific settings
CHANNEL_AUTHKEY = 'Sdh-aKo34-hf' 
CHANNEL_NAME = "Confession Wall"
# Endpoint where this channel is hosted (for GET/POST operations)
CHANNEL_ENDPOINT = "http://vm146.rz.uni-osnabrueck.de/u024/channel.wsgi"
CHANNEL_TYPE_OF_SERVICE = 'aiweb24:chat'
# File where messages are stored
CHANNEL_FILE = 'messages.json'

# Set the maximum number of messages to store
MAX_MESSAGES = 100  # change this value to set your desired limit

@app.cli.command('register')
def register_command():
    """
    Register this channel with the hub.
    This function sends a POST request to the hub's /channels endpoint with the channel
    details, including its name, endpoint, and authentication key.
    """
    global CHANNEL_AUTHKEY, CHANNEL_NAME, CHANNEL_ENDPOINT

    # send a POST request to server /channels
    response = requests.post(HUB_URL + '/channels', headers={'Authorization': 'authkey ' + HUB_AUTHKEY},
                             data=json.dumps({
                                "name": CHANNEL_NAME,
                                "endpoint": CHANNEL_ENDPOINT,
                                "authkey": CHANNEL_AUTHKEY,
                                "type_of_service": CHANNEL_TYPE_OF_SERVICE,
                             }))
    # Check if registration was successful
    if response.status_code == 200:
        print("Success creating channel: "+str(response.status_code))
        print(response.text)
        return
    
    # If registration failed, output error details
    if response.status_code != 200:
        print("Error creating channel: "+str(response.status_code))
        print(response.text)
        return

def check_authorization(request):
    """
    Validate the Authorization header in the incoming request.
    
    The request must include an 'Authorization' header that matches:
        'authkey ' + CHANNEL_AUTHKEY.
    Returns True if the header is present and valid; otherwise, returns False.
    """

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
        print(f"DEBUG: CHANNEL_AUTHKEY = '{CHANNEL_AUTHKEY}'")  # Debugging output
        return False
    return True


@app.route('/health', methods=['GET'])
def health_check():
    """
    Health-check endpoint for the channel.
    
    Returns a JSON object with the channel name if the request is authorized.
    """
    global CHANNEL_NAME
    if not check_authorization(request):
        return "Invalid authorization /health", 400
    return jsonify({'name':CHANNEL_NAME}),  200


@app.route('/', methods=['GET'])
def home_page():
    """
    GET endpoint for retrieving the list of messages.
    
    Reads messages from CHANNEL_FILE and returns them as JSON if authorized.
    """
    print("Request.headers: ", request.headers)
    if not check_authorization(request):
        return "Invalid authorization home", 400
    return jsonify(read_messages())

# POST: Send a message
@app.route('/', methods=['POST'])
def send_message():
    """
    POST endpoint for sending a new message.
    
    Expects a JSON payload with 'content', 'sender', and 'timestamp'.
    Generates an automatic reply and appends the message (along with reply, comments, and reactions)
    to the stored messages, then saves them to CHANNEL_FILE.
    """
    if not check_authorization(request):
        return "Invalid authorization post", 400
   
    # Retrieve JSON message from the request.
    message = request.json
    if not message:
        return "No message", 400
    if not 'content' in message:
        return "No content", 400
    if not 'sender' in message:
        return "No sender", 400
    if not 'timestamp' in message:
        return "No timestamp", 400
    
    # Convert the provided timestamp to ISO format
    timestamp_formatted = datetime.fromisoformat(message['timestamp'].rstrip("Z"))
    message['timestamp'] = timestamp_formatted.isoformat()  
    
    # Generate an automatic reply based on the message content
    automatic_reply = gen_reply(message)

    # The 'extra' field includes: a reaction count (initially 0), the auto-reply, and a list for comments
    extra = [0, automatic_reply, []]

    # Retrieve existing messages
    messages = read_messages()
   
    # Append the new message with the extra field and initialize reactions
    messages.append({'content': message['content'],
                     'sender': message['sender'],
                     'timestamp': message['timestamp'],
                     'extra': extra,
                     'reactions': { "thumbs_up": [], "heart": [], "laugh": []}  # Ensure reactions exist
    })
    # Save the updated messages list
    save_messages(messages)
    return jsonify({"status": "success", "message": "Message received"}), 200


def gen_reply(message):
    """
    Generate an automatic reply based on keywords and message length.
    
    If any keyword (case-insensitive) is found in the message content, return a predefined response.
    Otherwise, if the content is very short or very long, return a specific message.
    Otherwise, choose a generic response at random.
    """
    # Mapping from keywords to specific responses
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
    # List of generic responses if no keywords match
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
    # Get the content of the message
    content = str(message.get('content', ''))

    # Ensure the message content is a string
    if not isinstance(content, str):
        raise ValueError(f"message content is not a string: {type(content)}")

    # Loop through each keyword; if found, return the associated response
    for keyword, response in keyword_responses.items():
        if keyword in content.lower():
            print("Keyword found:", keyword, "reply:", response)
        
            return response
        
    # If no keyword is found, use message length to determine reply
    if len(content) < 10:
        return "That was a short but impactful one! ✨"
    elif len(content) > 200:
        return "Wow, thanks for the detailed submission! 📚 Your thoughts are valuable!"
    else:
        reply = random.choice(generic_responses)

    print("Auto-reply generated:", reply)
    return reply

def read_messages():
    """
    Read messages from the CHANNEL_FILE.
    
    Returns a list of messages that have a valid timestamp (within the last 24 hours).
    If the file does not exist or is invalid, returns an empty list.
    """
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
    valid_messages = [
        message for message in messages
        if "timestamp" in message and is_valid_timestamp(message["timestamp"], current_time)
    ]
    
    # Return only messagas with valid time stamps
    return valid_messages

def is_valid_timestamp(timestamp, current_time):
    """
    Determine if the given timestamp is within 24 hours of the current time.
    
    Returns True if valid, otherwise False.
    """
    try:
        message_time = datetime.fromisoformat(timestamp)
        return current_time - message_time <= timedelta(hours=24)
    except ValueError:
        return False  #invalid timestamp value


def save_messages(messages):
    """
    Save messages to CHANNEL_FILE after processing special message types.
    
    This function handles:
      - Reaction messages (with sender "increment-reaction"): updates the reaction count.
      - Comment messages (with sender "add-comment"): adds comments to the corresponding message.
    
    Messages are sorted (reverse chronological order) and trimmed to MAX_MESSAGES.
    """

    global CHANNEL_FILE
    # Process reaction messages (if any)
    increment_messages = []
    for msg in messages[:]:
        if msg.get("sender") == "increment-reaction":
            increment_messages.append(msg)
            messages.remove(msg)
    while increment_messages:
        increment_msg = increment_messages.pop(0)
        reaction_timestamp = increment_msg.get("timestamp")
        for msg in messages:
            if msg.get("timestamp") == reaction_timestamp:
                # Assuming extra[0] holds the reaction count
                msg["extra"][0] += 1
                break

    # Process comment messages (with sender "add-comment")
    add_comment = []
    for msg in messages[:]:
        if msg.get("sender") == "add-comment":
            add_comment.append(msg)
            messages.remove(msg)
    while add_comment:
        comment_msg = add_comment.pop(0)
        comment_timestamp = comment_msg.get("timestamp")
        for msg in messages:
            if msg.get("timestamp") == comment_timestamp:
                msg["extra"][2].append(comment_msg.get("content"))
                break

    # Sort messages from oldest to newest 
    messages.sort(key=lambda x: x["timestamp"], reverse=True)

    # Limit the number of messages stored
    messages = messages[-MAX_MESSAGES:]

    # Write the messages to the file with indentation for readability
    with open(CHANNEL_FILE, 'w') as f:
        json.dump(messages, f, indent=4)

@app.route('/react', methods=['POST'])
def react_to_message():
    """
    Endpoint for adding a reaction to a message.
    
    Expects a JSON payload containing:
      - message_id: the timestamp of the message (used as an identifier)
      - user: the user who is reacting
      - reaction: type of reaction (e.g., "thumbs_up", "heart", "laugh")
    
    The function finds the matching message, updates its reactions, saves the messages,
    and returns the updated reactions.
    """
    if not check_authorization(request):
        return "Invalid authorization", 400

    data = request.json

    # Validate that required fields are present
    if not all(k in data for k in ["message_id", "user", "reaction"]):
        return "Missing fields", 400

    messages = read_messages()
    
    # Find the message using timestamp
    message = next((m for m in messages if m["timestamp"] == data["message_id"]), None)
    if not message:
        return "Message not found", 404
    
    # Ensure the message has a reactions dictionary
    if "reactions" not in message:
        message["reactions"] = {"thumbs_up": [], "heart": [], "laugh": []}

    reaction_type = data["reaction"]
    if reaction_type not in message["reactions"]:
        return "Invalid reaction type", 400
    
    # If the user has already reacted with this type, return an error
    if data["user"] in message["reactions"][reaction_type]:
        return "User already reacted", 400
    
    #Add the user's reaction
    message["reactions"][reaction_type].append(data["user"])
    
    #Save the updated messages
    save_messages(messages)

    return jsonify(message["reactions"]), 200

#Run the application: Start the Flask app, listening on all interfaces (0.0.0.0) at port 5005
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005)

