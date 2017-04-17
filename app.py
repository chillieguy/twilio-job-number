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
import gspread
import time
from oauth2client.service_account import ServiceAccountCredentials

# The session object makes use of a secret key.
SECRET_KEY = 'thequickbrownfoxjumpedoverthelazydog'

# Get secrets from Heroku enviroment
ACCOUNT_SID = environ.get('ACCOUNT-SID')
AUTH_TOKEN = environ.get('AUTH-TOKEN')

# Create Twilio client
client = Client(ACCOUNT_SID, AUTH_TOKEN)

# Set up Flask app, set session time out to 30 seconds
app = Flask(__name__)
app.config.from_object(__name__)
app.permanent_session_lifetime = timedelta(seconds=30)

# use creds to create a client to interact with the Google Drive API
scope = ['https://spreadsheets.google.com/feeds']
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
gspread_client = gspread.authorize(creds)

# Find a workbook by name and open the first sheet
# Make sure you use the right name here.
sheet = gspread_client.open("twilio contacts").sheet1

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
    resp.say("Hello.  Thank you for calling the Chuck Underwood job line. Please wait while you are connected to Chuck.")
    resp.dial("+15416391136")

    sheet.insert_row([request.values.get('From', None) ,datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "Call"], index=1)
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

    if counter == 1:
        # When receiving first sms of session send welcome message
        # Build our reply
        message = "You have reached Chuck Underwood \n\nRespond with your choice: \n1) Call Chuck immediatley \n2) Go to Chuck's resume \n3) Random Joke \n\nThank you for your interest"
    
    if counter > 1:
        # When counter is greater than one as for response
        if request.values.get('Body') == '1':
            message =  "Calling"
            # Moved to seperate function
            call()
        elif request.values.get('Body') == '2':
            message = "https://chillieguy.com/resume"
        elif request.values.get('Body') == '3':
            message = random_joke()
        else:
            message = "Invalid option.  Try again."
    
    # Put it in a TwiML response
    r = MessagingResponse()
    r.message(message)

    sheet.insert_row([request.values.get('From', None), datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "SMS"], index=1)

    return str(r)

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

# Made a seperate function to keep code DRY
def call():
    """Helper function to make outbound call """
    call = client.api.account.calls.create(to="+15416391136",  # Any phone number
              from_="+15417145139", # Must be a valid Twilio number
              url="http://twimlets.com/holdmusic?Bucket=com.twilio.music.ambient")

if __name__ == "__main__":
    app.debug = True
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    


