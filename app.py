import os
from mistralai import Mistral
from dotenv import load_dotenv
import streamlit as st

load_dotenv('./.env')

# Retrieve the API key from environment variables
api_key = os.environ["MISTRAL_API_KEY"]

# Specify model
model = "mistral-small-latest"

# Initialize the Mistral client
client = Mistral(api_key=api_key)

st.title("Mistral Playground")

system_prompt = st.text_input("System prompt:",placeholder="What this document is about?")
user_prompt = st.text_area("User prompt:", placeholder="What you want to see from this document?.")
file_path = st.text_input("File Path:", placeholder="Online pdf link")

if st.button("Get Response"):
    if not system_prompt:
        st.error("Please provide a system prompt.")
        st.stop() 
    if not user_prompt:
        st.error("Please provide a user prompt.")
        st.stop()
    if not file_path:
        st.error("Please provide a file path.")
        st.stop()
    
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
    st.write(chat_response.choices[0].message.content)
