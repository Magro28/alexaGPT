# alexaGPT

Just some snippets for an Alexa skill which connects to OpenAI GPT API
I implemented a simple memory function (stores the last 20 conversations) and should remember all things in one session.

## How to setup
Just go to developer.amazon.com -> Alexa and build a skill from scratch und use the python environment. 
Replace in the code section the lambda_function.py and requirement.txt.
ALso add your open ai API KEY from platform.openai.com in the code and change the prompt description to your likes.

Deploy the code and set it under "Test" to "development". It should now run on your Alexa device.

