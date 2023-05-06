# alexaGPT

Just some snippets for an Alexa skill which connects to OpenAI GPT API
I implemented a simple memory function (stores the last 20 conversations) and should remember these. Just up the value if you like in the add_message_to_history function.

## How to setup
Just go to developer.amazon.com -> Alexa and build a skill from scratch and use the python environment. 
Replace in the code section the lambda_function.py and requirement.txt.
ALso add your open ai API KEY from platform.openai.com in the code and change the prompt description to your likes.

Deploy the code and set it under "Test" to "development". It should now run on your Alexa device.

