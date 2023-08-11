import json
import os
import openai
from dotenv import load_dotenv, find_dotenv

from context_cache import make_context, get_context
from products import product_list_electronics
from template import template_electronics_shop

_ = load_dotenv(find_dotenv())

openai.api_key = os.getenv('OPENAI_API_KEY')


class ShopAssistant:
    """
    Shop assistant class. This class is responsible for running the chatbot in conversation mode.
    """
    delimiter = "####"

    def __init__(self, template=None, list_of_products=None, moderation=True):
        self.user_name = None
        self.context = None
        self.template = template
        self.list_of_products = list_of_products
        self.moderation = moderation
        self.products = None
        self.temp = 0
        self.model = "gpt-3.5-turbo"
        self.max_tokens = 500

    def main(self):
        """
        Main function of the class. Runs the chatbot in conversation mode.
        :return:
        """
        self.user_name = input("What is your name? ")
        while True:
            print('(type exit to quit)')
            question = input("Question: ")
            if question == "exit":
                print("Bye!")
                exit()
            answer = self.get_completion_from_messages(question)
            final_answer = self.get_only_final_answer(answer)
            make_context(self.user_name, question, final_answer)
            print(final_answer)

    def get_completion_from_messages(self, messages):
        """
        Gets the completion from the messages.
        :param messages: user message
        :return: full response from the model with context and hidden layer
        """
        moderation_flagged = self.get_moderation_pass(messages)
        message = self.get_message(messages)
        if self.moderation and not moderation_flagged:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=message,
                temperature=self.temp,  # this is the degree of randomness of the model's output
                max_tokens=self.max_tokens,  # the maximum number of tokens the model can output
            )
            return response.choices[0].message["content"]
        return {"error": "message failed moderation"}, 400

    def get_product_by_name(self, name):
        """
        Gets a product by name.
        :param name: product name
        :return: product object(dict)
        """
        return self.list_of_products.get(name, None)

    def get_products_by_category(self, category):
        """
        Gets all products by category.
        :param category: category
        :return: List[products]
        """
        return [product for product in self.list_of_products.values() if product["category"] == category]

    def get_only_final_answer(self, msg):
        """
        Gets the final answer from the message.
        :param msg: user message
        :return: only the final answer without hidden layer and context
        """
        try:
            final_response = msg.split(self.delimiter)[-1].strip()
        except Exception as e:
            final_response = "Sorry, I'm having trouble right now, please try asking another question."

        return final_response

    @staticmethod
    def get_moderation_pass(msg):
        """
        Checks if the message passes the moderation check from OpenAI.
        :param msg: user message
        :return: Boolean
        """
        return openai.Moderation.create(input=msg)["results"][0]['flagged']

    @staticmethod
    def read_string_to_list(input_string):
        """
        Reads a string and converts it to a list of dictionaries.
        :param input_string: string input
        :return: Dict[dictionary] or None
        """
        if input_string is None:
            return None

        try:
            if isinstance(input_string, dict):
                input_string = json.dumps(input_string)
            input_string = input_string.replace("'", "\"")  # Replace single quotes with double quotes for valid JSON
            data = json.loads(input_string)
            return data
        except json.JSONDecodeError:
            print("Error: Invalid JSON string")
            return None

    def generate_output_string(self, data_list):
        output_string = ""

        if data_list is None:
            return output_string

        for data in data_list:
            try:
                if "products" in data:
                    products_list = data["products"]
                    for product_name in products_list:
                        product = self.get_product_by_name(product_name)
                        if product:
                            output_string += json.dumps(product, indent=4) + "\n"
                        else:
                            print(f"Error: Product '{product_name}' not found")
                elif "category" in data:
                    category_name = data["category"]
                    category_products = self.get_products_by_category(category_name)
                    for product in category_products:
                        output_string += json.dumps(product, indent=4) + "\n"
                else:
                    print("Error: Invalid object format")
            except Exception as e:
                print(f"Error: {e}")

        return output_string

    def get_message(self, messages):
        """
        Makes a message for the AI to process (with visible and hidden layer of message).
        :param messages: user message
        :return: full formated message with system pre-prompt and possible context
        """
        msg = [
            {'role': 'system', 'content': self.template.format(
                self.delimiter, self.delimiter, self.list_of_products, self.delimiter, self.delimiter,
                self.delimiter, self.delimiter,
                self.delimiter, self.delimiter)
             },
            {'role': 'user', 'content': f"{self.delimiter}{messages}{self.delimiter}"}
        ]
        self.context = get_context(self.user_name)
        if self.context:
            msg.append({'role': 'assistant', 'content': self.context})
        return msg


# create shop assistant instance
assistant = ShopAssistant(
    list_of_products=product_list_electronics,
    template=template_electronics_shop,
)

# case scenario when we know that user is looking only for TV
# tv_filtered_product_list = assistant.generate_output_string(data_list=assistant.get_products_by_category("TV"))
# assistant.list_of_products = tv_filtered_product_list
# assistant.context = "I don't like Panasonic tvs."
# # print(user_context)
#
# user_message = 'Customer: Hello, I want to buy a new TV with big screen.'
# print(assistant.get_completion_from_messages(messages=user_message))

# run assistant in conversation mode with previous answers and questions cached as context
assistant.main()
