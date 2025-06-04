import re

def extract_first_json_block(text: str) -> str:
    """
    Extract the first valid JSON block from a string.
    """
    match = re.search(r'\{[\s\S]+?\}', text)
    if match:
        return match.group(0)
    raise ValueError("No valid JSON block found in agent response.")
