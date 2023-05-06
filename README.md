# alexaGPT

Just some snippets for an Alexa skill which connects to OpenAI GPT API

I implemented a simple memory function (stores the last 20 conversations) and should remember these until the lambda function restarts. Just up the value if you like in the add_message_to_history function.

## How to setup

Just go to developer.amazon.com -> Alexa and build a skill from scratch and use the python environment. Choose the right locale. 
#### Build section

##### Invocations
Set the invocation name 

##### Interaction Model
###### Json File
Change the intents and invocation name in the intents.json file and put the json file there. 

Build the model.

#### Code section
Replace in the code section the lambda_function.py and requirement.txt.

Also add your open ai API KEY from platform.openai.com in the code and change the prompt description to your likes.

Deploy the code.

#### Test section
In the "Test" tab set skill testing to "development". It should now run on your Alexa device.

## Limitations
The Alexa API limits long responses. So keep the max_token parameter low and instruct GPT to respond in short sentences. Longer responses can be continued by saying "continue" or "fortsetzen". 

Sometimes there are still some crashes which wipe out the memory. 

