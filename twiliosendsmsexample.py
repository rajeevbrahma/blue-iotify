from twilio.rest import TwilioRestClient

account_sid = "AC161d5213dce9632db6d2b6febdad21eb" # Your Account SID from www.twilio.com/console
auth_token  = "9ee4b0327f1e3d09b7a8928bb602ac9b"  # Your Auth Token from www.twilio.com/console

client = TwilioRestClient(account_sid, auth_token)

message = client.messages.create(body="Hello from Python",
    to="+919738300498",    # Replace with your phone number
    from_="+12512724152") # Replace with your Twilio number
print message
print(message.sid)