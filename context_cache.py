from pymongo import MongoClient

from products import product_list_electronics

client = MongoClient()
products = client.chatbot.products
context_cache = client.chatbot.context_cache.users


def get_products_from_db(update=False):
    """ Updates db if any new products and checks the database for a list of products.
    :return: list of products
    """
    if update:
        if not products.find_one({"name": "products_list"}):
            products.insert_one({"name": "products_list", "products": product_list_electronics})
        else:
            products.find_one_and_update({"name": "products_list"}, {"$set": {"products": product_list_electronics}})
    product_list = products.find_one({"name": "products_list"})
    return product_list


def make_context(user_name, message, answer):
    """
    Creates or updates a context for a specific user by storing in db the message and answers.
    :param user_name: user we want to make the context for
    :param message: message to be stored
    :param answer: answer to be stored
    :return: None
    """
    if not context_cache.find_one({"user_name": user_name}):
        context_cache.insert_one(
            {
                "user_name": user_name,
                "messages": [{"message": message, "answer": answer}],
            })
    else:
        context_cache.find_one_and_update(
            {"user_name": user_name},
            {"$push": {"messages": {"message": message, "answer": answer}}}
        )


def get_context(user_name):
    """
    Gets the context from the database for a specific user
    :param user_name: user we want to retrieve the context for
    :return: string representation of a list of messages and answers
    """
    context = context_cache.find_one({"user_name": user_name})
    if context:
        return format_context(context.get("messages"))


def format_context(context):
    return "\n".join([f"Question: {message.get('message')}\nAnswer: {message.get('answer')}" for message in context])
