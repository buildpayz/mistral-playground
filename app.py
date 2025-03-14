import os
from mistralai import Mistral
from dotenv import load_dotenv
import streamlit as st
from google import genai
from google.genai import types

load_dotenv('./.env')

# Retrieve the API key from environment variables
mistral_api_key = os.environ["MISTRAL_API_KEY"]
gemini_api_key = os.environ["GEMINI_API_KEY"]

# Specify model
# model = "mistral-large-latest"

# Initialize the Mistral client
mistral_client = Mistral(api_key=mistral_api_key)
gemini_client = genai.Client(api_key=gemini_api_key)


st.title("Quotation Playground")

system_prompt = st.text_area("System prompt:",placeholder="What this document is about?")
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

    ocr_response = mistral_client.ocr.process(
        model="mistral-ocr-latest",
        document={
            "type": "document_url",
            "document_url": file_path
        },
        include_image_base64=True
    )

    response = gemini_client.models.generate_content(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(
            system_instruction=system_prompt),
        contents=[f"{user_prompt}", f"{ocr_response}"],
    )


    
    st.write(f"""{response.candidates[0].content.parts[0].text[3:-3]}""")
    with open("output.md", "w") as file:
        file.write(response.candidates[0].content.parts[0].text[3:-3])
    st.success("Response written to output.md")
