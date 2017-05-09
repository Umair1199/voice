import os, re
# For Get Request Data and Generate JSON Response
from flask import Flask, request, jsonify
# For Generate AccessToken and Grant Permission
from twilio.jwt.access_token import (
    AccessToken,
    SyncGrant,
    VoiceGrant
)
# For Twilio Client
from twilio.rest import Client
# For Generate TwiML
import twilio.twiml
# Create JSON Data
import json
from datetime import datetime

from dotenv import load_dotenv, find_dotenv
from os.path import join, dirname

# Live Details
ACCOUNT_SID             = ''
API_KEY                 = ''
API_KEY_SECRET          = ''
PUSH_CREDENTIAL_SID     = ''
APP_SID                 = ''
AUTH_TOKEN              = ''
SYNC_SERVICE_SID        = ''
#

CALLER_ID_0 = ''
CALLER_ID_1 = ''
CALLER_ID_2 = ''
CALLER_ID_3 = ''
CALLER_ID_4 = ''
CALLER_ID_5 = ''
CALLER_ID_6 = ''
CALLER_ID_7 = ''
CALLER_ID_8 = ''

IDENTITY_0 = ''
IDENTITY_1 = ''
IDENTITY_2 = ''
IDENTITY_3 = ''
IDENTITY_4 = ''
IDENTITY_5 = ''
IDENTITY_6 = ''
IDENTITY_7 = ''
IDENTITY_8 = ''

app = Flask(__name__)
#phone_pattern = re.compile(r"^[\d\+\-\(\) ]+$")
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

@app.route('/generateToken')
def generateToken():
#    account_sid = os.environ.get("ACCOUNT_SID", ACCOUNT_SID)
#    api_key = os.environ.get("API_KEY", API_KEY)
#    api_key_secret = os.environ.get("API_KEY_SECRET", API_KEY_SECRET)
#    push_credential_sid = os.environ.get("PUSH_CREDENTIAL_SID", PUSH_CREDENTIAL_SID)
#    app_sid = os.environ.get("APP_SID", APP_SID)
#    sync_service_sid = os.environ.get("SYNC_SERVICE_SID", SYNC_SERVICE_SID)
#    auth_token = os.environ.get("AUTH_TOKEN", AUTH_TOKEN)
    account_sid         = os.environ['TWILIO_ACCOUNT_SID']
    api_key             = os.environ['TWILIO_API_KEY']
    api_key_secret      = os.environ['TWILIO_API_KEY_SECRET']
    push_credential_sid = os.environ['TWILIO_PUSH_CREDENTIAL_SID']
    app_sid             = os.environ['TWILIO_TWIML_APP_SID']
    sync_service_sid    = os.environ['TWILIO_SYNC_SERVICE_SID']
    auth_token          = os.environ['TWILIO_AUTH_TOKEN']
    
    identity = request.values.get('id')
    
    if identity[0] == ' ':
        identity = "+" + identity[1:]
    
    identity = getIdentity(identity)
    print(identity)

    token = AccessToken(account_sid, api_key, api_key_secret, identity=identity)

    # Create a Voice grant and add to token
    grant = VoiceGrant(
        push_credential_sid=push_credential_sid,
        outgoing_application_sid=app_sid
    )
    token.add_grant(grant)

    # Create a Sync grant and add to token
    if sync_service_sid:
        sync_grant = SyncGrant(service_sid=sync_service_sid)
        token.add_grant(sync_grant)

#    client = Client(account_sid, auth_token)
#    data = json.dumps({'board':{
#                      'date_updated': str(datetime.now()),
#                      'status': "none",
#                      }})
#    documents = client.preview \
#                        .sync \
#                            .services(sync_service_sid) \
#                                .documents \
#                                    .list()
#    isMatch = False
#    for document in documents:
#        print(document.unique_name)
#        print(document.data)
#        did_delete = client.preview \
#                            .sync \
#                                .services(sync_service_sid) \
#                                    .documents(document.unique_name) \
#                                        .delete()
#        print("Delete: ",did_delete)
#        if document.unique_name == identity:
#            isMatch = True
#            print("Fetch")
#            document = client.preview.sync.services(sync_service_sid).documents(identity).fetch()
#            print(document.unique_name)#
#    if not isMatch:
#        print ("Create")
#        document = client.preview.sync.services(sync_service_sid).documents.create(unique_name=identity, data=data)
#        print(document.unique_name)
#    else:
#        print("Already created.")

    return jsonify(identity=identity, token=token.to_jwt())
#    return str(token)


@app.route('/call', methods=['GET', 'POST'])
def call():
    """ This method routes calls from/to client                  """
    """ Rules: 1. From can be either client:name or PSTN number  """
    """        2. To value specifies target. When call is coming """
    """           from PSTN, To value is ignored and call is     """
    """           routed to client named CLIENT                  """

    resp = twilio.twiml.Response()
#    print(request.values.get('From'))
#    print(request.values.get('To'))
    from_value = request.values.get('From')
    to_value = request.values.get('To')
    
#    if from_value[0] == ' ':
#        from_value = "+" + from_value[1:]
#    if to_value[0] == ' ':
#        to_value = "+" + to_value[1:]

    if not (from_value and to_value):
        resp.say("Invalid request")
        return str(resp)

    "From Value"
    from_client = getIdentity(from_value)

    "To Value"
    to_client = getIdentity(to_value)

#    if phone_pattern.match(from_value):
    if not checkIdentity(from_value):
        print("PSTN -> client")
#        resp.dial(callerId=from_value).client(to_client)
        resp.dial(callerId=from_value).client(to_client, statusCallback=request.url_root + 'callbackStatus', statusCallbackEvent= 'initiated ringing answered completed', statusCallbackMethod= 'POST')
        print(from_value, "-", to_client)

#    elif phone_pattern.match(to):
    elif not checkIdentity(to_value):
        print("client -> PSTN")
#        resp.dial(to_value, callerId=from_value)
#        resp.dial(callerId=from_value).number(to_value)
        resp.dial(callerId='client:'+from_client).number(to_value, statusCallback=request.url_root + 'callbackStatus', statusCallbackEvent= 'initiated ringing answered completed', statusCallbackMethod= 'POST') #Display Client name in Twilio
#        resp.dial(callerId=from_value).number(to_client, statusCallback=request.url_root + 'voice', statusCallbackEvent= 'initiated ringing answered completed', statusCallbackMethod= 'POST') #Display Client number in Twilio
        print(from_value, "-", to_value)

    else:
        print("client -> client")
#        resp.dial(callerId=from_value).client(to_client)
        resp.dial(callerId='client:'+from_client).client(to_client, statusCallback=request.url_root + 'callbackStatus', statusCallbackEvent= 'initiated ringing answered completed', statusCallbackMethod= 'POST') #Display Client name in Twilio
#        resp.dial(callerId=from_value).client(to_client, statusCallback=request.url_root + 'voice', statusCallbackEvent= 'initiated ringing answered completed', statusCallbackMethod= 'POST') #Display Client number in Twilio
        print(from_value, "-", to_client)

    return str(resp)

@app.route('/callbackStatus', methods=['GET', 'POST'])
def callbackStatus():
    callSid = request.values.get('CallSid')
    From = request.values.get('From')
    sequenceNumber = request.values.get('SequenceNumber')
    parentCallSid = request.values.get('ParentCallSid')
    caller = request.values.get('Caller')
    apiVersion = request.values.get('ApiVersion')
    To = request.values.get('To')
    callbackSource = request.values.get('CallbackSource')
    timestamp = request.values.get('Timestamp')
    accountSid = request.values.get('AccountSid')
    callStatus = request.values.get('CallStatus')
    called = request.values.get('Called')
#    print("CallSid ->", request.values.get('CallSid'))
#    print("From ->", request.values.get('From'))
#    print("SequenceNumber ->", request.values.get('SequenceNumber'))
#    print("ParentCallSid ->", request.values.get('ParentCallSid'))
#    print("Caller ->", request.values.get('Caller'))
#    print("ApiVersion ->", request.values.get('ApiVersion'))
#    print("To ->", request.values.get('To'))
#    print("CallbackSource ->", request.values.get('CallbackSource'))
#    print("Timestamp ->", request.values.get('Timestamp'))
#    print("AccountSid ->", request.values.get('AccountSid'))
#    print("CallStatus ->", request.values.get('CallStatus'))
#    print("Called ->", request.values.get('Called'))

    account_sid         = os.environ['TWILIO_ACCOUNT_SID']
    auth_token          = os.environ['TWILIO_AUTH_TOKEN']
    sync_service_sid    = os.environ['TWILIO_SYNC_SERVICE_SID']
    client = Client(account_sid, auth_token)

    from_value = request.values.get('From')
    if checkIdentity(from_value):
        identity = getIdentity(from_value)
        new_data = json.dumps({'board':{
                              'date_updated': str(datetime.now()),
                              'status': callStatus,
                              }})
        print(new_data)
        print(identity)
        document = client.preview.sync.services(sync_service_sid).documents(identity).update(data=new_data)

    return jsonify(callSid=callSid,
                   From=From,
                   sequenceNumber=sequenceNumber,
                   parentCallSid=parentCallSid,
                   caller=caller,
                   apiVersion=apiVersion,
                   To=To,
                   callbackSource=callbackSource,
                   timestamp=timestamp,
                   accountSid=accountSid,
                   callStatus=callStatus,
                   called=called)
    #

def getIdentity(client_id):
#    client_id = request.values.get('id')
#    client_id = client_id.replace("+", "")
#    client_id = client_id.replace(" ", "")

    client_id = re.sub('[^A-Za-z0-9+]', '', client_id) # http://stackoverflow.com/questions/5843518/remove-all-special-characters-punctuation-and-spaces-from-string
    
    if client_id == os.environ['CALLER_ID_0']:  # re.match(client_id, CALLER_ID_1): For regex
        client_id = os.environ['IDENTITY_0']
    
    elif client_id == os.environ['CALLER_ID_1']:
        client_id = os.environ['IDENTITY_1']
    
    elif client_id == os.environ['CALLER_ID_2']:
        client_id = os.environ['IDENTITY_2']
    
    elif client_id == os.environ['CALLER_ID_3']:
        client_id = os.environ['IDENTITY_3']
    
    elif client_id == os.environ['CALLER_ID_4']:
        client_id == os.environ['IDENTITY_4']
    
    elif client_id == os.environ['CALLER_ID_5']:
        client_id = os.environ['IDENTITY_5']
    
    elif client_id == os.environ['CALLER_ID_6']:
        client_id = os.environ['IDENTITY_6']
    
    elif client_id == os.environ['CALLER_ID_7']:
        client_id = os.environ['IDENTITY_7']
    
    elif client_id == os.environ['CALLER_ID_8']:
        client_id = os.environ['IDENTITY_8']
    
    return str(client_id)

def checkIdentity(client_id):
    isMatch = False
    
    client_id = re.sub('[^A-Za-z0-9+]', '', client_id) # http://stackoverflow.com/questions/5843518/remove-all-special-characters-punctuation-and-spaces-from-string
    
    if client_id == os.environ['CALLER_ID_0']:
        isMatch = True
    
    elif client_id == os.environ['CALLER_ID_1']:
        isMatch = True
    
    elif client_id == os.environ['CALLER_ID_2']:
        isMatch = True
    
    elif client_id == os.environ['CALLER_ID_3']:
        isMatch = True
    
    elif client_id == os.environ['CALLER_ID_4']:
        isMatch = True
    
    elif client_id == os.environ['CALLER_ID_5']:
        isMatch = True
    
    elif client_id == os.environ['CALLER_ID_6']:
        isMatch = True
    
    elif client_id == os.environ['CALLER_ID_7']:
        isMatch = True
    
    elif client_id == os.environ['CALLER_ID_8']:
        isMatch = True
    
    return isMatch



#-------------------------# Old Methods #-------------------------#
@app.route('/accessToken')
def token():
  account_sid = os.environ.get("ACCOUNT_SID", ACCOUNT_SID)
  api_key = os.environ.get("API_KEY", API_KEY)
  api_key_secret = os.environ.get("API_KEY_SECRET", API_KEY_SECRET)
  push_credential_sid = os.environ.get("PUSH_CREDENTIAL_SID", PUSH_CREDENTIAL_SID)
  app_sid = os.environ.get("APP_SID", APP_SID)

  grant = VoiceGrant(
    push_credential_sid=push_credential_sid,
    outgoing_application_sid=app_sid
  )

  token = AccessToken(account_sid, api_key, api_key_secret, IDENTITY)
  token.add_grant(grant)

  return str(token)

@app.route('/outgoing', methods=['GET', 'POST'])
def outgoing():
  resp = twilio.twiml.Response()
  resp.say("Congratulations! You have made your first oubound call! Good bye.")
  return str(resp)

@app.route('/incoming', methods=['GET', 'POST'])
def incoming():
  resp = twilio.twiml.Response()
  resp.say("Congratulations! You have received your first inbound call! Good bye.")
  return str(resp)

@app.route('/placeCall', methods=['GET', 'POST'])
def placeCall():
  account_sid = os.environ.get("ACCOUNT_SID", ACCOUNT_SID)
  api_key = os.environ.get("API_KEY", API_KEY)
  api_key_secret = os.environ.get("API_KEY_SECRET", API_KEY_SECRET)

  client = Client(api_key, api_key_secret, account_sid)
  call = client.calls.create(url=request.url_root + 'incoming', to='client:' + IDENTITY, from_='client:' + CALLER_ID)
  return str(call.sid)

@app.route('/', methods=['GET', 'POST'])
def welcome():
  resp = twilio.twiml.Response()
  resp.say("Welcome to Twilio iOS Client...")
  return str(resp)

if __name__ == "__main__":
  port = int(os.environ.get("PORT", 5000))
  app.run(host='0.0.0.0', port=port, debug=True)
