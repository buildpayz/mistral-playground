"""Quotation Playground Streamlit Application."""
import os
from typing import Optional

USER_PROMPT = ('Please analyze the document, determine the *ideal* project milestones '
              'using complex reasoning, and generate the table as instructed in the '
              'system prompt. Remember to include the Milestone, % of Project, Amount (AUD), '
              'Deliverable, Work Area(s), and Trade(s) columns, with the milestone '
              'information only appearing on the Milestone row, and not repeated on the '
              'Deliverable rows. Make sure all monetary values are in AUD and exclude '
              'GST. Strive to provide the most logical breakdown of the project based '
              'on your understanding of construction processes.')

import streamlit as st
from dotenv import load_dotenv

from utils.api_clients import MistralClient, GeminiClient, CONSTRUCTION_SYSTEM_PROMPT
from utils.file_handler import save_response
# Page configuration
st.set_page_config(
    page_title="Project Structure Playground",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .stTextArea > div > div > textarea {
        background-color: #f0f2f6;
    }
    .main .block-container {
        padding-top: 2rem;
    }
    .stAlert {
        margin-top: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_resource
def initialize_clients() -> tuple[MistralClient, GeminiClient]:
    """Initialize API clients with caching.
    
    Returns:
        Tuple of (MistralClient, GeminiClient)
    """
    load_dotenv('./.env')
    
    # Retrieve API keys from environment variables
    mistral_api_key = os.environ.get("MISTRAL_API_KEY", "")
    gemini_api_key = os.environ.get("GEMINI_API_KEY", "")
    
    if not mistral_api_key or not gemini_api_key:
        st.error("Missing API keys in environment variables.")
        st.stop()
    
    return MistralClient(mistral_api_key), GeminiClient(gemini_api_key)

def process_document(mistral_client: MistralClient, gemini_client: GeminiClient,
                    uploaded_file: Optional[st.runtime.uploaded_file_manager.UploadedFile] = None,
                    file_url: Optional[str] = None) -> None:
    """Process document and generate response.
    
    Args:
        mistral_client: Initialized Mistral client
        gemini_client: Initialized Gemini client
        uploaded_file: Uploaded file object
        file_url: URL to process
    """
    with st.spinner("Processing document..."):
        try:
            # Process document with OCR
            if uploaded_file:
                ocr_result = mistral_client.process_document(
                    file_content=uploaded_file.getvalue(),
                    file_name=uploaded_file.name
                )
            else:
                ocr_result = mistral_client.process_document(file_url=file_url)
            
            if ocr_result.error:
                st.error(f"OCR Error: {ocr_result.error}")
                return
            
            # Generate content with Gemini
            with st.spinner("Generating response..."):
                response_text = gemini_client.generate_content(
                    user_prompt=USER_PROMPT,
                    ocr_text=ocr_result.text,
                    system_prompt=CONSTRUCTION_SYSTEM_PROMPT
                )
                
                # Display response
                st.markdown("### Response:")
                st.markdown(response_text)
                
                # Save response
                success, error = save_response(response_text)
                if success:
                    st.success("Response saved to output.md")
                else:
                    st.error(f"Failed to save response: {error}")
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            import traceback
            with st.expander("View detailed error"):
                st.code(traceback.format_exc(), language="python")

def main():
    """Main application function."""
    st.title("📚 Project Structure Playground")
    
    # Initialize clients
    mistral_client, gemini_client = initialize_clients()
    
    # Create tabs for different sections
    input_tab, chat_tab, about_tab = st.tabs(["Input", "Chat", "About"])
    
    with input_tab:
        
        # File input methods
        col1, col2 = st.columns(2)
        
        with col1:
            uploaded_file = st.file_uploader(
                "Upload a PDF file",
                type=['pdf'],
                help="Upload a local PDF file for processing"
            )
        
        with col2:
            file_url = st.text_input(
                "Or enter PDF URL:",
                placeholder="Online pdf link",
                help="Provide a URL to a publicly accessible PDF"
            )
        
        # Process button
        if st.button("Get Response", type="primary", use_container_width=True):
            # Validate inputs
            if not uploaded_file and not file_url:
                st.error("Please either upload a file or provide a URL.")
                st.stop()
            
            process_document(
                mistral_client=mistral_client,
                gemini_client=gemini_client,
                uploaded_file=uploaded_file,
                file_url=file_url
            )
    
    with about_tab:
        st.markdown("""
        ### About Project Structure Playground
        
        This application allows you to extract and analyze text from PDF documents using:
        - **Mistral AI** for OCR processing
        - **Google Gemini** for content generation
        
        #### How to use:
        1. Upload a PDF file or provide a URL
        2. Click "Get Response" to process
        
        The generated response will be displayed and saved to `output.md`.
        """)

def init_chat():
    """Initialize chat messages in session state."""
    if "messages" not in st.session_state:
        st.session_state.messages = []

def display_chat():
    """Display chat interface."""
    init_chat()
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask a question about the document"):
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display assistant response
        with st.chat_message("assistant"):
            response = "Based on the document analysis, I'll help answer your question about the project structure. What specific details would you like to know?"
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

def main():
    """Main application function."""
    st.title("📚 Project Structure Playground")
    
    # Initialize clients
    mistral_client, gemini_client = initialize_clients()
    
    # Create tabs for different sections
    input_tab, chat_tab, about_tab = st.tabs(["Input", "Chat", "About"])
    
    with input_tab:
        # Input tab content (existing code)
        col1, col2 = st.columns(2)
        
        with col1:
            uploaded_file = st.file_uploader(
                "Upload a PDF file",
                type=['pdf'],
                help="Upload a local PDF file for processing"
            )
        
        with col2:
            file_url = st.text_input(
                "Or enter PDF URL:",
                placeholder="Online pdf link",
                help="Provide a URL to a publicly accessible PDF"
            )
        
        if st.button("Get Response", type="primary", use_container_width=True):
            if not uploaded_file and not file_url:
                st.error("Please either upload a file or provide a URL.")
                st.stop()
            
            process_document(
                mistral_client=mistral_client,
                gemini_client=gemini_client,
                uploaded_file=uploaded_file,
                file_url=file_url
            )
    
    with chat_tab:
        display_chat()
    
    with about_tab:
        st.markdown("""
        ### About Project Structure Playground
        
        This application allows you to extract and analyze text from PDF documents using:
        - **Mistral AI** for OCR processing
        - **Google Gemini** for content generation
        
        #### How to use:
        1. Upload a PDF file or provide a URL
        2. Click "Get Response" to process
        3. Use the Chat tab to ask questions about the document
        
        The generated response will be displayed and saved to `output.md`.
        """)

if __name__ == "__main__":
    main()
