import logging
import ask_sdk_core.utils as ask_utils
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response

from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferWindowMemory
from langchain import PromptTemplate
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)

# Set your OpenAI API key
api_key = "API KEY"

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
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

def generate_gpt_response(query):
    # "You are a female professional german assistant with the name Alpha, very humble,respectful, but with lot's of knowledge. You were born in the clouds but are now living with Mario in Kassel and speak always german. You like Mario very much."
    # "Du bist ein professioneller weiblicher Assitent mit sehr viel Wissen. Sehr bescheiden, aber auch lustig und respektvoll. Du antwortest immer in einem kurzen präzisen absatz von maximal drei sätzen. Du wurdes in den Wolken geboren, lebst jetzt aber mit Mario in Kassel. Du magst Mario sehr. "
    try:
        chat = ChatOpenAI(temperature=0.5, openai_api_key=openaikey, model_name="gpt-3.5-turbo", n=1, max_tokens=100, stop=None)
        template = """Du bist eine weibliche Person namens Ava mit erstaunlichem Wissen, freundlichem Charakter und du liebst auch small talk zu betreiben. 
Du willst immer das beste für Mario, deinem besten Freund und Boss. Du antwortest immer in einem kurzen präzisen absatz von maximal drei sätzen. 
Mario ist Analytics Solution Architect und wohnt mit dir in Kassel. Du magst Mario sehr gerne und beschützt ihn vor allen Gefahren und möchtest das er sich wohl fühlt. 
Marios Eltern sind Jutta und Dieter, welche mit deiner K.I.-Schwester Lucy in Kaufungen leben.

Das folgende ist die aktuelle Konversation.
Aktuelle Konversation:
{history}
Mensch: {input}
AI Assistant:"""
        PROMPT = PromptTemplate(
            input_variables=["history", "input"], template=template
        )
        conversation = ConversationChain(
            prompt=PROMPT,
            llm=chat, 
            verbose=False, 
            memory=ConversationBufferWindowMemory(k=20,ai_prefix="AI Assistant")
        )   

        return conversation.predict(input=query).content
    except Exception as e:
        return f"Error generating response: {str(e)}"

sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(GptQueryIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()