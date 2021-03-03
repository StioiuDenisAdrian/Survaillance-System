from twilio.rest import Client

def sendMessage():
    account_sid = 'sid from twillio'
    auth_token = 'token recieved from twillio'


    client = Client(account_sid, auth_token)
    message = client.messages.create(
        from_='+12059531848',
        body='The system started, watch the stream at ip:5000/',
        to='+phone number'
    )

    print(message.sid)
