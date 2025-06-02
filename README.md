# ai-devcrew-back
AI Software Development Crew Agents - Backend

## Requirements

- Python 3.10+
- FastAPI
- CrewAI
- API key de OpenAI

## Instalation

```bash
git clone https://github.com/LaunchCG/ai-devcrew-back.git
cd ai-devcrew-back
python -m venv venv
venv\Scripts\activate # on Windows or on Linux source venv/bin/activate  # 
pip install -r requirements.txt
```

## Set .env file with all the environment variables needed
```bash
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4

LITELLM_API_KEY_OPENAI=sk-...
LITELLM_API_KEY_DEEPSEEK=sk-...
```

## Local Execution
```bash
venv\Scripts\activate # On Windows if you don't have activated the virtual environment yet or on Linux source venv/bin/activate
uvicorn main:app --reload
```
