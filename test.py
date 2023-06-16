from twilio.rest import Client

# Your Account SID from twilio.com/console
account_sid = "AC013daab4089979e0cb840c4b4d118bf3"
# Your Auth Token from twilio.com/console
auth_token = "99734501e429696d8aef1cfaeaeb629e"

client = Client(account_sid, auth_token)

message = client.messages.create(
    to="+19132441797", from_="+18886441428", body="Hello from Python!"
)

print(message.sid)
