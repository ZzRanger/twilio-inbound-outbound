import os
from flask import Flask, request, Response, render_template
from twilio.rest import Client
from twilio.jwt.taskrouter.capabilities import WorkerCapabilityToken
from twilio.twiml.voice_response import VoiceResponse, Dial
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VoiceGrant
from dotenv import load_dotenv

load_dotenv()


app = Flask(__name__)


# Your Account Sid and Auth Token from twilio.com/user/account
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
workspace_sid = os.getenv("TWILIO_WORKSPACE_SID")
workflow_sid = os.getenv("TWILIO_WORKFLOW_SID")


client = Client(account_sid, auth_token)


@app.route("/assignment_callback", methods=["GET", "POST"])
def assignment_callback():
    """Respond to assignment callbacks with an acceptance and 200 response"""
    print("HIIII")
    ret = (
        '{"instruction": "dequeue", "from":"%s", "post_work_activity_sid":"WA79401126500f72d0ca54cae16ec41789"}'
        % (os.getenv("TWILIO_CALLER_ID"))
    )  # a verified phone number from your twilio account
    resp = Response(response=ret, status=200, mimetype="application/json")
    return resp


@app.route("/incoming_call", methods=["GET", "POST"])
def incoming_call():
    if request.form.get("To") != os.getenv("TWILIO_CALLER_ID"):
        resp = VoiceResponse()

        # Placing an outbound call from the Twilio client
        dial = Dial(caller_id=os.getenv("TWILIO_CALLER_ID"))
        # wrap the phone number or client name in the appropriate TwiML verb
        # by checking if the number given has only digits and format symbols

        dial.number(request.form["To"])

        resp.append(dial)

        return Response(str(resp), mimetype="text/xml")
    """Respond to incoming requests."""

    resp = VoiceResponse()
    with resp.gather(
        numDigits=1, action="/enqueue_call", method="POST", timeout=5
    ) as g:
        g.say("Para Español oprime el uno.", language="es")
        g.say("For English, please hold or press two.", language="en")

    return str(resp)


@app.route("/enqueue_call", methods=["GET", "POST"])
def enqueue_call():
    digit_pressed = request.args.get("Digits")
    if digit_pressed == "1":
        language = "es"
    else:
        language = "en"

    resp = VoiceResponse()
    with resp.enqueue(None, workflowSid=workflow_sid) as e:
        e.task('{"selected_language":"' + language + '"}')

    return str(resp)


@app.route("/agents", methods=["GET"])
def generate_view():
    # account_sid = os.getenv["TWILIO_ACCOUNT_SID"]
    application_sid = os.getenv("TWILIO_TWIML_APP_SID")
    api_key = os.getenv("API_KEY")
    api_secret = os.getenv("API_SECRET")

    worker_sid = request.args.get("WorkerSid")

    worker_capability = WorkerCapabilityToken(
        account_sid, auth_token, workspace_sid, worker_sid
    )
    worker_capability.allow_update_activities()
    worker_capability.allow_update_reservations()

    worker_token = worker_capability.to_jwt()

    # Create access token with credentials
    token = AccessToken(
        account_sid,
        api_key,
        api_secret,
        identity="cool_beans",
    )

    # Create a Voice grant and add to token
    voice_grant = VoiceGrant(
        outgoing_application_sid=application_sid,
        incoming_allow=True,
    )
    token.add_grant(voice_grant)

    # Return token info as JSON
    token = token.to_jwt()

    return render_template("agent.html", worker_token=worker_token, token=token)


if __name__ == "__main__":
    app.run(debug=True)
