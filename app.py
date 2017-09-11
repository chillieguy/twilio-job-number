from flask import Flask, request, session, redirect
from twilio import twiml
from twilio.twiml.messaging_response import MessagingResponse
from twilio.twiml.voice_response import VoiceResponse
from twilio.rest import Client
from datetime import timedelta, datetime
import os
import json
from os import environ
import random

# The session object makes use of a secret key.
SECRET_KEY = 'thequickbrownfoxjumpedoverthelazydog'

# Get secrets from Heroku enviroment
ACCOUNT_SID = environ.get('ACCOUNT-SID')
AUTH_TOKEN = environ.get('AUTH-TOKEN')

# Create Twilio client
client = Client(ACCOUNT_SID, AUTH_TOKEN)

# Set up Flask app, set session time out to 60 seconds
app = Flask(__name__)
app.config.from_object(__name__)
app.permanent_session_lifetime = timedelta(seconds=60)

# Default route incase someone visits site root page
@app.route("/", methods=['GET', 'POST'])
def hello():
    '''Default to respond to visiting the page in a web browser '''
    return "This is not the page you are looking for."

# Route used by Twilio when a call is placed to Twilio phone number
@app.route("/voice", methods=['GET', 'POST'])
def voice():
    """Respond to incoming requests."""
    resp = VoiceResponse()
    resp.say("Hello.  Thank you for calling Chuck Underwood. It will be just a moment while you are connected.")
    resp.dial("+15416391136")

    return str(resp)

@app.route("/sms", methods=['GET', 'POST'])
def sms():
    """Respond with the number of text messages sent between two parties."""
    # Increment the counter
    counter = session.get('counter', 0)
    counter += 1

    # Save the new counter value in the session
    session['counter'] = counter

    message = "Hello World"

    sender = request.values.get('From', None)

    if counter == 1:
        # When receiving first sms of session send welcome message
        # Build our reply
        message = "You have reached Chuck Underwood \n\nRespond with your choice: \n1) Request call with Chuck \n2) Go to Chuck's resume \n3) Random Joke \n\nThank you for your interest"
    
    if counter > 1:
        # When counter is greater than one as for response
        if request.values.get('Body') == '1':
            # Helper function to send request to Chuck with sender phone number
            send_request(sender)
            message =  "Call request sent to Chuck for {}.\nChuck will call you back immediately if possible.  Otherwise he will call ASAP".format(sender)
        elif request.values.get('Body') == '2':
            message = "https://chillieguy.com/resume"
        elif request.values.get('Body') == '3':
            message = random_joke()
        else:
            message = "Invalid option.  Try again."
    
    # Put it in a TwiML response
    r = MessagingResponse()
    r.message(message)

    return str(r)

def send_request(sender):
    message_send = client.api.account.messages.create(to="+15416391136", from_="+15417145139", body="{} is requesting a call back.".format(sender))


def random_joke():
    '''Return random joke from array'''
    jokes = [
        "Why do trees seem suspicious on sunny days? \n\nDunno, they're just a bit shady.",
        "What did they give the guy who inventred the doorknocker? \n\nA no-bell prize.",
        "What do you call a fake noodle? \n\nAn impasta.",
        "What do you call a bear with no teeth? \n\nA gummy bear.",
        "I bought some shoes from a drug dealer. I don't know what he laced them with, but I've been tripping all day.",
        "Why did the cookie go to the hospital? \n\nBecause he felt crummy.",
        "Why did Johnny throw the clock out of the window? \n\nBecause he wanted to see time fly!",
        "Why was the baby strawberry crying? \n\nBecause his mom and dad were in a jam.",
        "What did one toilet say to the other toilet? \n\nYou look flushed.",
        "Why shouldn't you write with a broken pencil? \n\nBecause it's pointless.",
        "What do call cheese that isn't yours? \n\nNacho Cheese.",
        "How do you make a tissue dance? \n\nPut a little boogey in it!",
        "What do you get when you cross a snowman with a vampire? \n\nFrostbite.",
        "I went to the zoo the other day, there was only one dog in it, it was a shitzu...",
        "I used to think I was indecisive, but now I'm not too sure.",
        "It's funny, when I walk into a spider web I demolish his home and misplace his dinner yet I still feel like the victim.",
        "A computer once beat me at chess, but it was no match for me at kick boxing."
    ]

    return random.choice(jokes)

if __name__ == "__main__":
    #app.debug = True
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    