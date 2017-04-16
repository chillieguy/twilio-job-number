from flask import Flask, request, session
from twilio.twiml.messaging_response import MessagingResponse
from datetime import timedelta
import os
import random

# The session object makes use of a secret key.
SECRET_KEY = 'abc'
app = Flask(__name__)
app.config.from_object(__name__)
app.permanent_session_lifetime = timedelta(seconds=30)

@app.route("/", methods=['GET', 'POST'])
def hello():
    return "This is not the page you are looking for."

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
        
        # Build our reply
        message = "You have reached Chuck Underwood \n\nRespond with your choice: \n1) Call Chuck immediatley \n2) Go to Chuck's resume \n3) Random Joke \n\nThank you for your interest"
    
    if counter > 1:
        if request.values.get('Body') == '1':
            message = "You picked option 1"
        elif request.values.get('Body') == '2':
            message = "https://chillieguy.com/resume"
        elif request.values.get('Body') == '3':
            message = random_joke()
        else:
            message = "Invalid option.  Try again."
    
    # Put it in a TwiML response
    resp = MessagingResponse()
    resp.message(message)

    return str(resp)

def random_joke():
    jokes = [
        "Why do trees seem suspicious on sunny days? \n\nDunno, they're just a bit shady.",
        "What did they give the guy who inventred the doorknocker? \n\nA no-bell prize.",
        "What do you call a fake noodle? \n\nAn impasta.",
        "What do you call a bear with no teeth? \n\nA gummy bear.",
        "I bought some shoes from a drug dealer. I don't know what he laced them with, but I've been tripping all day."
    ]


    return random.choice(jokes)

if __name__ == "__main__":
    app.debug = True
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    


