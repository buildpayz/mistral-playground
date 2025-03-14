import os
from mistralai import Mistral
from dotenv import load_dotenv  

load_dotenv('./.env')

# Retrieve the API key from environment variables
api_key = os.environ["MISTRAL_API_KEY"]

# Specify model
model = "mistral-small-latest"

# Initialize the Mistral client
client = Mistral(api_key=api_key)

system_prompt = input("system propmt: ")
user_prompt = input("User prompt: ")
file_path = input("File Path: ")
# Define the messages for the chat
messages = [
    {
        "role": "system",
        "content": [
            {
                "type": "text",
                "text": system_prompt
            },
            
        ]
    },
    {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": user_prompt
            },
            {
                "type": "document_url",
                "document_url": file_path
            }
        ]
    }
]

# Get the chat response
chat_response = client.chat.complete(
    model=model,
    messages=messages
)

# Print the content of the response
print(chat_response.choices[0].message.content)
