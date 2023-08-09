import os
import openai
import tiktoken
from dotenv import load_dotenv, find_dotenv

from products import product_list_electronics
from template import template_electronic_shop

_ = load_dotenv(find_dotenv())

openai.api_key = os.getenv('OPENAI_API_KEY')


class ShopAssistant:
    delimiter = "####"

    def __init__(self, template=None, list_of_products=None):
        self.template = template
        self.list_of_products = list_of_products
        self.products = None
        self.temp = 0
        self.model = "gpt-3.5-turbo"
        self.max_tokens = 500

    def get_completion_from_messages(self, messages):
        moderation_flagged = self.get_moderation_pass(messages)
        if not moderation_flagged:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {'role': 'system', 'content': self.template.format(
                        self.delimiter, self.delimiter, self.list_of_products, self.delimiter, self.delimiter,
                        self.delimiter, self.delimiter,
                        self.delimiter)
                     },
                    {'role': 'user', 'content': f"{self.delimiter}{messages}{self.delimiter}"}
                ],
                temperature=self.temp,  # this is the degree of randomness of the model's output
                max_tokens=self.max_tokens,  # the maximum number of tokens the model can ouptut
            )
            return response.choices[0].message["content"]
        return {"error": "message failed moderation"}, 400

    def get_product_by_name(self, name):
        return self.list_of_products.get(name, None)

    def get_products_by_category(self, category):
        return [product for product in self.list_of_products.values() if product["category"] == category]

    def get_only_final_answer(self, msg):
        try:
            final_response = msg.split(self.delimiter)[-1].strip()
        except Exception as e:
            final_response = "Sorry, I'm having trouble right now, please try asking another question."

        return final_response

    @staticmethod
    def get_moderation_pass(msg):
        return openai.Moderation.create(input=msg)["results"][0]['flagged']


assistant = ShopAssistant(
    list_of_products=product_list_electronics,
    template=template_electronic_shop
)

message = "What is more expensive BlueWave laptop or Black Addler nanobook?"
print(assistant.get_completion_from_messages(messages=message))
