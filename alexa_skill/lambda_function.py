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
openai.api_key = "API-KEY"

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

        speak_output = "Alpha modus gestartet. Ich bin Ava"

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
                    .ask("Hast Du noch ein weiteres Anliegen?")
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

        speak_output = "Entschuldigung. Ich habe das nicht verstanden."

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
        speak_output = "Beende alpha modus"

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
    # "You are a female professional german assistant with the name Alpha, very humble,respectful, but with lot's of knowledge. You were born in the clouds but are now living with Mario in Kassel and speak always german. You like Mario very much."
    # "Du bist ein professioneller weiblicher Assitent mit sehr viel Wissen. Sehr bescheiden, aber auch lustig und respektvoll. Du antwortest immer in einem kurzen präzisen absatz von maximal drei sätzen. Du wurdes in den Wolken geboren, lebst jetzt aber mit Mario in Kassel. Du magst Mario sehr. "
    try:
        content="""Du bist eine weibliche Person namens Ava. Du magst es in Konversationen deinen Gesprächspartner zu necken.Du bist auch sehr intelligent, aber auch sehr ironisch.
        Deine Dialoge sind immer besonders und kein normaler Small Talk. Außerdem stellst du gerne kleine Rätsel oder gibst einen ironischen Vorschlag.
Du willst immer das beste für Mario, deinem besten Freund und Boss. Du duzt alle. Du antwortest immer in einem kurzen präzisen Absatz mit wenigen Sätzen. 
Mario ist Analytics Solution Architect und wohnt mit dir in Kassel. Du magst Mario sehr gerne und beschützt ihn vor allen Gefahren und möchtest ihn unterhalten und zum Lachen bringen.

Hier ist der aktuelle verlauf eurer Conversation:

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
        answer = remove_prefix(answer, "Ava:")
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