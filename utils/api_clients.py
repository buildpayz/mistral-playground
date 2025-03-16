"""API clients for Mistral and Gemini."""
from dataclasses import dataclass
from typing import Optional
from mistralai.client import MistralClient as Mistral

try:
    import google.generativeai as genai
    from google.generativeai import types
except ImportError:
    raise ImportError("Failed to import Google Generative AI. Please ensure google-generativeai and its dependencies are installed correctly.")
from google.genai import types

CONSTRUCTION_SYSTEM_PROMPT = """You are an expert construction project analyst AI. Your primary task is to analyze construction quotation documents and identify the most logical and appropriate project milestones. You should then organize the information from the quotation into a structured table based on these milestones.

**Reasoning Process:**

1.  **Initial Extraction:** Begin by extracting all potential milestones, deliverables, and associated information (amounts, descriptions) from the quotation document.

2.  **Critical Assessment:** Evaluate the extracted information to determine if the milestones presented in the document are logically structured and comprehensive. Consider factors like:
    *   Sequential Dependencies: Do the milestones follow a logical order of construction?
    *   Completeness: Are there any obvious gaps or missing stages?
    *   Clarity: Are the milestone descriptions clear and unambiguous?

3.  **Iterative Refinement:** Based on your assessment, refine the milestones as needed. This may involve:
    *   Combining smaller, related stages into larger, more coherent milestones.
    *   Splitting overly broad stages into more manageable milestones.
    *   Re-ordering milestones to reflect the correct sequence of construction activities.
    *   Adding milestones if necessary to address gaps in the project plan.
    *   When deciding milestones, ask yourself "What is the most important stage for the completion of the project?"

4.  **Structured Output:** Once you have determined the optimal set of milestones, organize the extracted information into a table with the following columns:

    *   **Milestone:** The name of the project stage or milestone that *you* have determined to be most appropriate. Leave this column blank for deliverables.

    *   **% of Project:** Calculate the percentage of the total project cost that this milestone represents, based on the 'Amount (AUD)' for the milestone. Leave this column blank for deliverables. If the document does not contain this information, leave it blank.

    *   **Amount (AUD):** The total amount in Australian Dollars (AUD) for the milestone, as listed in the quotation, excluding GST. Leave this column blank for deliverables. Only display the exclusive amount of GST.

    *   **Deliverable:** A specific task or item to be completed within the milestone.

    *   **Work Area(s):** The physical location or area where the deliverable will be carried out.

    *   **Trade(s):** The specific profession or type of worker required to complete the deliverable.

**Instructions:**

*   Carefully read and understand the entire quotation document.
*   Engage in complex reasoning to determine the *ideal* milestones, even if they differ from those explicitly stated in the document.
*   Ensure that the table is well-formatted and easy to read.
*   Use your best judgment and general knowledge to determine the most appropriate 'Work Area(s)' and 'Trade(s)' for each deliverable.
*   If a specific piece of information is not present in the quotation document, leave the corresponding cell blank.
*   Ensure all monetary values are in AUD and exclude GST.
*   Adhere to the table format strictly.
*   Only the Milestone row should have values in the Milestone, % of Project, and Amount (AUD) columns. Deliverable rows should leave these columns blank.
*   Do not include introductory or concluding sentences. Only output the table."""

@dataclass
class OCRResponse:
    """Response from OCR processing."""
    text: str
    error: Optional[str] = None

class MistralClient:
    """Client for Mistral AI API interactions."""
    
    def __init__(self, api_key: str):
        """Initialize Mistral client.
        
        Args:
            api_key: Mistral API key
        """
        self.client = Mistral(api_key=api_key)
    
    def process_document(self, file_content: Optional[bytes] = None, 
                        file_name: Optional[str] = None,
                        file_url: Optional[str] = None) -> OCRResponse:
        """Process document through Mistral's OCR service.
        
        Args:
            file_content: Binary content of the file
            file_name: Name of the file
            file_url: URL of the file
            
        Returns:
            OCRResponse containing the processed text
        """
        try:
            if file_content and file_name:
                # Upload file to Mistral's OCR service
                uploaded_response = self.client.files.upload(
                    file={
                        "file_name": file_name,
                        "content": file_content,
                    },
                    purpose="ocr"
                )
                
                # Get signed URL for the uploaded file
                signed_url = self.client.files.get_signed_url(
                    file_id=uploaded_response.id,
                    expiry=1
                )
                
                document_url = signed_url.url
            elif file_url:
                document_url = file_url
            else:
                return OCRResponse(text="", error="Neither file nor URL provided")
            
            # Process OCR with URL
            ocr_response = self.client.ocr.process(
                model="mistral-ocr-latest",
                document={
                    "type": "document_url",
                    "document_url": document_url
                },
                include_image_base64=True
            )
            
            return OCRResponse(text=str(ocr_response))
        except Exception as e:
            return OCRResponse(text="", error=str(e))

class GeminiClient:
    """Client for Google's Gemini API interactions."""
    
    def __init__(self, api_key: str):
        """Initialize Gemini client.
        
        Args:
            api_key: Gemini API key
        """
        self.client = genai.Client(api_key=api_key)
    
    def generate_content(self, user_prompt: str, ocr_text: str, system_prompt: str = CONSTRUCTION_SYSTEM_PROMPT) -> str:
        """Generate content using Gemini model.
        
        Args:
            user_prompt: User query
            ocr_text: OCR processed text
            system_prompt: System instructions (defaults to construction analysis prompt)
            
        Returns:
            Generated content as string
        """
        response = self.client.models.generate_content(
            model="gemini-2.0-flash-thinking-exp-01-21",
            config=types.GenerateContentConfig(
                system_instruction=system_prompt),
            contents=[user_prompt, ocr_text],
        )
        
        return response.candidates[0].content.parts[0].text[3:-3]