import json
import codecs
from pathlib import Path

PROMPT_FILE_PATH = Path(__file__).resolve().parent.parent / "prompts" / "prompts.json"

def load_prompts() -> str:
    try:
        with open(PROMPT_FILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise RuntimeError(f"Error loading prompts': {str(e)}")

def get_prompt_byname(prompt_name: str) -> str:
    try:
        return load_prompts().get(prompt_name.upper(), "")
    except Exception as e:
        raise RuntimeError(f"Error loading prompt '{prompt_name}': {str(e)}")

def addorupdate_prompt_byname(prompt_name: str, prompt_value: str) -> str:
    try:
        prompts = load_prompts()
        prompts[prompt_name.upper()] = codecs.decode(prompt_value, 'unicode_escape').encode('latin1').decode('utf-8')
        with open(PROMPT_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(prompts, f, indent=2, ensure_ascii=False)

        return json.dumps(prompts, indent=2)
    except Exception as e:
        raise RuntimeError(f"Error adding or updating prompt '{prompt_name}': {str(e)}")
