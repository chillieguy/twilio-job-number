from flask import Flask, request, session
from twilio.twiml.messaging_response import MessagingResponse
from datetime import timedelta
import os

# The session object makes use of a secret key.
SECRET_KEY = 'abc'
app = Flask(__name__)
app.config.from_object(__name__)
app.permanent_session_lifetime = timedelta(seconds=30)

@app.route("/sms", methods=['GET', 'POST'])
def hello():
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
    return "What’s brown and sticky? \n\n\n\nA stick."

if __name__ == "__main__":
    app.run(debug=True)


