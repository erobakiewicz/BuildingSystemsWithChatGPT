import os
import openai
import tiktoken
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())

openai.api_key = os.getenv('OPENAI_API_KEY')

delimiter = "-------------------"
system_message = f"""You will be provided with customer service messages and your job is to respond to them.
The messages will be provided in the following format:
{delimiter}
Customer: Hello, I have a problem with my order.
{delimiter}

Classify the message as one of the following categories billing, support, general inquiry:
1. Billing: unsubscribe, upgrade
2. Support: technical, bug, issue
3. Account Management: login, password change, deactivate account
4. General Inquiry: question, inquiry, other

Provide your response in the following format:
{delimiter}
Service: Hello, I am here to help you with your order.
{delimiter}
"""


def get_moderation_pass(msg):
    return openai.Moderation.create(input=msg)["results"][0]['flagged']


def get_completion_from_messages(messages,
                                 model="gpt-3.5-turbo",
                                 temperature=0,
                                 max_tokens=500):
    moderation_pass = get_moderation_pass(messages)
    if moderation_pass:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {'role': 'system', 'content': system_message},
                {'role': 'user', 'content': f"{delimiter}{messages}{delimiter}"}
            ],
            temperature=temperature,  # this is the degree of randomness of the model's output
            max_tokens=max_tokens,  # the maximum number of tokens the model can ouptut
        )
        return response.choices[0].message["content"]
    return {"error": "message failed moderation"}, 400


print(get_completion_from_messages("prompt"))