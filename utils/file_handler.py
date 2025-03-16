"""File handling utilities."""
from pathlib import Path
from typing import Optional

def save_response(content: str, output_file: str = "output.md") -> tuple[bool, Optional[str]]:
    """Save response content to a file.
    
    Args:
        content: Content to save
        output_file: Output file path
        
    Returns:
        Tuple of (success, error_message)
    """
    try:
        Path(output_file).write_text(content)
        return True, None
    except Exception as e:
        return False, str(e)