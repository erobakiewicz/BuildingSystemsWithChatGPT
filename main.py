import os
import openai
import tiktoken
from dotenv import load_dotenv, find_dotenv

from list_of_products import list_of_products

_ = load_dotenv(find_dotenv())

openai.api_key = os.getenv('OPENAI_API_KEY')

delimiter = "-------------------"
system_message = f"""You will be provided with customer service messages and your job is to respond to them.
The messages will be provided in the following format:
{delimiter}
Customer: Hello, I have a problem with my order.
{delimiter}

To answer perform following steps:
1. Classify the message as one of the following categories billing, support, general inquiry:
    1. Billing: unsubscribe, upgrade
    2. Support: technical, bug, issue
    3. Account Management: login, password change, deactivate account
    4. General Inquiry: question, inquiry, other
2. Check if the message is about a product from a list of products {list_of_products}. 
If not ask about product which might be related to the message.
3. If the message is about a product list all assumptions the user is making about the product in the message.
4. Check if those assumptions are correct.
RESPONSE TO USER: Formulate response for a user based on the message and the assumptions. 
Try to correct politely any incorrect assumptions.

Provide your response in the following format:
Use the following format:
Step 1:{delimiter} <step 1 reasoning>
Step 2:{delimiter} <step 2 reasoning>
Step 3:{delimiter} <step 3 reasoning>
Step 4:{delimiter} <step 4 reasoning>
Response to user:{delimiter} <response to user>
"""


def get_moderation_pass(msg):
    return openai.Moderation.create(input=msg)["results"][0]['flagged']


def get_only_final_answer(msg):
    try:
        final_response = msg.split(delimiter)[-1].strip()
    except Exception as e:
        final_response = "Sorry, I'm having trouble right now, please try asking another question."

    return final_response


def get_completion_from_messages(messages,
                                 model="gpt-3.5-turbo",
                                 temperature=0,
                                 max_tokens=500):
    moderation_flagged = get_moderation_pass(messages)
    if not moderation_flagged:
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


print(get_completion_from_messages("What is more expensive BlueWave laptop or BlackAddler nanobook?"))
