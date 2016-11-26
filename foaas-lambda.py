"""
F-O-A-A-S Skill. 

"""
from __future__ import print_function

import json
import random
import urllib
import requests

# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': title,
            'content': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to the insult generator. " \
                    "Please tell me who to insult by saying: " \
                    "What do we say about Bob, or: Everyone should go home."
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Please tell me who to insult by saying: " \
                    "What do we say about Bob, or: Everyone should go home."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def get_help_response():
    session_attributes = {}
    card_title = "Help"
    speech_output = "Tell me who to insult by saying: " \
                    "What do we say about Bob, or: Everyone should go home."
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Tell me who to insult by saying: " \
                    "What do we say about Bob, or: Everyone should go home."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def get_stop_response():
    session_attributes = {}
    card_title = "Bye"
    speech_output = "Ok."
    reprompt_text = ""
    should_end_session = True
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Bye"
    speech_output = "Thank you for trying the insult generator. " \
                    "Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


# --------------- Code to communicate with foaas ------------------

def make_request(request):
  try:
    resp = requests.get(request, headers={ 'Accept': 'application/json' })
    if resp.status_code != 200:
      pass
    else:
      data = json.loads(resp.content)
      return data
  except: 
    print("Request failed:", sys.exc_info()[0])
  return None

def get_random_endpoint_for_person(to_text, endpoints, from_text="Your F-O-A-A-S Skill"):
    return "http://foaas.com/{}/{}/{}".format(random.choice(endpoints), urllib.quote(to_text), urllib.quote(from_text))

def get_random_endpoint(endpoints, from_text="Your F-O-A-A-S Skill"):
    return "http://foaas.com/{}/{}".format(random.choice(endpoints), urllib.quote(from_text))

def get_operations():
  name_endpoints = list()
  generic_endpoints = list()
  try:
    data = make_request("http://foaas.com/operations/")
    for entry in data:
      if len(entry['fields']) == 1:
        generic_endpoints.append(entry['name'])
      elif len(entry['fields']) == 2:
        name_endpoints.append(entry['name'])
  except: 
    print("Could not get operations:", sys.exc_info()[0])  
  return generic_endpoints, name_endpoints

def get_message(request, default_text):
  message = default_text
  try:
    message = make_request(request)['message']
  except:
    print("Get message failed", sys.exc_info()[0])
    pass
  return message

def get_insult(kw, default_text):
  op1, op2 = get_operations()
  speech_output = default_text
  try:
    if kw:
      speech_output = get_message(get_random_endpoint_for_person(kw, op2), speech_output)
    else:
      speech_output = get_message(get_random_endpoint(op1), speech_output)
  except:
    pass
  return speech_output

# --------------- End of foaas code ------------------


def communicate_with_foaas(intent, session):
    card_title = "What the Fuck"
    session_attributes = {}
    should_end_session = True
    speech_output = "I didn't understand a fucking work!"
    reprompt_text = ""
    if intent['name'] == "AboutPerson":
        kw = intent['slots']['KeyWord']['value']
        #session_attributes = create_favorite_color_attributes(favorite_color)
        speech_output = "What the fuck is wrong with you asking me about " + \
                        kw
        speech_output = get_insult(kw, speech_output)
    else:
        speech_output = get_insult(None, speech_output)

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    #print("on_intent requestId=" + intent_request['requestId'] +
    #      ", sessionId=" + session['sessionId'])

    
    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "AboutPerson":
        return communicate_with_foaas(intent, session)
    elif intent_name == "AboutEveryone":
        return communicate_with_foaas(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_help_response()
    elif (intent_name == "AMAZON.StopIntent") or (intent_name == "AMAZON.CancelIntent"):
        return get_stop_response()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])


