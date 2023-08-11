from pymongo import MongoClient

client = MongoClient()
context_cache = client.chatbot.context_cache.users


def make_context(user_name, message, answer):
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
    context = context_cache.find_one({"user_name": user_name})
    if context:
        return format_context(context.get("messages"))


def format_context(context):
    return "\n".join([f"Question: {message.get('message')}\nAnswer: {message.get('answer')}" for message in context])
