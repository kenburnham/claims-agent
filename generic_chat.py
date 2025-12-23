
from google import genai
import os

def chat_sesh():
    client_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=client_key)
    chat = client.chats.create(model="gemini-2.5-flash-lite")

    user_query = input("Hi! I am Gemini. How can I help you today?\nYou: ")
    while user_query.lower() != "exit":
        response = chat.send_message(user_query)
        print(f"Gemini: {response.text}")
        user_query = input("You: ")



if __name__ == "__main__":
   chat_sesh()