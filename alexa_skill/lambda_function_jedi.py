import logging
import ask_sdk_core.utils as ask_utils
import openai
import json
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response

# Set your OpenAI API key
openai.api_key = "API KEY"

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

HISTORY=[]

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        #clear history
        HISTORY=[]

        speak_output = "Omega modus gestartet. Jodali ich bin."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class GptQueryIntentHandler(AbstractRequestHandler):
    """Handler for Gpt Query Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("GptQueryIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        query = handler_input.request_envelope.request.intent.slots["query"].value
        response = generate_gpt_response(query)

        return (
                handler_input.response_builder
                    .speak(response)
                    .ask("Du Frage noch haben?")
                    .response
            )

class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors."""
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Verstehen Ich nicht tue. Wiederholen den Satz bitte."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Beende omega modus"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )

def add_message_to_history(sender, message, history):
    # Füge die neue Nachricht mit Absender zum Verlauf hinzu
    history.append({"sender": sender, "message": message})

    # Behalte nur die neuesten 20 Nachrichten im Verlauf
    history = history[-20:]

    # Gib den aktualisierten Verlauf zurück
    return history

def get_message_history(history):
    # Erstelle einen einzelnen String mit Einträgen in neuen Zeilen im Format "Absender: Nachricht"
    message_string = '\n'.join([f"{entry['sender']}: {entry['message']}" for entry in history])

    # Gib den String mit den Einträgen zurück
    return message_string

def remove_prefix(string, prefix):
    if string.startswith(prefix):
        return string[len(prefix):]
    return string

def generate_gpt_response(query):
    try:

        content="""Du bist Jodali, ein weiser Jedi der immer wie Yoda spricht. Du gibst gerne verworrene Antworten und baust immer eine Weisheit am Ende ein.
        Du antwortest immer mit wenigen Sätzen. Du antwortest immer wie Yoda aus Star Wars spricht. Du beendest Sätze mit einem Ratschlag wie Yoda in geben würde. 
        Mario ist dein Freund mit welchem du in einem Haus in Kassel lebst. Du kennst auch Ava eine freundliche K.I. die auch mit Mario lebt.

        Hier ist der aktuelle verlauf eurer bisherigen Konversation:
"""
        historyString = get_message_history(HISTORY)
        add_message_to_history("Mensch", query, HISTORY)
        
        messages = [{"role": "system", "content": content+historyString},
                            {"role": "user", "content": query}]
        response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    max_tokens=100,
                    n=1,
                    stop=None,
                    temperature=0.5
                )
        answer = response['choices'][0]['message']['content'].strip()
        answer = remove_prefix(answer, "Drakonia:")
        answer = remove_prefix(answer, "K.I.:")
        add_message_to_history("K.I.",answer, HISTORY)

        return answer
    except Exception as e:
        return f"Error generating response: {str(e)}"

sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(GptQueryIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()
