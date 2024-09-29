import openai
import os
import chainlit as cl
from prompts import SYSTEM_PROMPT
from dotenv import load_dotenv
from langfuse.decorators import observe
from langfuse.openai import openai
import json
from question_functions import get_goals

 # Load environment variables
load_dotenv()

configurations = {
    "mistral_7B_instruct": {
        "endpoint_url": os.getenv("MISTRAL_7B_INSTRUCT_ENDPOINT"),
        "api_key": os.getenv("RUNPOD_API_KEY"),
        "model": "mistralai/Mistral-7B-Instruct-v0.2"
    },
    "mistral_7B": {
        "endpoint_url": os.getenv("MISTRAL_7B_ENDPOINT"),
        "api_key": os.getenv("RUNPOD_API_KEY"),
        "model": "mistralai/Mistral-7B-v0.1"
    },
    "openai_gpt-4": {
        "endpoint_url": os.getenv("OPENAI_ENDPOINT"),
        "api_key": os.getenv("OPENAI_API_KEY"),
        "model": "gpt-4"
    }
}

# Choose configuration
config_key = "openai_gpt-4"
# config_key = "mistral_7B_instruct"
#config_key = "mistral_7B"

# Get selected configuration
config = configurations[config_key]

# Initialize the OpenAI async client
client = openai.AsyncClient(api_key=config["api_key"], base_url=config["endpoint_url"])

gen_kwargs = {
    "model": config["model"],
    "temperature": 0.3,
    "max_tokens": 500
}

SYSTEM_PROMPT = SYSTEM_PROMPT

@observe
@cl.on_chat_start
def on_chat_start():    
    message_history = [{"role": "system", "content": SYSTEM_PROMPT}]
    cl.user_session.set("message_history", message_history)

@observe
async def generate_response(client, message_history, gen_kwargs):
    response_message = cl.Message(content="")
    await response_message.send()

    stream = await client.chat.completions.create(messages=message_history, stream=True, **gen_kwargs)
    async for part in stream:
        if token := part.choices[0].delta.content or "":
            await response_message.stream_token(token)
    
    await response_message.update()

    return response_message


@cl.on_message
@observe()
async def on_message(message: cl.Message):

    message_history = cl.user_session.get("message_history", [])
    message_history.append({"role": "user", "content": message.content})
    response_message = await generate_response(client, message_history, gen_kwargs)
    #print(response_message.content)
    try:
        response = json.loads(response_message.content)
        if response["function"] and response["function"] == "get_goals":
            fc_response = get_goals()
            message_history.append({"role": "system", "content": fc_response})
            response_message = await generate_response(client, message_history, gen_kwargs)
    except json.JSONDecodeError as e:
        print(e.msg)
   


    message_history.append({"role": "assistant", "content": response_message.content})
    cl.user_session.set("message_history", message_history)
    #await response_message.update()


if __name__ == "__main__":
    cl.main()
