import re

def extract_first_json_block(text: str) -> str:
    """
    Extract the first valid JSON block from a string.
    """
    match = re.search(r'\{[\s\S]+?\}', text)
    if match:
        return match.group(0)
    raise ValueError("No valid JSON block found in agent response.")

def extract_json_from_markdown_response(text: str) -> str:
    """
    Extract the first valid JSON block from a string, removing markdown if needed.
    """
    text = text.replace("```", "")  # Eliminar formato Markdown si existe

    brace_count = 0
    start_idx = None
    for idx, char in enumerate(text):
        if char == '{':
            if start_idx is None:
                start_idx = idx
            brace_count += 1
        elif char == '}':
            brace_count -= 1
            if brace_count == 0 and start_idx is not None:
                return text[start_idx:idx + 1]

    raise ValueError("No valid JSON block found in agent response.")
