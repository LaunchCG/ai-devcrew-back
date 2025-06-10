import json
from pathlib import Path

PROMPT_FILE_PATH = Path(__file__).resolve().parent.parent / "prompts" / "prompts.json"

def get_prompt(prompt_name: str) -> str:
    try:
        with open(PROMPT_FILE_PATH, "r", encoding="utf-8") as f:
            prompts = json.load(f)
        return prompts.get(prompt_name, "")
    except Exception as e:
        raise RuntimeError(f"Error loading prompt '{prompt_name}': {str(e)}")
